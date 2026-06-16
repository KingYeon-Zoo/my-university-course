/*
 * variable.c - 变量表实现模块
 * 
 * 本文件实现了shell变量的存储和管理功能。
 * 
 * 实现方式: 哈希表
 * - 使用链地址法解决哈希冲突
 * - 支持设置、获取、删除变量
 * - 支持导出变量为环境变量
 * 
 * 变量类型:
 * - 局部变量: 只在当前shell进程中可见
 * - 导出变量: 会传递给子进程（环境变量）
 * 
 * 特殊变量:
 * - PWD: 当前工作目录
 * - HOME: 用户主目录
 * - OLDPWD: 上一个工作目录
 * - ?: 上一个命令的退出码（在expand_variables中处理）
 */

#include "include/types.h"     /* 数据结构定义 */
#include "include/internal.h"  /* 内部接口定义 */
#include <stdlib.h>            /* malloc, free */
#include <string.h>            /* strcmp, strncpy */
#include <stdio.h>             /* sprintf */
#include <windows.h>           /* GetEnvironmentVariable, SetEnvironmentVariable */

/*
 * var_table_create - 创建一个新的变量表
 * 
 * @返回值: 成功返回变量表指针，失败返回NULL
 * 
 * 创建并初始化一个空的哈希表。
 * 默认设置PWD和HOME变量。
 */
struct var_table *var_table_create(void)
{
	struct var_table *table;
	int i;
	
	/* 分配变量表结构 */
	table = (struct var_table *)malloc(sizeof(struct var_table));
	if (!table)
		return NULL;
	
	/* 初始化所有桶为空 */
	for (i = 0; i < HASH_TABLE_SIZE; i++)
		table->buckets[i] = NULL;
	
	/* 初始化变量计数 */
	table->count = 0;
	
	/* 设置一些默认变量 */
	var_table_set(table, "PWD", ".");    /* 当前目录 */
	var_table_set(table, "HOME", ".");   /* 主目录 */
	
	return table;
}

/*
 * var_table_destroy - 销毁变量表并释放所有资源
 * 
 * @table: 要销毁的变量表指针
 * 
 * 遍历所有桶和链表，释放每个变量条目。
 */
void var_table_destroy(struct var_table *table)
{
	struct var_entry *entry, *next;
	int i;
	
	/* NULL检查 */
	if (!table)
		return;
	
	/* 遍历所有桶 */
	for (i = 0; i < HASH_TABLE_SIZE; i++) {
		entry = table->buckets[i];
		/* 释放桶中的链表 */
		while (entry) {
			next = entry->next;
			free(entry);
			entry = next;
		}
	}
	
	/* 释放变量表结构本身 */
	free(table);
}

/*
 * var_table_set - 设置变量的值
 * 
 * @table: 变量表指针
 * @name: 变量名
 * @value: 变量值
 * @返回值: 成功返回0，失败返回-1
 * 
 * 如果变量已存在，更新其值。
 * 如果变量不存在，创建新条目。
 */
int var_table_set(struct var_table *table, const char *name, const char *value)
{
	unsigned int hash;
	struct var_entry *entry;
	
	/* 参数检查 */
	if (!table || !name || !value)
		return -1;
	
	/* 检查名称和值长度 */
	if (strlen(name) >= MAX_VAR_NAME || strlen(value) >= MAX_VAR_VALUE)
		return -1;
	
	/* 计算哈希值 */
	hash = hash_string(name);
	
	/* 在链表中搜索现有条目 */
	entry = table->buckets[hash];
	while (entry) {
		if (strcmp(entry->name, name) == 0) {
			/* 找到现有变量，更新值 */
			strncpy(entry->value, value, MAX_VAR_VALUE - 1);
			entry->value[MAX_VAR_VALUE - 1] = '\0';
			return 0;
		}
		entry = entry->next;
	}
	
	/* 变量不存在，创建新条目 */
	entry = (struct var_entry *)malloc(sizeof(struct var_entry));
	if (!entry)
		return -1;
	
	/* 设置变量名 */
	strncpy(entry->name, name, MAX_VAR_NAME - 1);
	entry->name[MAX_VAR_NAME - 1] = '\0';
	
	/* 设置变量值 */
	strncpy(entry->value, value, MAX_VAR_VALUE - 1);
	entry->value[MAX_VAR_VALUE - 1] = '\0';
	
	/* 初始化为非导出状态 */
	entry->exported = 0;
	
	/* 使用头插法将新条目插入链表 */
	entry->next = table->buckets[hash];
	table->buckets[hash] = entry;
	
	/* 增加变量计数 */
	table->count++;
	
	return 0;
}

/*
 * var_table_get - 获取变量的值
 * 
 * @table: 变量表指针
 * @name: 变量名
 * @返回值: 成功返回变量值的指针，变量不存在返回NULL
 * 
 * 首先在变量表中查找，如果没找到则尝试从系统环境变量获取。
 */
const char *var_table_get(struct var_table *table, const char *name)
{
	unsigned int hash;
	struct var_entry *entry;
	
	/* 参数检查 */
	if (!table || !name)
		return NULL;
	
	/* 特殊变量 $? 在这里不处理（由expand_variables处理） */
	if (strcmp(name, "?") == 0) {
		static char exit_code_str[12];
		/* 返回空字符串，实际值在expand_variables中设置 */
		return exit_code_str;
	}
	
	/* 计算哈希值 */
	hash = hash_string(name);
	
	/* 在链表中搜索 */
	entry = table->buckets[hash];
	while (entry) {
		if (strcmp(entry->name, name) == 0)
			return entry->value;  /* 找到了 */
		entry = entry->next;
	}
	
	/* 变量表中没找到，尝试从系统环境变量获取 */
	{
		static char env_value[MAX_VAR_VALUE];
		DWORD result = GetEnvironmentVariableA(name, env_value, 
		                                       sizeof(env_value));
		if (result > 0 && result < sizeof(env_value))
			return env_value;
	}
	
	return NULL;  /* 变量不存在 */
}

/*
 * var_table_unset - 删除一个变量
 * 
 * @table: 变量表指针
 * @name: 要删除的变量名
 * @返回值: 成功返回0，变量不存在返回-1
 * 
 * 从哈希表中移除指定的变量条目。
 */
int var_table_unset(struct var_table *table, const char *name)
{
	unsigned int hash;
	struct var_entry *entry, *prev;
	
	/* 参数检查 */
	if (!table || !name)
		return -1;
	
	/* 计算哈希值 */
	hash = hash_string(name);
	
	/* 在链表中搜索 */
	entry = table->buckets[hash];
	prev = NULL;
	
	while (entry) {
		if (strcmp(entry->name, name) == 0) {
			/* 找到了，从链表中移除 */
			if (prev)
				prev->next = entry->next;
			else
				table->buckets[hash] = entry->next;
			
			/* 释放条目 */
			free(entry);
			table->count--;
			return 0;
		}
		prev = entry;
		entry = entry->next;
	}
	
	return -1;  /* 变量不存在 */
}

/*
 * var_table_export - 将变量导出为环境变量
 * 
 * @table: 变量表指针
 * @name: 要导出的变量名
 * 
 * 导出的变量会传递给子进程。
 * 使用Windows的SetEnvironmentVariable API。
 */
void var_table_export(struct var_table *table, const char *name)
{
	unsigned int hash;
	struct var_entry *entry;
	
	/* 参数检查 */
	if (!table || !name)
		return;
	
	/* 计算哈希值 */
	hash = hash_string(name);
	
	/* 在链表中搜索 */
	entry = table->buckets[hash];
	while (entry) {
		if (strcmp(entry->name, name) == 0) {
			/* 找到变量，标记为已导出 */
			entry->exported = 1;
			/* 设置为系统环境变量 */
			SetEnvironmentVariableA(name, entry->value);
			return;
		}
		entry = entry->next;
	}
}
