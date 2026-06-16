package cn.org.alan.exam.controller;

import cn.org.alan.exam.common.result.Result;
import cn.org.alan.exam.utils.SecurityUtil;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.sql.CallableStatement;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Types;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 存储过程和视图调用控制器
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Api(tags = "数据库存储过程与视图接口")
@RestController
@RequestMapping("/api/db-objects")
public class ProcedureController {

    @Resource
    private JdbcTemplate jdbcTemplate;

    @GetMapping("/course-stats/{courseId}")
    @ApiOperation("调用存储过程：查询指定课程的题型与章节题目统计")
    @PreAuthorize("hasAnyAuthority('role_teacher','role_admin')")
    public Result<Map<String, Object>> getCourseStats(@PathVariable("courseId") Integer courseId) {
        try {
            Map<String, Object> result = jdbcTemplate.execute((Connection conn) -> {
                CallableStatement stmt = conn.prepareCall("{call proc_get_course_question_stats(?)}");
                stmt.setInt(1, courseId);
                boolean hasResults = stmt.execute();
                
                List<Map<String, Object>> typeStats = new ArrayList<>();
                List<Map<String, Object>> chapterStats = new ArrayList<>();
                
                if (hasResults) {
                    // 第一个结果集：题型统计
                    try (ResultSet rs1 = stmt.getResultSet()) {
                        while (rs1.next()) {
                            Map<String, Object> row = new HashMap<>();
                            row.put("typeName", rs1.getString("type_name"));
                            row.put("questionCount", rs1.getInt("question_count"));
                            typeStats.add(row);
                        }
                    }
                    
                    // 第二个结果集：章节统计
                    if (stmt.getMoreResults()) {
                        try (ResultSet rs2 = stmt.getResultSet()) {
                            while (rs2.next()) {
                                Map<String, Object> row = new HashMap<>();
                                row.put("chapterName", rs2.getString("chapter_name"));
                                row.put("questionCount", rs2.getInt("question_count"));
                                chapterStats.add(row);
                            }
                        }
                    }
                }
                
                Map<String, Object> stats = new HashMap<>();
                stats.put("typeStats", typeStats);
                stats.put("chapterStats", chapterStats);
                return stats;
            });
            return Result.success("调用成功", result);
        } catch (Exception e) {
            return Result.failed("调用存储过程失败: " + e.getMessage());
        }
    }

    @GetMapping("/all-courses-stats")
    @ApiOperation("调用存储过程：查询各门课程、各种题型的习题数量")
    @PreAuthorize("hasAnyAuthority('role_teacher','role_admin')")
    public Result<List<Map<String, Object>>> getAllCoursesStats() {
        try {
            List<Map<String, Object>> result = jdbcTemplate.queryForList("CALL proc_get_all_course_question_stats()");
            return Result.success("调用成功", result);
        } catch (Exception e) {
            return Result.failed("调用存储过程失败: " + e.getMessage());
        }
    }

    @GetMapping("/view/course-types")
    @ApiOperation("查询视图：各门课程使用的题型")
    @PreAuthorize("hasAnyAuthority('role_student','role_teacher','role_admin')")
    public Result<List<Map<String, Object>>> getCourseTypesFromView() {
        try {
            List<Map<String, Object>> result = jdbcTemplate.queryForList("SELECT * FROM v_course_question_types");
            return Result.success("查询成功", result);
        } catch (Exception e) {
            return Result.failed("查询视图失败: " + e.getMessage());
        }
    }

    @PostMapping("/auto-assemble")
    @ApiOperation("调用存储过程：自动组卷")
    @PreAuthorize("hasAnyAuthority('role_teacher','role_admin')")
    public Result<Integer> autoAssemblePaper(@RequestBody Map<String, Object> params) {
        try {
            Integer courseId = (Integer) params.get("courseId");
            String title = (String) params.get("title");
            Integer duration = (Integer) params.get("duration");
            Integer passedScore = (Integer) params.get("passedScore");
            Integer radioCount = (Integer) params.get("radioCount");
            Integer radioScore = (Integer) params.get("radioScore");
            Integer multiCount = (Integer) params.get("multiCount");
            Integer multiScore = (Integer) params.get("multiScore");
            Integer judgeCount = (Integer) params.get("judgeCount");
            Integer judgeScore = (Integer) params.get("judgeScore");
            Integer saqCount = (Integer) params.get("saqCount");
            Integer saqScore = (Integer) params.get("saqScore");
            
            Integer userId = SecurityUtil.getUserId();

            Integer newExamId = jdbcTemplate.execute((Connection conn) -> {
                CallableStatement stmt = conn.prepareCall("{call proc_auto_assemble_paper(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}");
                stmt.setInt(1, courseId);
                stmt.setString(2, title);
                stmt.setInt(3, duration);
                stmt.setInt(4, passedScore);
                stmt.setInt(5, radioCount);
                stmt.setInt(6, radioScore);
                stmt.setInt(7, multiCount);
                stmt.setInt(8, multiScore);
                stmt.setInt(9, judgeCount);
                stmt.setInt(10, judgeScore);
                stmt.setInt(11, saqCount);
                stmt.setInt(12, saqScore);
                stmt.setInt(13, userId);
                stmt.registerOutParameter(14, Types.INTEGER);
                stmt.execute();
                return stmt.getInt(14);
            });
            
            return Result.success("自动组卷成功", newExamId);
        } catch (Exception e) {
            return Result.failed("自动组卷失败: " + e.getMessage());
        }
    }
}
