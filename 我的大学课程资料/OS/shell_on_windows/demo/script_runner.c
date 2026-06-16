/*
 * script_runner.c - 脚本文件执行模块
 * 
 * 本文件实现了shell脚本文件的执行功能。
 * 
 * 主要功能:
 * - 检查脚本文件是否存在
 * - 执行脚本并计时
 * - 显示执行结果和统计信息
 * - 列出可用的测试脚本
 * 
 * 支持的脚本格式:
 * - .sh 文件（Unix/Linux shell脚本）
 * - UTF-8编码
 * - 支持多种控制结构（if, while, for等）
 */

/* 设置源文件编码为UTF-8 */
#pragma execution_character_set("utf-8")

#include "../kernel/include/shell_api.h"  /* Shell公共API */
#include <stdio.h>                        /* printf */
#include <stdlib.h>                       /* 标准库 */
#include <string.h>                       /* 字符串操作 */
#include <windows.h>                      /* Windows API */

/*============================================================================
 * ANSI颜色码定义
 *============================================================================*/
#define COLOR_RESET   "\x1b[0m"   /* 重置颜色 */
#define COLOR_RED     "\x1b[31m"  /* 红色 - 用于错误信息 */
#define COLOR_GREEN   "\x1b[32m"  /* 绿色 - 用于成功信息 */
#define COLOR_BLUE    "\x1b[34m"  /* 蓝色 - 用于状态信息 */

/*
 * file_exists - 检查文件是否存在
 * 
 * @filepath: 文件路径
 * @返回值: 存在返回1，不存在返回0
 * 
 * 使用GetFileAttributes API检查文件属性。
 * 确保路径指向的是文件而不是目录。
 */
static int file_exists(const char *filepath)
{
	DWORD attrs = GetFileAttributesA(filepath);
	return (attrs != INVALID_FILE_ATTRIBUTES && 
	        !(attrs & FILE_ATTRIBUTE_DIRECTORY));
}

/*
 * run_script_file - 执行脚本文件
 * 
 * @ctx: shell上下文句柄
 * @filepath: 脚本文件路径
 * @返回值: 脚本退出码，失败返回-1
 * 
 * 执行流程:
 * 1. 检查文件是否存在
 * 2. 显示开始执行信息
 * 3. 记录开始时间
 * 4. 调用shell_exec_file执行脚本
 * 5. 记录结束时间
 * 6. 显示执行结果和耗时
 */
int run_script_file(shell_context_t ctx, const char *filepath)
{
	int result;
	DWORD start_time, end_time;
	
	/* 参数检查 */
	if (!ctx || !filepath)
		return -1;
	
	/* 检查文件是否存在 */
	if (!file_exists(filepath)) {
		printf(COLOR_RED "错误: 文件 '%s' 不存在\n" COLOR_RESET, filepath);
		return -1;
	}
	
	/* 显示开始执行信息 */
	printf(COLOR_BLUE "================================\n");
	printf("开始执行脚本: %s\n", filepath);
	printf("================================\n" COLOR_RESET);
	printf("\n");
	
	/* 记录开始时间 */
	start_time = GetTickCount();
	
	/* 执行脚本 */
	result = shell_exec_file(ctx, filepath);
	
	/* 记录结束时间 */
	end_time = GetTickCount();
	
	/* 显示执行结果 */
	printf("\n");
	printf(COLOR_BLUE "================================\n");
	
	if (result == 0) {
		printf(COLOR_GREEN "脚本执行成功！\n" COLOR_RESET);
	} else {
		printf(COLOR_RED "脚本执行失败，退出码: %d\n" COLOR_RESET, result);
	}
	
	/* 显示执行耗时 */
	printf(COLOR_BLUE "执行时间: %lu 毫秒\n", end_time - start_time);
	printf("================================\n" COLOR_RESET);
	
	return result;
}

/*
 * list_test_scripts - 列出可用的测试脚本
 * 
 * 在test目录下搜索所有.sh文件，并显示列表。
 * 方便用户查看有哪些测试脚本可以执行。
 * 
 * 使用Windows的FindFirstFile/FindNextFile API进行文件搜索。
 */
void list_test_scripts(void)
{
	WIN32_FIND_DATAA find_data;
	HANDLE find_handle;
	int count = 0;
	
	printf("\n");
	printf(COLOR_BLUE "可用的测试脚本:\n" COLOR_RESET);
	printf("--------------------------------\n");
	
	/* 搜索test目录下的.sh文件 */
	find_handle = FindFirstFileA("test\\*.sh", &find_data);
	if (find_handle != INVALID_HANDLE_VALUE) {
		do {
			printf("  %d. test\\%s\n", ++count, find_data.cFileName);
		} while (FindNextFileA(find_handle, &find_data));
		
		FindClose(find_handle);
	}
	
	/* 如果没有找到任何脚本 */
	if (count == 0) {
		printf("  (未找到测试脚本)\n");
	}
	
	printf("--------------------------------\n");
}
