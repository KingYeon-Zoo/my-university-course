/*
 * shell_core.c - Shell内核核心实现模块
 * 
 * 本文件实现了shell内核的公共API，是所有功能模块的入口点。
 * 它连接词法分析器、语法分析器和执行器，对外提供统一的接口。
 * 
 * 主要职责:
 * - 初始化和销毁shell环境
 * - 执行命令行和脚本文件
 * - 管理变量
 * - 提供调试功能
 * 
 * 架构概述:
 *   用户代码
 *      |
 *      v
 * [shell_api.h] - 公共API接口
 *      |
 *      v
 * [shell_core.c] - 核心实现（本文件）
 *      |
 *      +---> [lexer.c] - 词法分析
 *      |
 *      +---> [parser.c] - 语法分析
 *      |
 *      +---> [executor.c] - 执行
 *      |
 *      +---> [variable.c] - 变量管理
 *      |
 *      +---> [builtin_cmd.c] - 内置命令
 */

#include "include/shell_api.h"  /* 公共API定义 */
#include "include/types.h"      /* 数据结构定义 */
#include "include/internal.h"   /* 内部接口定义 */
#include <stdlib.h>             /* malloc, free */
#include <string.h>             /* strcmp, strncpy, strlen */
#include <stdio.h>              /* snprintf */
#include <windows.h>            /* Windows API */
#include <direct.h>             /* _getcwd */

/*
 * Shell上下文结构体（内部使用）
 * 
 * 包含shell运行所需的所有状态信息。
 * 对外通过不透明指针shell_context_t暴露。
 */
struct shell_context {
	struct exec_context exec_ctx;    /* 执行上下文（必须是第一个成员） */
	shell_callbacks_t callbacks;     /* 回调函数集合 */
};

/*
 * shell_output - 全局输出回调函数
 * 
 * @ctx: 执行上下文指针
 * @output: 要输出的文本
 * 
 * 将输出文本传递给用户注册的回调函数。
 * 被其他模块（如builtin_cmd.c）调用。
 */
void shell_output(struct exec_context *ctx, const char *output)
{
	struct shell_context *shell_ctx;
	
	/* 参数检查 */
	if (!ctx || !output)
		return;
	
	/* 从执行上下文获取shell上下文 */
	/* 注意: exec_ctx是shell_context的第一个成员，所以可以直接转换 */
	shell_ctx = (struct shell_context *)((char *)ctx - 
	            offsetof(struct shell_context, exec_ctx));
	
	/* 调用用户的输出回调函数 */
	if (shell_ctx->callbacks.output_cb)
		shell_ctx->callbacks.output_cb(shell_ctx->callbacks.user_data, output);
}

/*
 * shell_error - 全局错误回调函数
 * 
 * @ctx: 执行上下文指针
 * @error: 错误信息
 * @line: 错误发生的行号
 * 
 * 将错误信息传递给用户注册的回调函数。
 */
void shell_error(struct exec_context *ctx, const char *error, int line)
{
	struct shell_context *shell_ctx;
	
	/* 参数检查 */
	if (!ctx || !error)
		return;
	
	/* 从执行上下文获取shell上下文 */
	shell_ctx = (struct shell_context *)((char *)ctx - 
	            offsetof(struct shell_context, exec_ctx));
	
	/* 调用用户的错误回调函数 */
	if (shell_ctx->callbacks.error_cb)
		shell_ctx->callbacks.error_cb(shell_ctx->callbacks.user_data, 
		                              error, line);
}

/*
 * shell_init - 初始化shell环境
 * 
 * @callbacks: 用户提供的回调函数结构
 * @返回值: 成功返回shell上下文句柄，失败返回NULL
 * 
 * 初始化过程:
 * 1. 分配shell上下文结构
 * 2. 创建变量表
 * 3. 获取并设置当前工作目录
 * 4. 保存回调函数
 */
shell_context_t shell_init(const shell_callbacks_t *callbacks)
{
	struct shell_context *ctx;
	char cwd[MAX_PATH_LEN];
	
	/* 回调函数不能为空 */
	if (!callbacks)
		return NULL;
	
	/* 分配shell上下文 */
	ctx = (struct shell_context *)malloc(sizeof(struct shell_context));
	if (!ctx)
		return NULL;
	
	/* 创建变量表 */
	ctx->exec_ctx.vars = var_table_create();
	if (!ctx->exec_ctx.vars) {
		free(ctx);
		return NULL;
	}
	
	/* 初始化执行上下文 */
	ctx->exec_ctx.last_exit_code = 0;   /* 上一个命令的退出码 */
	ctx->exec_ctx.should_exit = 0;      /* 退出标志 */
	ctx->exec_ctx.callback_data = NULL; /* 用户数据 */
	
	/* 获取并设置当前工作目录 */
	if (_getcwd(cwd, sizeof(cwd))) {
		strncpy(ctx->exec_ctx.current_dir, cwd, MAX_PATH_LEN - 1);
		ctx->exec_ctx.current_dir[MAX_PATH_LEN - 1] = '\0';
		var_table_set(ctx->exec_ctx.vars, "PWD", cwd);
	} else {
		strcpy(ctx->exec_ctx.current_dir, ".");
	}
	
	/* 保存回调函数 */
	ctx->callbacks = *callbacks;
	
	return (shell_context_t)ctx;
}

/*
 * shell_exec_line - 执行单行shell命令
 * 
 * @ctx: shell上下文句柄
 * @line: 命令行字符串
 * @返回值: 命令的退出码
 * 
 * 执行流程:
 * 1. 跳过空行和注释
 * 2. 词法分析 - 生成Token链表
 * 3. 语法分析 - 生成AST
 * 4. 执行 - 遍历并执行AST
 * 5. 清理资源
 */
int shell_exec_line(shell_context_t ctx, const char *line)
{
	struct shell_context *shell_ctx = (struct shell_context *)ctx;
	struct token *tokens;
	struct ast_node *ast;
	int error_line = 0;
	int result;
	
	/* 参数检查 */
	if (!ctx || !line)
		return -1;
	
	/* 跳过空行和注释 */
	{
		const char *p = line;
		/* 跳过开头的空白 */
		while (*p && (*p == ' ' || *p == '\t'))
			p++;
		/* 检查是否为空行、注释或只有换行符 */
		if (!*p || *p == '#' || *p == '\n')
			return 0;
	}
	
	/* 词法分析 */
	tokens = lexer_tokenize(line, &error_line);
	if (!tokens) {
		shell_error(&shell_ctx->exec_ctx, "Lexical error", error_line);
		return -1;
	}
	
	/* 语法分析 */
	ast = parser_parse(tokens, &error_line);
	token_list_destroy(tokens);  /* Token链表不再需要 */
	
	if (!ast) {
		if (error_line > 0) {
			shell_error(&shell_ctx->exec_ctx, "Syntax error", error_line);
		}
		return -1;
	}
	
	/* 执行AST */
	result = executor_run(&shell_ctx->exec_ctx, ast);
	
	/* 清理AST */
	ast_destroy(ast);
	
	return result;
}

/*
 * shell_exec_file - 执行shell脚本文件
 * 
 * @ctx: shell上下文句柄
 * @filepath: 脚本文件路径
 * @返回值: 脚本的退出码
 * 
 * 执行流程:
 * 1. 打开并读取脚本文件
 * 2. 切换到脚本所在目录（相对路径能正确解析）
 * 3. 解析并执行整个脚本
 * 4. 恢复原来的工作目录
 * 5. 清理资源
 */
int shell_exec_file(shell_context_t ctx, const char *filepath)
{
	struct shell_context *shell_ctx = (struct shell_context *)ctx;
	HANDLE file;
	DWORD file_size, bytes_read;
	char *content;
	int result = 0;
	char old_dir[MAX_PATH_LEN];    /* 保存原来的目录 */
	char script_dir[MAX_PATH_LEN]; /* 脚本所在目录 */
	char *last_slash;
	int changed_dir = 0;
	
	/* 参数检查 */
	if (!ctx || !filepath)
		return -1;
	
	/* 先打开文件（在切换目录之前） */
	file = CreateFileA(filepath, GENERIC_READ, FILE_SHARE_READ, NULL,
	                  OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
	if (file == INVALID_HANDLE_VALUE) {
		shell_error(&shell_ctx->exec_ctx, "Cannot open file", 0);
		return -1;
	}
	
	/* 获取文件大小 */
	file_size = GetFileSize(file, NULL);
	if (file_size == INVALID_FILE_SIZE) {
		CloseHandle(file);
		return -1;
	}
	
	/* 分配缓冲区 */
	content = (char *)malloc(file_size + 1);
	if (!content) {
		CloseHandle(file);
		return -1;
	}
	
	/* 读取文件内容 */
	if (!ReadFile(file, content, file_size, &bytes_read, NULL)) {
		free(content);
		CloseHandle(file);
		return -1;
	}
	content[bytes_read] = '\0';  /* 添加字符串结尾 */
	
	CloseHandle(file);
	
	/* 切换到脚本所在目录 */
	if (_getcwd(old_dir, sizeof(old_dir))) {
		/* 从文件路径提取目录部分 */
		strncpy(script_dir, filepath, MAX_PATH_LEN - 1);
		script_dir[MAX_PATH_LEN - 1] = '\0';
		
		/* 查找最后一个斜杠（支持/和\） */
		last_slash = NULL;
		{
			char *p = script_dir;
			while (*p) {
				if (*p == '/' || *p == '\\')
					last_slash = p;
				p++;
			}
		}
		
		/* 如果路径包含目录，切换到该目录 */
		if (last_slash) {
			*last_slash = '\0';
			if (_chdir(script_dir) == 0) {
				changed_dir = 1;
				/* 临时更新PWD变量 */
				if (_getcwd(script_dir, sizeof(script_dir))) {
					var_table_set(shell_ctx->exec_ctx.vars, "PWD", script_dir);
					strncpy(shell_ctx->exec_ctx.current_dir, script_dir, MAX_PATH_LEN - 1);
					shell_ctx->exec_ctx.current_dir[MAX_PATH_LEN - 1] = '\0';
				}
			}
		}
	}
	
	/* 解析并执行整个文件内容 */
	{
		struct token *tokens;
		struct ast_node *ast;
		int error_line = 0;
		
		/* 词法分析整个文件 */
		tokens = lexer_tokenize(content, &error_line);
		if (!tokens) {
			shell_error(&shell_ctx->exec_ctx, "Lexical error", error_line);
			free(content);
			return -1;
		}
		
		/* 语法分析整个文件 */
		ast = parser_parse(tokens, &error_line);
		token_list_destroy(tokens);
		
		if (!ast) {
			if (error_line > 0) {
				shell_error(&shell_ctx->exec_ctx, "Syntax error", error_line);
			}
			free(content);
			return -1;
		}
		
		/* 执行AST */
		result = executor_run(&shell_ctx->exec_ctx, ast);
		
		/* 清理AST */
		ast_destroy(ast);
	}
	
	free(content);
	
	/* 恢复原来的工作目录 */
	if (changed_dir) {
		_chdir(old_dir);
		/* 恢复PWD变量 */
		var_table_set(shell_ctx->exec_ctx.vars, "PWD", old_dir);
		strncpy(shell_ctx->exec_ctx.current_dir, old_dir, MAX_PATH_LEN - 1);
		shell_ctx->exec_ctx.current_dir[MAX_PATH_LEN - 1] = '\0';
	}
	
	return result;
}

/*
 * shell_get_var - 获取变量值
 * 
 * @ctx: shell上下文句柄
 * @name: 变量名
 * @返回值: 变量值指针，不存在返回NULL
 */
const char *shell_get_var(shell_context_t ctx, const char *name)
{
	struct shell_context *shell_ctx = (struct shell_context *)ctx;
	
	if (!ctx || !name)
		return NULL;
	
	return var_table_get(shell_ctx->exec_ctx.vars, name);
}

/*
 * shell_set_var - 设置变量值
 * 
 * @ctx: shell上下文句柄
 * @name: 变量名
 * @value: 变量值
 * @返回值: 成功返回0，失败返回-1
 */
int shell_set_var(shell_context_t ctx, const char *name, const char *value)
{
	struct shell_context *shell_ctx = (struct shell_context *)ctx;
	
	if (!ctx || !name || !value)
		return -1;
	
	return var_table_set(shell_ctx->exec_ctx.vars, name, value);
}

/*
 * shell_get_exit_code - 获取上一个命令的退出码
 * 
 * @ctx: shell上下文句柄
 * @返回值: 退出码
 */
int shell_get_exit_code(shell_context_t ctx)
{
	struct shell_context *shell_ctx = (struct shell_context *)ctx;
	
	if (!ctx)
		return -1;
	
	return shell_ctx->exec_ctx.last_exit_code;
}

/*
 * shell_should_exit - 检查shell是否应该退出
 * 
 * @ctx: shell上下文句柄
 * @返回值: 应该退出返回1，否则返回0
 */
int shell_should_exit(shell_context_t ctx)
{
	struct shell_context *shell_ctx = (struct shell_context *)ctx;
	
	if (!ctx)
		return 0;
	
	return shell_ctx->exec_ctx.should_exit;
}

/*
 * shell_destroy - 销毁shell环境
 * 
 * @ctx: shell上下文句柄
 * 
 * 释放所有分配的资源。
 */
void shell_destroy(shell_context_t ctx)
{
	struct shell_context *shell_ctx = (struct shell_context *)ctx;
	
	if (!ctx)
		return;
	
	/* 销毁变量表 */
	if (shell_ctx->exec_ctx.vars)
		var_table_destroy(shell_ctx->exec_ctx.vars);
	
	/* 释放上下文结构 */
	free(shell_ctx);
}

/*============================================================================
 * 调试函数实现
 * 用于开发和调试目的，可以查看词法分析和语法分析的中间结果。
 *============================================================================*/

/*
 * shell_debug_tokenize - 词法分析调试
 * 
 * @ctx: shell上下文句柄
 * @line: 输入行
 * @token_count: 输出Token数量
 * @返回值: Token描述字符串数组
 */
char **shell_debug_tokenize(shell_context_t ctx, const char *line, 
                            int *token_count)
{
	struct token *tokens, *tok;
	char **result;
	int count = 0;
	int i;
	
	if (!ctx || !line || !token_count)
		return NULL;
	
	/* 执行词法分析 */
	tokens = lexer_tokenize(line, NULL);
	if (!tokens)
		return NULL;
	
	/* 计算Token数量 */
	tok = tokens;
	while (tok) {
		count++;
		tok = tok->next;
	}
	
	/* 分配结果数组 */
	result = (char **)malloc(sizeof(char *) * count);
	if (!result) {
		token_list_destroy(tokens);
		return NULL;
	}
	
	/* 填充结果数组 */
	tok = tokens;
	for (i = 0; i < count; i++) {
		char buffer[512];
		snprintf(buffer, sizeof(buffer), "[%d] Type=%d Value='%s'",
		        tok->line, tok->type, tok->value);
		result[i] = string_duplicate(buffer);
		tok = tok->next;
	}
	
	token_list_destroy(tokens);
	*token_count = count;
	return result;
}

/*
 * shell_debug_parse - 语法分析调试
 * 
 * @ctx: shell上下文句柄
 * @line: 输入行
 * @返回值: AST描述字符串
 */
char *shell_debug_parse(shell_context_t ctx, const char *line)
{
	struct token *tokens;
	struct ast_node *ast;
	char *result;
	
	if (!ctx || !line)
		return NULL;
	
	/* 词法分析 */
	tokens = lexer_tokenize(line, NULL);
	if (!tokens)
		return NULL;
	
	/* 语法分析 */
	ast = parser_parse(tokens, NULL);
	token_list_destroy(tokens);
	
	if (!ast)
		return NULL;
	
	/* 简单的AST描述 */
	result = string_duplicate("AST created successfully");
	ast_destroy(ast);
	
	return result;
}

/*
 * shell_debug_free_tokens - 释放Token调试信息
 * 
 * @tokens: Token字符串数组
 * @count: Token数量
 */
void shell_debug_free_tokens(char **tokens, int count)
{
	int i;
	
	if (!tokens)
		return;
	
	for (i = 0; i < count; i++)
		if (tokens[i])
			free(tokens[i]);
	
	free(tokens);
}

/*
 * shell_debug_free_ast - 释放AST调试信息
 * 
 * @ast_str: AST描述字符串
 */
void shell_debug_free_ast(char *ast_str)
{
	if (ast_str)
		free(ast_str);
}
