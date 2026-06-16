/*
 * utils.c - 工具函数模块
 * 
 * 本文件提供各种通用的辅助函数，被内核的其他模块使用。
 * 
 * 主要功能:
 * - 字符串哈希计算（用于变量表的哈希表）
 * - 字符串复制（类似strdup）
 * - 通配符模式匹配
 * - 变量展开（$var, ${var}, $((expr))）
 * - 字符串处理工具
 */

#include "include/types.h"     /* 数据结构定义 */
#include "include/internal.h"  /* 内部接口定义 */
#include <stdlib.h>            /* malloc, free */
#include <string.h>            /* strlen, strcmp, strcpy */
#include <ctype.h>             /* isspace, isalnum, isdigit */
#include <stdio.h>             /* sprintf */

/*
 * hash_string - 计算字符串的哈希值
 * 
 * @str: 输入字符串
 * @返回值: 哈希值（0 到 HASH_TABLE_SIZE-1 范围内）
 * 
 * 使用djb2算法，这是一个简单但效果良好的字符串哈希算法。
 * 
 * 算法原理:
 * - 初始值为5381（一个质数）
 * - 对每个字符: hash = hash * 33 + c
 * - 最后对表大小取模
 */
unsigned int hash_string(const char *str)
{
	unsigned int hash = 5381;  /* djb2魔数 */
	int c;
	
	/* 遍历字符串中的每个字符 */
	while ((c = *str++))
		hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
	
	/* 对表大小取模，确保结果在有效范围内 */
	return hash % HASH_TABLE_SIZE;
}

/*
 * string_duplicate - 复制字符串（类似POSIX的strdup）
 * 
 * @str: 要复制的源字符串
 * @返回值: 新分配的字符串副本，失败返回NULL
 * 
 * 分配足够的内存来存储字符串副本（包括结尾的'\0'）。
 * 返回的字符串需要调用者使用free()释放。
 */
char *string_duplicate(const char *str)
{
	char *dup;
	size_t len;
	
	/* NULL检查 */
	if (!str)
		return NULL;
	
	/* 计算字符串长度（不包括'\0'） */
	len = strlen(str);
	
	/* 分配内存（+1 是为了存储结尾的'\0'） */
	dup = (char *)malloc(len + 1);
	if (!dup)
		return NULL;  /* 内存分配失败 */
	
	/* 复制字符串（包括结尾的'\0'） */
	memcpy(dup, str, len + 1);
	
	return dup;
}

/*
 * string_free - 释放字符串内存
 * 
 * @str: 要释放的字符串指针
 * 
 * 简单的free包装函数，增加了NULL检查。
 */
void string_free(char *str)
{
	if (str)
		free(str);
}

/*
 * string_match_pattern - 简单的通配符模式匹配
 * 
 * @str: 要匹配的字符串
 * @pattern: 模式字符串（支持*和?通配符）
 * @返回值: 匹配成功返回1，失败返回0
 * 
 * 通配符说明:
 * - *: 匹配任意数量的任意字符（包括0个）
 * - ?: 匹配任意单个字符
 * 
 * 算法: 双指针回溯法
 * 当遇到*时记录位置，匹配失败时回溯到*的位置重试。
 */
int string_match_pattern(const char *str, const char *pattern)
{
	const char *s = str;         /* 字符串指针 */
	const char *p = pattern;     /* 模式指针 */
	const char *star = NULL;     /* 记录最后一个*的位置 */
	const char *ss = NULL;       /* 记录遇到*时str的位置 */
	
	while (*s) {
		if (*p == '*') {
			/* 遇到*，记录位置并前进 */
			star = p++;
			ss = s;
		} else if (*p == *s || *p == '?') {
			/* 字符匹配或?通配符，两个指针都前进 */
			p++;
			s++;
		} else if (star) {
			/* 不匹配但之前有*，回溯 */
			p = star + 1;
			s = ++ss;
		} else {
			/* 不匹配且没有*可回溯，匹配失败 */
			return 0;
		}
	}
	
	/* 跳过模式末尾的* */
	while (*p == '*')
		p++;
	
	/* 如果模式也到达末尾，匹配成功 */
	return *p == '\0';
}

/*
 * eval_arithmetic - 简单的算术表达式求值器
 * 
 * @expr: 算术表达式字符串
 * @返回值: 计算结果
 * 
 * 支持的运算符: +, -, *, /, %
 * 
 * 注意: 这是一个简化实现，从左到右求值，不考虑优先级。
 * 例如: "1+2*3" 会被计算为 (1+2)*3=9，而不是 1+(2*3)=7
 */
static int eval_arithmetic(const char *expr)
{
	int values[64];      /* 操作数栈 */
	char ops[64];        /* 运算符栈 */
	int val_count = 0;   /* 操作数数量 */
	int op_count = 0;    /* 运算符数量 */
	const char *p = expr;
	
	/* 解析表达式 */
	while (*p) {
		/* 跳过空白 */
		while (*p == ' ' || *p == '\t')
			p++;
		
		if (!*p) break;
		
		/* 读取数字 */
		if (isdigit(*p)) {
			int num = 0;
			while (isdigit(*p)) {
				num = num * 10 + (*p - '0');
				p++;
			}
			if (val_count < 64)
				values[val_count++] = num;
		}
		
		/* 跳过空白 */
		while (*p == ' ' || *p == '\t')
			p++;
		
		/* 读取运算符 */
		if (*p == '+' || *p == '-' || *p == '*' || *p == '/' || *p == '%') {
			if (op_count < 64)
				ops[op_count++] = *p;
			p++;
		} else if (*p) {
			p++;  /* 跳过未知字符 */
		}
	}
	
	/* 从左到右求值 */
	if (val_count == 0) return 0;
	
	int result = values[0];
	int i;
	for (i = 0; i < op_count && i + 1 < val_count; i++) {
		switch (ops[i]) {
		case '+': result += values[i + 1]; break;
		case '-': result -= values[i + 1]; break;
		case '*': result *= values[i + 1]; break;
		case '/': 
			if (values[i + 1] != 0) 
				result /= values[i + 1]; 
			break;
		case '%': 
			if (values[i + 1] != 0) 
				result %= values[i + 1]; 
			break;
		}
	}
	
	return result;
}

/*
 * expand_variables - 展开字符串中的变量引用
 * 
 * @ctx: 执行上下文（用于查找变量值）
 * @str: 包含变量引用的源字符串
 * @返回值: 展开后的新字符串，需要调用者释放
 * 
 * 支持的变量语法:
 * - $var:      简单变量引用
 * - ${var}:    花括号变量引用
 * - $?:        上一个命令的退出码
 * - $((expr)): 算术表达式
 * 
 * 示例:
 *   输入: "Hello $name"，其中 name=World
 *   输出: "Hello World"
 */
char *expand_variables(struct exec_context *ctx, const char *str)
{
	char *result;
	const char *src = str;
	char *dst;
	char var_name[MAX_VAR_NAME];
	const char *var_value;
	size_t i;
	size_t result_size = MAX_VAR_VALUE * 2;  /* 足够大的缓冲区 */
	
	/* NULL检查 */
	if (!str)
		return NULL;
	
	/* 使用动态分配避免嵌套调用时的冲突 */
	result = (char *)malloc(result_size);
	if (!result)
		return NULL;
	
	dst = result;
	result[0] = '\0';
	
	/* 遍历源字符串 */
	while (*src && (size_t)(dst - result) < result_size - 1) {
		if (*src == '$') {
			/* 遇到变量引用 */
			src++;
			
			/* 处理特殊变量 $? (上一个命令的退出码) */
			if (*src == '?') {
				char exit_code[12];
				sprintf(exit_code, "%d", ctx->last_exit_code);
				var_value = exit_code;
				src++;
				
				/* 复制变量值到结果 */
				i = 0;
				while (var_value[i] && (size_t)(dst - result) < result_size - 1) {
					*dst++ = var_value[i++];
				}
				continue;
			}
			/* 处理算术表达式 $((expr)) */
			else if (*src == '(' && *(src + 1) == '(') {
				char expr[256];
				int depth = 2;  /* 括号深度 */
				src += 2;
				i = 0;
				
				/* 提取表达式直到匹配的 )) */
				while (*src && depth > 0 && i < 255) {
					if (*src == '(') depth++;
					else if (*src == ')') {
						depth--;
						if (depth == 0) break;
					}
					expr[i++] = *src++;
				}
				expr[i] = '\0';
				
				/* 跳过闭合的 )) */
				if (*src == ')') src++;
				if (*src == ')') src++;
				
				/* 首先展开表达式中的变量 */
				{
					char expanded_expr[256];
					const char *ep = expr;
					char *dp = expanded_expr;
					
					while (*ep && (dp - expanded_expr) < 255) {
						/* 跳过空白 */
						while (*ep == ' ' || *ep == '\t') {
							*dp++ = *ep++;
						}
						
						/* 变量名（不带$前缀） */
						if (isalpha(*ep) || *ep == '_') {
							char vname[MAX_VAR_NAME];
							const char *vval;
							int vi = 0;
							while ((isalnum(*ep) || *ep == '_') && vi < MAX_VAR_NAME - 1) {
								vname[vi++] = *ep++;
							}
							vname[vi] = '\0';
							vval = var_table_get(ctx->vars, vname);
							if (vval) {
								while (*vval && (dp - expanded_expr) < 255)
									*dp++ = *vval++;
							} else {
								/* 变量不存在，使用0 */
								*dp++ = '0';
							}
						} else if (*ep == '$') {
							/* 处理表达式中的$var */
							ep++;
							if (isalpha(*ep) || *ep == '_') {
								char vname[MAX_VAR_NAME];
								const char *vval;
								int vi = 0;
								while ((isalnum(*ep) || *ep == '_') && vi < MAX_VAR_NAME - 1) {
									vname[vi++] = *ep++;
								}
								vname[vi] = '\0';
								vval = var_table_get(ctx->vars, vname);
								if (vval) {
									while (*vval && (dp - expanded_expr) < 255)
										*dp++ = *vval++;
								} else {
									*dp++ = '0';
								}
							}
						} else {
							*dp++ = *ep++;
						}
					}
					*dp = '\0';
					
					/* 求值算术表达式 */
					{
						char num_str[32];
						int num_result = eval_arithmetic(expanded_expr);
						sprintf(num_str, "%d", num_result);
						var_value = num_str;
						
						/* 复制结果到输出 */
						i = 0;
						while (var_value[i] && (size_t)(dst - result) < result_size - 1) {
							*dst++ = var_value[i++];
						}
					}
				}
				continue;
			}
			/* 处理 ${var} 语法 */
			else if (*src == '{') {
				src++;
				i = 0;
				/* 读取变量名直到 } */
				while (*src && *src != '}' && i < (size_t)(MAX_VAR_NAME - 1)) {
					var_name[i++] = *src++;
				}
				var_name[i] = '\0';
				if (*src == '}')
					src++;
			}
			/* 处理 $var 语法 */
			else if (isalnum(*src) || *src == '_') {
				i = 0;
				/* 读取变量名（字母、数字、下划线） */
				while ((isalnum(*src) || *src == '_') && 
				   i < (size_t)(MAX_VAR_NAME - 1)) {
					var_name[i++] = *src++;
				}
				var_name[i] = '\0';
			}
			else {
				/* 单独的$，保持原样 */
				*dst++ = '$';
				continue;
			}
			
			/* 查找变量值 */
			var_value = var_table_get(ctx->vars, var_name);
			if (var_value) {
				/* 复制变量值到结果 */
				i = 0;
				while (var_value[i] && (size_t)(dst - result) < result_size - 1) {
					*dst++ = var_value[i++];
				}
			}
		} else {
			/* 普通字符，直接复制 */
			*dst++ = *src++;
		}
	}
	
	*dst = '\0';  /* 字符串结尾 */
	/* 返回动态分配的缓冲区 - 调用者负责释放 */
	return result;
}

/*
 * string_trim - 去除字符串两端的空白（原地修改）
 * 
 * @str: 要处理的字符串
 * 
 * 去除字符串开头和结尾的空白字符（空格、制表符、换行等）。
 */
void string_trim(char *str)
{
	char *end;
	
	/* NULL或空字符串检查 */
	if (!str || !*str)
		return;
	
	/* 去除开头的空白 */
	while (isspace((unsigned char)*str))
		str++;
	
	/* 全是空白的情况 */
	if (*str == 0)
		return;
	
	/* 去除结尾的空白 */
	end = str + strlen(str) - 1;
	while (end > str && isspace((unsigned char)*end))
		end--;
	
	/* 添加新的字符串结尾 */
	end[1] = '\0';
}

/*
 * string_split - 按分隔符分割字符串
 * 
 * @str: 要分割的字符串
 * @delim: 分隔符字符
 * @result: 输出数组，存储分割后的子字符串
 * @max_parts: 最大分割数量
 * @返回值: 实际分割的数量
 * 
 * 每个子字符串都是新分配的内存，调用者需要逐个释放。
 */
int string_split(const char *str, char delim, char **result, int max_parts)
{
	const char *start = str;
	const char *end;
	int count = 0;
	int len;
	
	/* 参数检查 */
	if (!str || !result)
		return 0;
	
	while (*start && count < max_parts) {
		/* 跳过开头的分隔符 */
		while (*start == delim)
			start++;
		
		/* 检查是否到达结尾 */
		if (!*start)
			break;
		
		/* 找到当前token的结尾 */
		end = start;
		while (*end && *end != delim)
			end++;
		
		/* 复制token */
		len = end - start;
		result[count] = (char *)malloc(len + 1);
		if (result[count]) {
			memcpy(result[count], start, len);
			result[count][len] = '\0';
			count++;
		}
		
		start = end;
	}
	
	return count;
}
