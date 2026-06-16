package cn.org.alan.exam.controller;

import cn.org.alan.exam.common.result.Result;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.servlet.http.HttpServletResponse;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * 数据库备份与恢复控制器
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Api(tags = "数据库备份恢复接口")
@RestController
@RequestMapping("/api/backup")
public class BackupController {

    @Value("${spring.datasource.url}")
    private String datasourceUrl;

    @Value("${spring.datasource.username}")
    private String username;

    @Value("${spring.datasource.password}")
    private String password;

    private final String backupDir = System.getProperty("user.dir") + File.separator + "backups";

    @PostMapping
    @ApiOperation("一键备份数据库")
    @PreAuthorize("hasAuthority('role_admin')")
    public Result<String> backup() {
        File dir = new File(backupDir);
        if (!dir.exists()) {
            dir.mkdirs();
        }

        String fileName = "db_backup_" + new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date()) + ".sql";
        File backupFile = new File(dir, fileName);

        // 解析 JDBC URL 获取 host, port 和 dbName
        String host = "127.0.0.1";
        String port = "3306";
        String dbName = "db_exam";
        try {
            String cleanUrl = datasourceUrl.substring(13); // 去掉 jdbc:mysql://
            String hostPortAndDb = cleanUrl.split("\\?")[0];
            String[] parts = hostPortAndDb.split("/");
            dbName = parts[1];
            String hostPort = parts[0];
            if (hostPort.contains(":")) {
                String[] hp = hostPort.split(":");
                host = hp[0];
                port = hp[1];
            } else {
                host = hostPort;
            }
        } catch (Exception e) {
            // 解析失败使用默认值
        }

        try {
            // 构建 mysqldump 命令 (使用数组参数防注入并适应跨平台)
            String[] cmd = {
                    "mysqldump",
                    "-h" + host,
                    "-P" + port,
                    "-u" + username,
                    "-p" + password,
                    dbName
            };

            Process process = Runtime.getRuntime().exec(cmd);
            
            try (InputStream is = process.getInputStream();
                 FileOutputStream fos = new FileOutputStream(backupFile)) {
                byte[] buffer = new byte[4096];
                int len;
                while ((len = is.read(buffer)) != -1) {
                    fos.write(buffer, 0, len);
                }
            }

            int exitCode = process.waitFor();
            if (exitCode == 0) {
                return Result.success("备份成功，文件名：" + fileName);
            } else {
                // 如果备份文件大小为0或命令出错，删除空文件并报错
                if (backupFile.exists() && backupFile.length() == 0) {
                    backupFile.delete();
                }
                return Result.failed("备份失败，错误码：" + exitCode + "。请确认系统已安装 mysqldump 且其配置在 PATH 中。");
            }
        } catch (Exception e) {
            if (backupFile.exists()) {
                backupFile.delete();
            }
            return Result.failed("备份异常：" + e.getMessage());
        }
    }

    @GetMapping("/list")
    @ApiOperation("获取备份文件列表")
    @PreAuthorize("hasAuthority('role_admin')")
    public Result<List<Map<String, Object>>> getBackupList() {
        File dir = new File(backupDir);
        List<Map<String, Object>> list = new ArrayList<>();
        if (dir.exists() && dir.isDirectory()) {
            File[] files = dir.listFiles((d, name) -> name.endsWith(".sql"));
            if (files != null) {
                for (File file : files) {
                    Map<String, Object> map = new HashMap<>();
                    map.put("fileName", file.getName());
                    map.put("fileSize", file.length());
                    map.put("backupTime", new Date(file.lastModified()));
                    list.add(map);
                }
            }
        }
        // 按时间倒序排序
        list.sort((o1, o2) -> ((Date) o2.get("backupTime")).compareTo((Date) o1.get("backupTime")));
        return Result.success("查询成功", list);
    }

    @PostMapping("/restore")
    @ApiOperation("一键恢复数据库")
    @PreAuthorize("hasAuthority('role_admin')")
    public Result<String> restore(@RequestParam("fileName") String fileName) {
        File backupFile = new File(backupDir, fileName);
        if (!backupFile.exists()) {
            return Result.failed("备份文件不存在！");
        }

        // 解析 JDBC URL
        String host = "127.0.0.1";
        String port = "3306";
        String dbName = "db_exam";
        try {
            String cleanUrl = datasourceUrl.substring(13);
            String hostPortAndDb = cleanUrl.split("\\?")[0];
            String[] parts = hostPortAndDb.split("/");
            dbName = parts[1];
            String hostPort = parts[0];
            if (hostPort.contains(":")) {
                String[] hp = hostPort.split(":");
                host = hp[0];
                port = hp[1];
            } else {
                host = hostPort;
            }
        } catch (Exception e) {
        }

        try {
            String[] cmd = {
                    "mysql",
                    "-h" + host,
                    "-P" + port,
                    "-u" + username,
                    "-p" + password,
                    dbName
            };

            Process process = Runtime.getRuntime().exec(cmd);
            try (OutputStream os = process.getOutputStream();
                 FileInputStream fis = new FileInputStream(backupFile)) {
                byte[] buffer = new byte[4096];
                int len;
                while ((len = fis.read(buffer)) != -1) {
                    os.write(buffer, 0, len);
                }
                os.flush();
            }

            int exitCode = process.waitFor();
            if (exitCode == 0) {
                return Result.success("还原成功");
            } else {
                return Result.failed("还原失败，命令行退出码：" + exitCode);
            }
        } catch (Exception e) {
            return Result.failed("还原异常：" + e.getMessage());
        }
    }

    @GetMapping("/download/{fileName:.+}")
    @ApiOperation("下载备份文件")
    @PreAuthorize("hasAuthority('role_admin')")
    public void downloadBackup(@PathVariable("fileName") String fileName, HttpServletResponse response) {
        File file = new File(backupDir, fileName);
        if (!file.exists()) {
            response.setStatus(404);
            return;
        }
        response.setContentType("application/octet-stream");
        response.setHeader("Content-Disposition", "attachment; filename=" + fileName);
        try (FileInputStream fis = new FileInputStream(file);
             OutputStream os = response.getOutputStream()) {
            byte[] buffer = new byte[4096];
            int len;
            while ((len = fis.read(buffer)) != -1) {
                os.write(buffer, 0, len);
            }
        } catch (IOException e) {
            response.setStatus(500);
        }
    }

    @DeleteMapping("/{fileName:.+}")
    @ApiOperation("删除备份文件")
    @PreAuthorize("hasAuthority('role_admin')")
    public Result<String> deleteBackup(@PathVariable("fileName") String fileName) {
        File file = new File(backupDir, fileName);
        if (file.exists()) {
            if (file.delete()) {
                return Result.success("删除备份成功");
            }
        }
        return Result.failed("删除备份失败或文件不存在");
    }
}
