/*
 * debug_ui.c - 调试模式界面模块
 * 
 * 本文件实现了shell的调试模式界面。
 * 调试模式允许用户查看命令的词法分析和语法分析结果，
 * 便于理解shell如何解析和处理命令。
 * 
 * 主要功能:
 * - 显示词法分析（Tokenization）结果
 * - 显示语法分析（Parsing）结果
 * - 允许用户选择是否执行命令
 * 
 * 适用场景:
 * - 学习shell解释器的工作原理
 * - 调试复杂的shell脚本
 * - 验证命令的解析是否正确
 */

/* 设置源文件编码为UTF-8 */
#pragma execution_character_set("utf-8")

#include "../kernel/include/shell_api.h"  /* Shell公共API */
#include <stdio.h>                        /* printf, fgets, fflush */
#include <stdlib.h>                       /* 标准库 */
#include <string.h>                       /* strlen, strcmp */

/*============================================================================
 * ANSI颜色码定义
 * 用于在终端输出彩色文本，增强可读性
 *============================================================================*/
#define COLOR_RESET   "\x1b[0m"    /* 重置颜色 */
#define COLOR_YELLOW  "\x1b[33m"   /* 黄色 - 用于标题 */
#define COLOR_CYAN    "\x1b[36m"   /* 青色 - 用于提示和分隔线 */
#define COLOR_MAGENTA "\x1b[35m"   /* 洋红色 - 用于AST信息 */

/* 最大命令行长度 */
#define MAX_LINE_LENGTH 1024

/*
 * display_tokens - 显示词法分析结果
 * 
 * @ctx: shell上下文句柄
 * @line: 要分析的命令行
 * 
 * 调用shell的调试API获取Token信息，并格式化显示。
 * 每个Token显示其行号、类型和值。
 */
static void display_tokens(shell_context_t ctx, const char *line)
{
	char **tokens;
	int token_count;
	int i;
	
	printf(COLOR_CYAN "\n=== 词法分析结果 ===\n" COLOR_RESET);
	
	/* 调用调试API进行词法分析 */
	tokens = shell_debug_tokenize(ctx, line, &token_count);
	if (!tokens) {
		printf("词法分析失败\n");
		return;
	}
	
	/* 显示每个Token */
	for (i = 0; i < token_count; i++) {
		printf("%s\n", tokens[i]);
	}
	
	printf(COLOR_CYAN "共 %d 个 token\n" COLOR_RESET, token_count);
	
	/* 释放Token信息 */
	shell_debug_free_tokens(tokens, token_count);
}

/*
 * display_ast - 显示语法分析结果
 * 
 * @ctx: shell上下文句柄
 * @line: 要分析的命令行
 * 
 * 调用shell的调试API进行语法分析，显示AST创建结果。
 */
static void display_ast(shell_context_t ctx, const char *line)
{
	char *ast_str;
	
	printf(COLOR_MAGENTA "\n=== 语法分析结果 ===\n" COLOR_RESET);
	
	/* 调用调试API进行语法分析 */
	ast_str = shell_debug_parse(ctx, line);
	if (!ast_str) {
		printf("语法分析失败\n");
		return;
	}
	
	/* 显示AST信息 */
	printf("%s\n", ast_str);
	
	/* 释放AST信息 */
	shell_debug_free_ast(ast_str);
}

/*
 * debug_shell - 调试模式主函数
 * 
 * @ctx: shell上下文句柄
 * 
 * 提供一个交互式调试界面:
 * 1. 读取用户输入的命令
 * 2. 显示词法分析结果
 * 3. 显示语法分析结果
 * 4. 询问用户是否执行该命令
 * 5. 如果用户确认，执行命令并显示结果
 * 
 * 用户可以输入'q'或'quit'退出调试模式。
 */
void debug_shell(shell_context_t ctx)
{
	char line[MAX_LINE_LENGTH];
	char choice;
	
	/* 参数检查 */
	if (!ctx)
		return;
	
	/* 显示调试模式标题 */
	printf("\n");
	printf(COLOR_YELLOW "调试模式\n" COLOR_RESET);
	printf("输入命令查看解析过程，输入 'q' 退出。\n");
	printf("\n");
	
	/* 主循环 */
	while (1) {
		/* 显示调试提示符 */
		printf(COLOR_CYAN "debug> " COLOR_RESET);
		fflush(stdout);
		
		/* 读取用户输入 */
		if (!fgets(line, sizeof(line), stdin))
			break;
		
		/* 移除行尾换行符 */
		{
			size_t len = strlen(line);
			if (len > 0 && line[len - 1] == '\n')
				line[len - 1] = '\0';
		}
		
		/* 检查是否退出 */
		if (strcmp(line, "q") == 0 || strcmp(line, "quit") == 0)
			break;
		
		/* 跳过空行 */
		if (!line[0])
			continue;
		
		/* 显示词法分析结果 */
		display_tokens(ctx, line);
		
		/* 显示语法分析结果 */
		display_ast(ctx, line);
		
		/* 询问用户是否执行命令 */
		printf("\n是否执行该命令? (y/n): ");
		fflush(stdout);
		
		if (scanf("%c", &choice) == 1) {
			/* 清空输入缓冲区 */
			while (getchar() != '\n');
			
			if (choice == 'y' || choice == 'Y') {
				/* 用户确认执行 */
				printf(COLOR_YELLOW "\n=== 执行结果 ===\n" COLOR_RESET);
				shell_exec_line(ctx, line);
			}
		}
		
		printf("\n");
	}
	
	printf("\n退出调试模式\n");
}
