/*
 * builtin_cmd.c - 内置命令实现模块
 * 
 * 本文件实现了shell的内置命令（built-in commands）。
 * 
 * 内置命令的特点:
 * - 在shell进程内部执行，不创建子进程
 * - 可以直接访问和修改shell的状态（如变量表、当前目录）
 * - 执行效率高
 * 
 * 为什么需要内置命令:
 * - 某些命令必须在shell进程中执行（如cd改变工作目录）
 * - 提供跨平台兼容性（Windows没有直接对应的Unix命令）
 * - 可以访问shell内部状态（如变量）
 * 
 * 实现的内置命令:
 * - cd: 切换工作目录
 * - echo: 输出文本
 * - pwd: 打印当前目录
 * - export: 导出环境变量
 * - exit: 退出shell
 * - test/[: 条件测试
 * - ls: 列出目录内容
 * - cat: 显示文件内容
 * - mkdir: 创建目录
 * - rmdir: 删除目录
 * - rm: 删除文件
 * - cp: 复制文件
 * - mv: 移动/重命名文件
 * - touch: 创建文件或更新时间戳
 * - help: 显示帮助
 * - clear: 清屏
 */

#include "include/types.h"     /* 数据结构定义 */
#include "include/internal.h"  /* 内部接口定义 */
#include <stdlib.h>            /* atoi, malloc, free */
#include <string.h>            /* strcmp, strncpy, strcat */
#include <stdio.h>             /* snprintf */
#include <windows.h>           /* Windows API */
#include <direct.h>            /* _getcwd, _chdir */
#include <io.h>                /* 文件I/O */
#include <fcntl.h>             /* 文件标志 */
#include <sys/stat.h>          /* 文件状态 */

/* 外部回调函数声明 - 在shell_core.c中定义 */
extern void shell_output(struct exec_context *ctx, const char *output);
extern void shell_error(struct exec_context *ctx, const char *error, int line);

/*
 * builtin_cd - 内置命令：cd（切换目录）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组（args[0]="cd", args[1]=目标目录）
 * @argc: 参数数量
 * @返回值: 成功返回0，失败返回-1
 * 
 * 用法:
 * - cd         : 切换到HOME目录
 * - cd path    : 切换到指定目录
 * - cd -       : 切换到上一个目录（OLDPWD）
 * 
 * 更新的变量:
 * - PWD: 当前工作目录
 * - OLDPWD: 上一个工作目录
 */
int builtin_cd(struct exec_context *ctx, char **args, int argc)
{
	const char *path;
	char resolved_path[MAX_PATH_LEN];
	char new_path[MAX_PATH_LEN];
	const char *oldpwd;
	
	if (argc < 2) {
		/* 没有参数 - 切换到HOME目录 */
		path = var_table_get(ctx->vars, "HOME");
		if (!path)
			path = ".";
	} else if (strcmp(args[1], "-") == 0) {
		/* cd - : 切换到上一个目录 */
		oldpwd = var_table_get(ctx->vars, "OLDPWD");
		if (!oldpwd) {
			return -1;  /* 没有上一个目录 */
		}
		path = oldpwd;
		/* 打印将要切换到的目录 */
		{
			char output[MAX_PATH_LEN + 2];
			extern void shell_output(struct exec_context *ctx, const char *output);
			snprintf(output, sizeof(output), "%s\n", path);
			shell_output(ctx, output);
		}
	} else {
		path = args[1];
	}
	
	/* 在切换前保存当前目录作为OLDPWD */
	if (_getcwd(resolved_path, sizeof(resolved_path))) {
		var_table_set(ctx->vars, "OLDPWD", resolved_path);
	}
	
	/* 展开路径中的变量 */
	{
		char *expanded = expand_variables(ctx, path);
		if (expanded) {
			strncpy(new_path, expanded, MAX_PATH_LEN - 1);
			new_path[MAX_PATH_LEN - 1] = '\0';
			free(expanded);
		} else {
			strncpy(new_path, path, MAX_PATH_LEN - 1);
			new_path[MAX_PATH_LEN - 1] = '\0';
		}
	}
	
	/* 执行目录切换 */
	if (_chdir(new_path) != 0) {
		return -1;  /* 切换失败 */
	}
	
	/* 更新PWD变量 */
	if (_getcwd(resolved_path, sizeof(resolved_path))) {
		var_table_set(ctx->vars, "PWD", resolved_path);
		strncpy(ctx->current_dir, resolved_path, MAX_PATH_LEN - 1);
		ctx->current_dir[MAX_PATH_LEN - 1] = '\0';
	}
	
	return 0;
}

/*
 * builtin_echo - 内置命令：echo（输出文本）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 总是返回0
 * 
 * 用法:
 * - echo text     : 输出文本并换行
 * - echo -n text  : 输出文本不换行
 * 
 * 变量会被自动展开。
 */
int builtin_echo(struct exec_context *ctx, char **args, int argc)
{
	char output[MAX_VAR_VALUE * 2];
	int i;
	int newline = 1;       /* 是否输出换行 */
	int start_idx = 1;     /* 开始处理参数的索引 */
	
	output[0] = '\0';
	
	/* 检查 -n 标志（不输出换行） */
	if (argc > 1 && strcmp(args[1], "-n") == 0) {
		newline = 0;
		start_idx = 2;
	}
	
	/* 连接所有参数，用空格分隔 */
	for (i = start_idx; i < argc; i++) {
		char *expanded = expand_variables(ctx, args[i]);
		
		if (expanded) {
			if (i > start_idx)
				strncat(output, " ", sizeof(output) - strlen(output) - 1);
			strncat(output, expanded, sizeof(output) - strlen(output) - 1);
			free(expanded);
		}
	}
	
	/* 添加换行符（如果需要） */
	if (newline)
		strncat(output, "\n", sizeof(output) - strlen(output) - 1);
	
	/* 输出结果 */
	shell_output(ctx, output);
	
	return 0;
}

/*
 * builtin_pwd - 内置命令：pwd（打印工作目录）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组（未使用）
 * @argc: 参数数量（未使用）
 * @返回值: 成功返回0，失败返回-1
 */
int builtin_pwd(struct exec_context *ctx, char **args, int argc)
{
	char cwd[MAX_PATH_LEN];
	char output[MAX_PATH_LEN + 2];
	
	(void)args;   /* 未使用 */
	(void)argc;   /* 未使用 */
	
	/* 获取当前工作目录 */
	if (_getcwd(cwd, sizeof(cwd))) {
		snprintf(output, sizeof(output), "%s\n", cwd);
		shell_output(ctx, output);
		return 0;
	}
	
	return -1;
}

/*
 * builtin_export - 内置命令：export（导出环境变量）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 总是返回0
 * 
 * 用法:
 * - export VAR=value  : 设置并导出变量
 * - export VAR        : 仅导出已存在的变量
 */
int builtin_export(struct exec_context *ctx, char **args, int argc)
{
	int i;
	
	if (argc < 2)
		return 0;
	
	for (i = 1; i < argc; i++) {
		char *eq = strchr(args[i], '=');
		
		if (eq) {
			/* 格式: export VAR=value */
			*eq = '\0';  /* 临时分割字符串 */
			var_table_set(ctx->vars, args[i], eq + 1);
			var_table_export(ctx->vars, args[i]);
			*eq = '=';   /* 恢复原始字符串 */
		} else {
			/* 格式: export VAR（仅导出现有变量） */
			var_table_export(ctx->vars, args[i]);
		}
	}
	
	return 0;
}

/*
 * builtin_exit - 内置命令：exit（退出shell）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 退出码
 * 
 * 用法:
 * - exit      : 使用退出码0退出
 * - exit N    : 使用退出码N退出
 */
int builtin_exit(struct exec_context *ctx, char **args, int argc)
{
	int exit_code = 0;
	
	/* 如果提供了参数，使用它作为退出码 */
	if (argc > 1)
		exit_code = atoi(args[1]);
	
	/* 设置退出标志，主循环会检测到并退出 */
	ctx->should_exit = 1;
	ctx->last_exit_code = exit_code;
	
	return exit_code;
}

/*
 * builtin_test - 内置命令：test / [（条件测试）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 条件为真返回0，为假返回1
 * 
 * 支持的测试:
 * - 字符串比较: str1 = str2, str1 == str2, str1 != str2
 * - 数值比较: n1 -eq n2, n1 -ne n2, n1 -gt n2, n1 -ge n2, n1 -lt n2, n1 -le n2
 * - 文件测试: -f file（是否为普通文件）, -d dir（是否为目录）
 * - 字符串测试: -n str（非空）, -z str（为空）
 */
int builtin_test(struct exec_context *ctx, char **args, int argc)
{
	int result = 0;
	
	if (argc < 2)
		return 1;
	
	/* 字符串相等比较: str1 = str2 或 str1 == str2 */
	if (argc >= 4 && (strcmp(args[2], "=") == 0 || strcmp(args[2], "==") == 0)) {
		char *s1 = expand_variables(ctx, args[1]);
		char *s2 = expand_variables(ctx, args[3]);
		
		if (s1 && s2)
			result = (strcmp(s1, s2) == 0) ? 0 : 1;
		else
			result = 1;
		
		if (s1) free(s1);
		if (s2) free(s2);
		return result;
	}
	
	/* 字符串不等比较: str1 != str2 */
	if (argc >= 4 && strcmp(args[2], "!=") == 0) {
		char *s1 = expand_variables(ctx, args[1]);
		char *s2 = expand_variables(ctx, args[3]);
		
		if (s1 && s2)
			result = (strcmp(s1, s2) != 0) ? 0 : 1;
		else
			result = 1;
		
		if (s1) free(s1);
		if (s2) free(s2);
		return result;
	}
	
	/* 数值相等比较: n1 -eq n2 */
	if (argc >= 4 && strcmp(args[2], "-eq") == 0) {
		char *s1 = expand_variables(ctx, args[1]);
		char *s2 = expand_variables(ctx, args[3]);
		int n1 = atoi(s1 ? s1 : args[1]);
		int n2 = atoi(s2 ? s2 : args[3]);
		if (s1) free(s1);
		if (s2) free(s2);
		return (n1 == n2) ? 0 : 1;
	}
	
	/* 数值不等比较: n1 -ne n2 */
	if (argc >= 4 && strcmp(args[2], "-ne") == 0) {
		char *s1 = expand_variables(ctx, args[1]);
		char *s2 = expand_variables(ctx, args[3]);
		int n1 = atoi(s1 ? s1 : args[1]);
		int n2 = atoi(s2 ? s2 : args[3]);
		if (s1) free(s1);
		if (s2) free(s2);
		return (n1 != n2) ? 0 : 1;
	}
	
	/* 数值大于比较: n1 -gt n2 */
	if (argc >= 4 && strcmp(args[2], "-gt") == 0) {
		char *s1 = expand_variables(ctx, args[1]);
		char *s2 = expand_variables(ctx, args[3]);
		int n1 = atoi(s1 ? s1 : args[1]);
		int n2 = atoi(s2 ? s2 : args[3]);
		if (s1) free(s1);
		if (s2) free(s2);
		return (n1 > n2) ? 0 : 1;
	}
	
	/* 数值大于等于比较: n1 -ge n2 */
	if (argc >= 4 && strcmp(args[2], "-ge") == 0) {
		char *s1 = expand_variables(ctx, args[1]);
		char *s2 = expand_variables(ctx, args[3]);
		int n1 = atoi(s1 ? s1 : args[1]);
		int n2 = atoi(s2 ? s2 : args[3]);
		if (s1) free(s1);
		if (s2) free(s2);
		return (n1 >= n2) ? 0 : 1;
	}
	
	/* 数值小于比较: n1 -lt n2 */
	if (argc >= 4 && strcmp(args[2], "-lt") == 0) {
		char *s1 = expand_variables(ctx, args[1]);
		char *s2 = expand_variables(ctx, args[3]);
		int n1 = atoi(s1 ? s1 : args[1]);
		int n2 = atoi(s2 ? s2 : args[3]);
		if (s1) free(s1);
		if (s2) free(s2);
		return (n1 < n2) ? 0 : 1;
	}
	
	/* 数值小于等于比较: n1 -le n2 */
	if (argc >= 4 && strcmp(args[2], "-le") == 0) {
		char *s1 = expand_variables(ctx, args[1]);
		char *s2 = expand_variables(ctx, args[3]);
		int n1 = atoi(s1 ? s1 : args[1]);
		int n2 = atoi(s2 ? s2 : args[3]);
		if (s1) free(s1);
		if (s2) free(s2);
		return (n1 <= n2) ? 0 : 1;
	}
	
	/* 文件测试: -f file（是否为普通文件） */
	if (argc >= 3 && strcmp(args[1], "-f") == 0) {
		DWORD attrs = GetFileAttributesA(args[2]);
		return (attrs != INVALID_FILE_ATTRIBUTES && 
		        !(attrs & FILE_ATTRIBUTE_DIRECTORY)) ? 0 : 1;
	}
	
	/* 目录测试: -d dir（是否为目录） */
	if (argc >= 3 && strcmp(args[1], "-d") == 0) {
		DWORD attrs = GetFileAttributesA(args[2]);
		return (attrs != INVALID_FILE_ATTRIBUTES && 
		        (attrs & FILE_ATTRIBUTE_DIRECTORY)) ? 0 : 1;
	}
	
	/* 字符串非空测试: -n str */
	if (argc >= 3 && strcmp(args[1], "-n") == 0) {
		return (strlen(args[2]) > 0) ? 0 : 1;
	}
	
	/* 字符串为空测试: -z str */
	if (argc >= 3 && strcmp(args[1], "-z") == 0) {
		return (strlen(args[2]) == 0) ? 0 : 1;
	}
	
	/* 默认: 单个参数，非空则为真 */
	if (argc == 2) {
		return (strlen(args[1]) > 0) ? 0 : 1;
	}
	
	return 1;
}

/*
 * builtin_ls - 内置命令：ls（列出目录内容）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 成功返回0，失败返回1
 * 
 * 用法:
 * - ls        : 列出当前目录
 * - ls path   : 列出指定目录
 */
int builtin_ls(struct exec_context *ctx, char **args, int argc)
{
	char search_path[MAX_PATH_LEN];
	WIN32_FIND_DATAA find_data;
	HANDLE find_handle;
	char output[MAX_PATH_LEN + 2];
	const char *path;
	
	/* 确定要列出的目录 */
	if (argc < 2) {
		path = ".";  /* 默认为当前目录 */
	} else {
		path = args[1];
	}
	
	/* 构建搜索模式: path\* */
	snprintf(search_path, sizeof(search_path), "%s\\*", path);
	
	/* 查找第一个文件 */
	find_handle = FindFirstFileA(search_path, &find_data);
	if (find_handle == INVALID_HANDLE_VALUE) {
		snprintf(output, sizeof(output), "ls: cannot access '%s': No such file or directory\n", path);
		shell_output(ctx, output);
		return 1;
	}
	
	/* 遍历所有文件 */
	do {
		/* 跳过 . 和 .. */
		if (strcmp(find_data.cFileName, ".") == 0 ||
		    strcmp(find_data.cFileName, "..") == 0) {
			continue;
		}
		
		snprintf(output, sizeof(output), "%s\n", find_data.cFileName);
		shell_output(ctx, output);
	} while (FindNextFileA(find_handle, &find_data));
	
	FindClose(find_handle);
	return 0;
}

/*
 * builtin_cat - 内置命令：cat（显示文件内容）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 成功返回0，有错误返回1
 * 
 * 用法: cat file1 [file2 ...]
 */
int builtin_cat(struct exec_context *ctx, char **args, int argc)
{
	HANDLE file;
	char buffer[4096];
	DWORD bytes_read;
	char output[256];
	int i;
	int result = 0;
	
	if (argc < 2) {
		shell_output(ctx, "cat: missing operand\n");
		return 1;
	}
	
	/* 处理每个文件 */
	for (i = 1; i < argc; i++) {
		file = CreateFileA(args[i], GENERIC_READ, FILE_SHARE_READ, NULL,
		                   OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
		if (file == INVALID_HANDLE_VALUE) {
			snprintf(output, sizeof(output), "cat: %s: No such file or directory\n", args[i]);
			shell_output(ctx, output);
			result = 1;
			continue;
		}
		
		/* 读取并输出文件内容 */
		while (ReadFile(file, buffer, sizeof(buffer) - 1, &bytes_read, NULL) && bytes_read > 0) {
			buffer[bytes_read] = '\0';
			shell_output(ctx, buffer);
		}
		
		CloseHandle(file);
	}
	
	return result;
}

/*
 * builtin_mkdir - 内置命令：mkdir（创建目录）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 成功返回0，有错误返回1
 * 
 * 用法: mkdir dir1 [dir2 ...]
 */
int builtin_mkdir(struct exec_context *ctx, char **args, int argc)
{
	char output[MAX_PATH_LEN + 64];
	int i;
	int result = 0;
	
	if (argc < 2) {
		shell_output(ctx, "mkdir: missing operand\n");
		return 1;
	}
	
	for (i = 1; i < argc; i++) {
		if (!CreateDirectoryA(args[i], NULL)) {
			DWORD err = GetLastError();
			if (err == ERROR_ALREADY_EXISTS) {
				snprintf(output, sizeof(output), "mkdir: cannot create directory '%s': File exists\n", args[i]);
			} else {
				snprintf(output, sizeof(output), "mkdir: cannot create directory '%s': Error %lu\n", args[i], err);
			}
			shell_output(ctx, output);
			result = 1;
		}
	}
	
	return result;
}

/*
 * builtin_rmdir - 内置命令：rmdir（删除空目录）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 成功返回0，有错误返回1
 * 
 * 用法: rmdir dir1 [dir2 ...]
 * 注意: 只能删除空目录
 */
int builtin_rmdir(struct exec_context *ctx, char **args, int argc)
{
	char output[MAX_PATH_LEN + 64];
	int i;
	int result = 0;
	
	if (argc < 2) {
		shell_output(ctx, "rmdir: missing operand\n");
		return 1;
	}
	
	for (i = 1; i < argc; i++) {
		if (!RemoveDirectoryA(args[i])) {
			DWORD err = GetLastError();
			if (err == ERROR_DIR_NOT_EMPTY) {
				snprintf(output, sizeof(output), "rmdir: failed to remove '%s': Directory not empty\n", args[i]);
			} else if (err == ERROR_FILE_NOT_FOUND || err == ERROR_PATH_NOT_FOUND) {
				snprintf(output, sizeof(output), "rmdir: failed to remove '%s': No such file or directory\n", args[i]);
			} else {
				snprintf(output, sizeof(output), "rmdir: failed to remove '%s': Error %lu\n", args[i], err);
			}
			shell_output(ctx, output);
			result = 1;
		}
	}
	
	return result;
}

/*
 * builtin_rm - 内置命令：rm（删除文件）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 成功返回0，有错误返回1
 * 
 * 用法: rm file1 [file2 ...]
 * 注意: 不能删除目录（使用rmdir）
 */
int builtin_rm(struct exec_context *ctx, char **args, int argc)
{
	char output[MAX_PATH_LEN + 64];
	DWORD attrs;
	int i;
	int result = 0;
	
	if (argc < 2) {
		shell_output(ctx, "rm: missing operand\n");
		return 1;
	}
	
	for (i = 1; i < argc; i++) {
		/* 检查文件属性 */
		attrs = GetFileAttributesA(args[i]);
		if (attrs == INVALID_FILE_ATTRIBUTES) {
			snprintf(output, sizeof(output), "rm: cannot remove '%s': No such file or directory\n", args[i]);
			shell_output(ctx, output);
			result = 1;
			continue;
		}
		
		/* 检查是否为目录 */
		if (attrs & FILE_ATTRIBUTE_DIRECTORY) {
			snprintf(output, sizeof(output), "rm: cannot remove '%s': Is a directory\n", args[i]);
			shell_output(ctx, output);
			result = 1;
			continue;
		}
		
		/* 删除文件 */
		if (!DeleteFileA(args[i])) {
			snprintf(output, sizeof(output), "rm: cannot remove '%s': Error %lu\n", args[i], GetLastError());
			shell_output(ctx, output);
			result = 1;
		}
	}
	
	return result;
}

/*
 * builtin_cp - 内置命令：cp（复制文件）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 成功返回0，失败返回1
 * 
 * 用法: cp source destination
 */
int builtin_cp(struct exec_context *ctx, char **args, int argc)
{
	char output[MAX_PATH_LEN * 2 + 64];
	
	if (argc < 3) {
		shell_output(ctx, "cp: missing destination file operand\n");
		return 1;
	}
	
	/* 执行复制操作 */
	if (!CopyFileA(args[1], args[2], FALSE)) {
		DWORD err = GetLastError();
		if (err == ERROR_FILE_NOT_FOUND) {
			snprintf(output, sizeof(output), "cp: cannot stat '%s': No such file or directory\n", args[1]);
		} else {
			snprintf(output, sizeof(output), "cp: cannot copy '%s' to '%s': Error %lu\n", args[1], args[2], err);
		}
		shell_output(ctx, output);
		return 1;
	}
	
	return 0;
}

/*
 * builtin_mv - 内置命令：mv（移动/重命名文件）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 成功返回0，失败返回1
 * 
 * 用法: mv source destination
 */
int builtin_mv(struct exec_context *ctx, char **args, int argc)
{
	char output[MAX_PATH_LEN * 2 + 64];
	
	if (argc < 3) {
		shell_output(ctx, "mv: missing destination file operand\n");
		return 1;
	}
	
	/* 执行移动操作（允许覆盖已存在的目标） */
	if (!MoveFileExA(args[1], args[2], MOVEFILE_REPLACE_EXISTING)) {
		DWORD err = GetLastError();
		if (err == ERROR_FILE_NOT_FOUND) {
			snprintf(output, sizeof(output), "mv: cannot stat '%s': No such file or directory\n", args[1]);
		} else {
			snprintf(output, sizeof(output), "mv: cannot move '%s' to '%s': Error %lu\n", args[1], args[2], err);
		}
		shell_output(ctx, output);
		return 1;
	}
	
	return 0;
}

/*
 * builtin_touch - 内置命令：touch（创建文件或更新时间戳）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 成功返回0，有错误返回1
 * 
 * 用法: touch file1 [file2 ...]
 */
int builtin_touch(struct exec_context *ctx, char **args, int argc)
{
	HANDLE file;
	FILETIME ft;
	SYSTEMTIME st;
	char output[MAX_PATH_LEN + 64];
	int i;
	int result = 0;
	
	if (argc < 2) {
		shell_output(ctx, "touch: missing file operand\n");
		return 1;
	}
	
	for (i = 1; i < argc; i++) {
		/* 尝试打开现有文件或创建新文件 */
		file = CreateFileA(args[i], GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE,
		                   NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
		if (file == INVALID_HANDLE_VALUE) {
			snprintf(output, sizeof(output), "touch: cannot touch '%s': Error %lu\n", args[i], GetLastError());
			shell_output(ctx, output);
			result = 1;
			continue;
		}
		
		/* 更新文件时间戳为当前时间 */
		GetSystemTime(&st);
		SystemTimeToFileTime(&st, &ft);
		SetFileTime(file, NULL, &ft, &ft);
		
		CloseHandle(file);
	}
	
	return result;
}

/*
 * builtin_help - 内置命令：help（显示帮助）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组（未使用）
 * @argc: 参数数量（未使用）
 * @返回值: 总是返回0
 */
int builtin_help(struct exec_context *ctx, char **args, int argc)
{
	(void)args;
	(void)argc;
	
	shell_output(ctx, "Shell built-in commands:\n");
	shell_output(ctx, "  cd [dir]         Change working directory\n");
	shell_output(ctx, "  pwd              Print working directory\n");
	shell_output(ctx, "  echo [args...]   Display a line of text\n");
	shell_output(ctx, "  export VAR=val   Set environment variable\n");
	shell_output(ctx, "  exit [code]      Exit the shell\n");
	shell_output(ctx, "  test [expr]      Evaluate conditional expression\n");
	shell_output(ctx, "  ls [path]        List directory contents\n");
	shell_output(ctx, "  cat <file...>    Concatenate and print files\n");
	shell_output(ctx, "  mkdir <dir...>   Create directories\n");
	shell_output(ctx, "  rmdir <dir...>   Remove empty directories\n");
	shell_output(ctx, "  rm <file...>     Remove files\n");
	shell_output(ctx, "  cp <src> <dst>   Copy file\n");
	shell_output(ctx, "  mv <src> <dst>   Move/rename file\n");
	shell_output(ctx, "  touch <file...>  Create file or update timestamp\n");
	shell_output(ctx, "  clear            Clear the screen\n");
	shell_output(ctx, "  help             Show this help message\n");
	
	return 0;
}

/*
 * builtin_clear - 内置命令：clear（清屏）
 * 
 * @ctx: 执行上下文
 * @args: 参数数组（未使用）
 * @argc: 参数数量（未使用）
 * @返回值: 总是返回0
 */
int builtin_clear(struct exec_context *ctx, char **args, int argc)
{
	(void)args;
	(void)argc;
	
	/* 输出ANSI转义序列清屏并将光标移到左上角 */
	shell_output(ctx, "\x1b[2J\x1b[H");
	
	return 0;
}

/*
 * is_builtin - 检查命令是否是内置命令
 * 
 * @cmd: 命令名称
 * @返回值: 是内置命令返回1，否则返回0
 */
int is_builtin(const char *cmd)
{
	if (!cmd)
		return 0;
	
	/* 检查所有内置命令 */
	if (strcmp(cmd, "cd") == 0) return 1;
	if (strcmp(cmd, "echo") == 0) return 1;
	if (strcmp(cmd, "pwd") == 0) return 1;
	if (strcmp(cmd, "export") == 0) return 1;
	if (strcmp(cmd, "exit") == 0) return 1;
	if (strcmp(cmd, "test") == 0) return 1;
	if (strcmp(cmd, "[") == 0) return 1;  /* [ 是test的别名 */
	if (strcmp(cmd, "ls") == 0) return 1;
	if (strcmp(cmd, "cat") == 0) return 1;
	if (strcmp(cmd, "mkdir") == 0) return 1;
	if (strcmp(cmd, "rmdir") == 0) return 1;
	if (strcmp(cmd, "rm") == 0) return 1;
	if (strcmp(cmd, "cp") == 0) return 1;
	if (strcmp(cmd, "mv") == 0) return 1;
	if (strcmp(cmd, "touch") == 0) return 1;
	if (strcmp(cmd, "help") == 0) return 1;
	if (strcmp(cmd, "clear") == 0) return 1;
	
	return 0;
}

/*
 * execute_builtin - 执行内置命令
 * 
 * @ctx: 执行上下文
 * @cmd: 命令名称
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 命令的退出码，未找到命令返回-1
 */
int execute_builtin(struct exec_context *ctx, const char *cmd, 
                    char **args, int argc)
{
	/* 根据命令名调用对应的处理函数 */
	if (strcmp(cmd, "cd") == 0)
		return builtin_cd(ctx, args, argc);
	
	if (strcmp(cmd, "echo") == 0)
		return builtin_echo(ctx, args, argc);
	
	if (strcmp(cmd, "pwd") == 0)
		return builtin_pwd(ctx, args, argc);
	
	if (strcmp(cmd, "export") == 0)
		return builtin_export(ctx, args, argc);
	
	if (strcmp(cmd, "exit") == 0)
		return builtin_exit(ctx, args, argc);
	
	if (strcmp(cmd, "test") == 0 || strcmp(cmd, "[") == 0)
		return builtin_test(ctx, args, argc);
	
	if (strcmp(cmd, "ls") == 0)
		return builtin_ls(ctx, args, argc);
	
	if (strcmp(cmd, "cat") == 0)
		return builtin_cat(ctx, args, argc);
	
	if (strcmp(cmd, "mkdir") == 0)
		return builtin_mkdir(ctx, args, argc);
	
	if (strcmp(cmd, "rmdir") == 0)
		return builtin_rmdir(ctx, args, argc);
	
	if (strcmp(cmd, "rm") == 0)
		return builtin_rm(ctx, args, argc);
	
	if (strcmp(cmd, "cp") == 0)
		return builtin_cp(ctx, args, argc);
	
	if (strcmp(cmd, "mv") == 0)
		return builtin_mv(ctx, args, argc);
	
	if (strcmp(cmd, "touch") == 0)
		return builtin_touch(ctx, args, argc);
	
	if (strcmp(cmd, "help") == 0)
		return builtin_help(ctx, args, argc);
	
	if (strcmp(cmd, "clear") == 0)
		return builtin_clear(ctx, args, argc);
	
	return -1;  /* 未找到命令 */
}
