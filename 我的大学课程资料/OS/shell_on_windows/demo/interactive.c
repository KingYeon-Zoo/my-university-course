/*
 * interactive.c - 交互式Shell实现模块
 * 
 * 本文件实现了交互式shell界面（REPL: Read-Eval-Print Loop）。
 * 
 * 交互式模式特点:
 * - 显示彩色提示符，包含用户名、主机名和当前目录
 * - 支持命令历史记录
 * - 实时执行用户输入的命令
 * - 类似Bash的用户体验
 * 
 * REPL循环:
 * 1. Read: 读取用户输入
 * 2. Eval: 执行命令
 * 3. Print: 显示结果
 * 4. Loop: 继续循环
 */

/* 设置源文件编码为UTF-8 */
#pragma execution_character_set("utf-8")

#include "../kernel/include/shell_api.h"  /* Shell公共API */
#include <stdio.h>                        /* printf, fgets */
#include <stdlib.h>                       /* malloc, free */
#include <string.h>                       /* strlen, strcmp, memmove */
#include <windows.h>                      /* Windows API */
#include <direct.h>                       /* _getcwd */

/*============================================================================
 * 常量定义
 *============================================================================*/
#define MAX_LINE_LENGTH 4096  /* 最大命令行长度 */
#define HISTORY_SIZE 100      /* 历史记录最大条数 */

/*============================================================================
 * 命令历史记录
 * 
 * 使用简单的字符串数组存储命令历史。
 * 当历史满时，移除最旧的记录。
 *============================================================================*/
static char *command_history[HISTORY_SIZE];  /* 历史记录数组 */
static int history_count = 0;                /* 当前历史记录数量 */
static int history_index = 0;                /* 当前索引（用于历史浏览） */

/*============================================================================
 * ANSI颜色码定义
 *============================================================================*/
#define COLOR_RESET   "\x1b[0m"   /* 重置颜色 */
#define COLOR_GREEN   "\x1b[32m"  /* 绿色 - 用于用户@主机 */
#define COLOR_CYAN    "\x1b[36m"  /* 青色 - 用于当前目录 */

/*
 * add_to_history - 将命令添加到历史记录
 * 
 * @cmd: 要添加的命令字符串
 * 
 * 如果历史记录已满，移除最旧的记录。
 * 使用_strdup复制命令字符串。
 */
static void add_to_history(const char *cmd)
{
	/* 跳过空命令 */
	if (!cmd || !*cmd)
		return;
	
	/* 如果历史记录已满，释放最旧的条目 */
	if (history_count >= HISTORY_SIZE) {
		free(command_history[0]);
		/* 移动所有条目向前一个位置 */
		memmove(command_history, command_history + 1, 
		        sizeof(char *) * (HISTORY_SIZE - 1));
		history_count--;
	}
	
	/* 添加新命令 */
	command_history[history_count++] = _strdup(cmd);
	history_index = history_count;  /* 重置历史索引 */
}

/*
 * get_prompt - 构建命令提示符
 * 
 * @prompt: 输出缓冲区
 * @max_len: 缓冲区最大长度
 * 
 * 提示符格式: user@hostname:current_dir$
 * 使用ANSI颜色码使提示符更美观。
 */
static void get_prompt(char *prompt, int max_len)
{
	char cwd[MAX_PATH];       /* 当前工作目录 */
	char user[256];           /* 用户名 */
	char hostname[256];       /* 主机名 */
	DWORD size;
	
	/* 获取用户名 */
	size = sizeof(user);
	if (!GetUserNameA(user, &size))
		strcpy(user, "user");
	
	/* 获取计算机名 */
	size = sizeof(hostname);
	if (!GetComputerNameA(hostname, &size))
		strcpy(hostname, "pc");
	
	/* 获取当前工作目录 */
	if (!_getcwd(cwd, sizeof(cwd)))
		strcpy(cwd, "~");
	
	/* 格式化提示符 */
	/* 格式: [绿色]user@hostname[重置]:[青色]cwd[重置]$ */
	snprintf(prompt, max_len, COLOR_GREEN "%s@%s" COLOR_RESET ":" 
	        COLOR_CYAN "%s" COLOR_RESET "$ ", user, hostname, cwd);
}

/*
 * read_line - 读取一行用户输入
 * 
 * @buffer: 输出缓冲区
 * @max_len: 缓冲区最大长度
 * @返回值: 成功返回0，失败返回-1（如EOF）
 * 
 * 移除输入末尾的换行符。
 */
static int read_line(char *buffer, int max_len)
{
	if (!fgets(buffer, max_len, stdin))
		return -1;  /* EOF或错误 */
	
	/* 移除行尾换行符 */
	{
		size_t len = strlen(buffer);
		if (len > 0 && buffer[len - 1] == '\n')
			buffer[len - 1] = '\0';
	}
	
	return 0;
}

/*
 * interactive_shell - 交互式shell主函数
 * 
 * @ctx: shell上下文句柄
 * 
 * 实现REPL循环:
 * 1. 显示提示符
 * 2. 读取用户输入
 * 3. 添加到历史记录
 * 4. 执行命令
 * 5. 检查是否应该退出
 * 6. 重复
 */
void interactive_shell(shell_context_t ctx)
{
	char line[MAX_LINE_LENGTH];
	char prompt[512];
	int exit_code;
	
	/* 参数检查 */
	if (!ctx)
		return;
	
	/* 显示欢迎信息 */
	printf("\n");
	printf("欢迎使用交互式 Shell！\n");
	printf("输入命令开始，输入 'exit' 退出。\n");
	printf("\n");
	
	/* REPL主循环 */
	while (1) {
		/* 显示提示符 */
		get_prompt(prompt, sizeof(prompt));
		printf("%s", prompt);
		fflush(stdout);
		
		/* 读取命令 */
		if (read_line(line, sizeof(line)) < 0)
			break;  /* EOF */
		
		/* 跳过空行 */
		if (!line[0])
			continue;
		
		/* 添加到历史记录 */
		add_to_history(line);
		
		/* 执行命令 */
		exit_code = shell_exec_line(ctx, line);
		
		/* 检查是否应该退出（用户执行了exit命令） */
		if (shell_should_exit(ctx))
			break;
	}
	
	printf("\n退出交互式 Shell\n");
}

/*
 * cleanup_history - 清理历史记录
 * 
 * 释放所有历史记录占用的内存。
 * 应在程序退出前调用。
 */
void cleanup_history(void)
{
	int i;
	
	for (i = 0; i < history_count; i++) {
		if (command_history[i])
			free(command_history[i]);
	}
	history_count = 0;
}
