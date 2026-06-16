/*
 * main.c - Shell演示程序主入口
 * 
 * 本文件是shell演示程序的主入口点。
 * 提供一个用户友好的菜单界面，展示shell的各种功能。
 * 
 * 功能菜单:
 * 1. 交互式Shell - 进入类似Bash的命令行界面
 * 2. 执行脚本 - 运行.sh脚本文件
 * 3. 调试模式 - 查看命令的解析过程
 * 4. 退出
 * 
 * 使用方式:
 * - 直接运行程序显示菜单
 * - 命令行参数指定脚本文件直接执行
 */

/* 设置源文件编码为UTF-8 */
#pragma execution_character_set("utf-8")

#include "../kernel/include/shell_api.h"  /* Shell公共API */
#include <stdio.h>                        /* printf, scanf, fgets */
#include <stdlib.h>                       /* exit */
#include <string.h>                       /* strlen */
#include <windows.h>                      /* Windows API */

/* 兼容旧版MinGW - 定义缺失的常量 */
#ifndef ENABLE_VIRTUAL_TERMINAL_PROCESSING
#define ENABLE_VIRTUAL_TERMINAL_PROCESSING 0x0004
#endif

/*============================================================================
 * 外部函数声明
 * 这些函数在其他文件中实现
 *============================================================================*/
extern void interactive_shell(shell_context_t ctx);  /* 交互式shell */
extern int run_script_file(shell_context_t ctx, const char *filepath);  /* 运行脚本 */
extern void debug_shell(shell_context_t ctx);        /* 调试模式 */

/*============================================================================
 * ANSI颜色码定义
 * 用于在终端输出彩色文本
 *============================================================================*/
#define COLOR_RESET   "\x1b[0m"   /* 重置颜色 */
#define COLOR_RED     "\x1b[31m"  /* 红色 - 用于错误信息 */
#define COLOR_GREEN   "\x1b[32m"  /* 绿色 - 用于菜单选项 */
#define COLOR_YELLOW  "\x1b[33m"  /* 黄色 - 用于成功信息 */
#define COLOR_BLUE    "\x1b[34m"  /* 蓝色 - 用于状态信息 */
#define COLOR_CYAN    "\x1b[36m"  /* 青色 - 用于标题框 */

/*
 * output_callback - 输出回调函数
 * 
 * @user_data: 用户数据（未使用）
 * @output: 要输出的文本
 * 
 * Shell通过此回调函数输出命令执行结果。
 * 直接将文本打印到标准输出。
 */
static void output_callback(void *user_data, const char *output)
{
	(void)user_data;  /* 未使用 */
	printf("%s", output);
}

/*
 * error_callback - 错误回调函数
 * 
 * @user_data: 用户数据（未使用）
 * @error: 错误信息
 * @line_number: 错误发生的行号（0表示无特定行）
 * 
 * Shell通过此回调函数报告错误。
 * 使用红色显示错误信息。
 */
static void error_callback(void *user_data, const char *error, int line_number)
{
	(void)user_data;  /* 未使用 */
	if (line_number > 0)
		printf(COLOR_RED "[Error at line %d] %s" COLOR_RESET "\n", 
		       line_number, error);
	else
		printf(COLOR_RED "[Error] %s" COLOR_RESET "\n", error);
}

/*
 * enable_console_colors - 启用Windows控制台的ANSI颜色支持
 * 
 * Windows 10及更高版本的控制台支持ANSI转义序列，
 * 但需要手动启用虚拟终端处理模式。
 * 同时设置控制台编码为UTF-8以支持中文显示。
 */
static void enable_console_colors(void)
{
	HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
	DWORD dwMode = 0;
	
	/* 设置控制台为UTF-8编码以正确显示中文 */
	SetConsoleOutputCP(65001);  /* UTF-8 */
	SetConsoleCP(65001);        /* UTF-8 */
	
	/* 启用虚拟终端处理（ANSI支持） */
	GetConsoleMode(hOut, &dwMode);
	dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
	SetConsoleMode(hOut, dwMode);
}

/*
 * display_menu - 显示主菜单
 * 
 * 显示程序的功能菜单，让用户选择要使用的功能。
 */
static void display_menu(void)
{
	printf("\n");
	printf(COLOR_CYAN "========================================\n");
	printf("   Unix/Linux Shell 解释器 for Windows\n");
	printf("========================================\n" COLOR_RESET);
	printf("\n");
	printf(COLOR_GREEN "1. " COLOR_RESET "进入交互式 Shell\n");
	printf(COLOR_GREEN "2. " COLOR_RESET "执行 .sh 脚本文件\n");
	printf(COLOR_GREEN "3. " COLOR_RESET "查看解析过程（调试模式）\n");
	printf(COLOR_GREEN "4. " COLOR_RESET "退出\n");
	printf("\n");
	printf("请选择: ");
}

/*
 * get_script_filename - 获取用户输入的脚本文件名
 * 
 * @filename: 输出缓冲区
 * @max_len: 缓冲区最大长度
 * @返回值: 成功返回0，失败返回-1
 */
static int get_script_filename(char *filename, int max_len)
{
	printf("请输入脚本文件路径: ");
	if (!fgets(filename, max_len, stdin))
		return -1;
	
	/* 移除行尾换行符 */
	{
		size_t len = strlen(filename);
		if (len > 0 && filename[len - 1] == '\n')
			filename[len - 1] = '\0';
	}
	
	return 0;
}

/*
 * main - 程序主入口
 * 
 * @argc: 命令行参数数量
 * @argv: 命令行参数数组
 * @返回值: 程序退出码
 * 
 * 程序流程:
 * 1. 启用控制台颜色支持
 * 2. 设置回调函数
 * 3. 初始化shell
 * 4. 如果有命令行参数，直接执行脚本
 * 5. 否则显示菜单，处理用户选择
 * 6. 退出前清理资源
 */
int main(int argc, char *argv[])
{
	shell_context_t shell_ctx;
	shell_callbacks_t callbacks;
	int choice;
	int running = 1;
	char script_path[512];
	
	/* 抑制未使用参数警告 */
	(void)argc;
	(void)argv;
	
	/* 启用控制台颜色支持 */
	enable_console_colors();
	
	/* 设置回调函数 */
	callbacks.output_cb = output_callback;
	callbacks.error_cb = error_callback;
	callbacks.user_data = NULL;
	
	/* 初始化shell */
	shell_ctx = shell_init(&callbacks);
	if (!shell_ctx) {
		printf(COLOR_RED "Failed to initialize shell\n" COLOR_RESET);
		return 1;
	}
	
	printf(COLOR_YELLOW "Shell 初始化成功！\n" COLOR_RESET);
	
	/* 如果命令行提供了脚本文件，直接执行 */
	if (argc > 1) {
		printf(COLOR_BLUE "执行脚本: %s\n" COLOR_RESET, argv[1]);
		run_script_file(shell_ctx, argv[1]);
		shell_destroy(shell_ctx);
		return 0;
	}
	
	/* 主菜单循环 */
	while (running) {
		display_menu();
		
		/* 读取用户选择 */
		if (scanf("%d", &choice) != 1) {
			/* 清空输入缓冲区 */
			while (getchar() != '\n');
			printf(COLOR_RED "无效输入！\n" COLOR_RESET);
			continue;
		}
		
		/* 清空输入缓冲区 */
		while (getchar() != '\n');
		
		/* 处理用户选择 */
		switch (choice) {
		case 1:
			/* 交互式Shell */
			printf(COLOR_BLUE "\n进入交互式 Shell（输入 'exit' 退出）\n" COLOR_RESET);
			interactive_shell(shell_ctx);
			break;
			
		case 2:
			/* 执行脚本文件 */
			if (get_script_filename(script_path, sizeof(script_path)) == 0) {
				printf(COLOR_BLUE "\n执行脚本: %s\n" COLOR_RESET, script_path);
				run_script_file(shell_ctx, script_path);
			}
			break;
			
		case 3:
			/* 调试模式 */
			printf(COLOR_BLUE "\n进入调试模式\n" COLOR_RESET);
			debug_shell(shell_ctx);
			break;
			
		case 4:
			/* 退出 */
			running = 0;
			break;
			
		default:
			printf(COLOR_RED "无效选择！\n" COLOR_RESET);
			break;
		}
	}
	
	printf(COLOR_YELLOW "\n感谢使用！再见！\n" COLOR_RESET);
	
	/* 清理资源 */
	shell_destroy(shell_ctx);
	
	return 0;
}
