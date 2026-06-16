/*
 * cmd_mapping.c - Unix到Windows命令映射模块
 * 
 * 本文件实现了Unix/Linux命令到Windows等效命令的转换功能。
 * 
 * 背景说明:
 * 许多常用的Unix命令在Windows上没有直接的等效命令，或者命令名不同。
 * 此模块提供一个映射表，将Unix命令自动转换为Windows命令。
 * 
 * 例如:
 * - ls -> dir (列出目录内容)
 * - cat -> type (显示文件内容)
 * - rm -> del (删除文件)
 * 
 * 注意:
 * 由于我们实现了大多数常用命令作为内置命令，
 * 此映射表主要用于那些直接调用外部程序的情况。
 */

#include "include/types.h"     /* 数据结构定义 */
#include "include/internal.h"  /* 内部接口定义 */
#include <string.h>            /* strcmp */

/*
 * 命令映射表
 * 
 * 静态数组，存储Unix命令到Windows命令的映射关系。
 * 以NULL, NULL结尾表示表结束。
 * 
 * 映射说明:
 * - ls -> dir: 列出目录内容
 * - cat -> type: 显示文件内容
 * - rm -> del: 删除文件
 * - cp -> copy: 复制文件
 * - mv -> move: 移动文件
 * - clear -> cls: 清屏
 * - grep -> findstr: 搜索文本
 * - touch -> type nul >: 创建空文件（不完全等效）
 */
static const struct cmd_mapping mappings[] = {
	{"ls", "dir"},           /* 列出目录 */
	{"cat", "type"},         /* 显示文件 */
	{"rm", "del"},           /* 删除文件 */
	{"cp", "copy"},          /* 复制文件 */
	{"mv", "move"},          /* 移动文件 */
	{"clear", "cls"},        /* 清屏 */
	{"grep", "findstr"},     /* 搜索文本 */
	{"touch", "type nul >"}, /* 创建空文件 */
	{NULL, NULL}             /* 表结束标记 */
};

/*
 * map_unix_to_windows - 将Unix命令映射为Windows等效命令
 * 
 * @unix_cmd: Unix命令名称
 * @返回值: 对应的Windows命令名称，如果没有找到映射则返回原命令
 * 
 * 工作流程:
 * 1. 遍历映射表
 * 2. 查找匹配的Unix命令
 * 3. 如果找到，返回对应的Windows命令
 * 4. 如果没找到，返回原命令（假设命令在Windows上也可用）
 * 
 * 示例:
 *   map_unix_to_windows("ls")     -> "dir"
 *   map_unix_to_windows("cat")    -> "type"
 *   map_unix_to_windows("python") -> "python" (无映射，返回原值)
 */
const char *map_unix_to_windows(const char *unix_cmd)
{
	int i;
	
	/* NULL检查 */
	if (!unix_cmd)
		return NULL;
	
	/* 遍历映射表查找匹配项 */
	for (i = 0; mappings[i].unix_cmd != NULL; i++) {
		/* 找到匹配的命令 */
		if (strcmp(unix_cmd, mappings[i].unix_cmd) == 0)
			return mappings[i].windows_cmd;
	}
	
	/* 没有找到映射 - 返回原始命令 */
	/* 这允许Windows原生命令（如cmd, powershell等）直接使用 */
	return unix_cmd;
}
