/*
 * executor.c - AST执行引擎模块
 * 
 * 本文件实现了抽象语法树的遍历和执行功能。
 * 
 * 执行器是解释器的核心，负责:
 * 1. 遍历抽象语法树(AST)
 * 2. 根据节点类型执行相应的操作
 * 3. 处理控制流（if/while/for）
 * 4. 管理命令执行和管道
 * 5. 处理变量赋值
 * 
 * 执行流程:
 *   词法分析 -> 语法分析 -> AST -> 执行器 -> 结果
 * 
 * 支持的执行模式:
 * - 简单命令: 内置命令在shell进程内执行，外部命令创建子进程
 * - 管道: 创建多个进程，用管道连接stdin/stdout
 * - 控制流: 递归执行子节点
 * - 变量赋值: 更新变量表
 */

#include "include/types.h"     /* 数据结构定义 */
#include "include/internal.h"  /* 内部接口定义 */
#include <stdlib.h>            /* malloc, free */
#include <string.h>            /* strcmp, strncpy */
#include <windows.h>           /* Windows API */
#include <io.h>                /* 文件I/O */

/* 外部回调函数 - 在shell_core.c中定义 */
extern void shell_output(struct exec_context *ctx, const char *output);
extern void shell_error(struct exec_context *ctx, const char *error, int line);

/*
 * execute_windows_command - 执行Windows外部命令
 * 
 * @ctx: 执行上下文
 * @cmd_line: 完整的命令行字符串
 * @返回值: 命令的退出码，失败返回-1
 * 
 * 使用Windows CreateProcess API创建子进程执行命令。
 * 等待命令完成后返回其退出码。
 */
static int execute_windows_command(struct exec_context *ctx, 
                                   const char *cmd_line)
{
	STARTUPINFOA si;          /* 启动信息 */
	PROCESS_INFORMATION pi;   /* 进程信息 */
	DWORD exit_code = 0;      /* 退出码 */
	
	(void)ctx;  /* 抑制未使用参数警告 */
	
	/* 初始化启动信息结构 */
	ZeroMemory(&si, sizeof(si));
	si.cb = sizeof(si);
	
	/* 初始化进程信息结构 */
	ZeroMemory(&pi, sizeof(pi));
	
	/* 创建子进程 */
	if (!CreateProcessA(
			NULL,             /* 应用程序名（NULL表示从命令行解析） */
			(LPSTR)cmd_line,  /* 命令行 */
			NULL,             /* 进程安全属性 */
			NULL,             /* 线程安全属性 */
			TRUE,             /* 继承句柄 */
			0,                /* 创建标志 */
			NULL,             /* 环境变量（NULL表示继承） */
			NULL,             /* 当前目录（NULL表示继承） */
			&si,              /* 启动信息 */
			&pi)) {           /* 进程信息 */
		return -1;  /* 创建失败 */
	}
	
	/* 等待进程结束 */
	WaitForSingleObject(pi.hProcess, INFINITE);
	
	/* 获取退出码 */
	GetExitCodeProcess(pi.hProcess, &exit_code);
	
	/* 关闭进程和线程句柄 */
	CloseHandle(pi.hProcess);
	CloseHandle(pi.hThread);
	
	return (int)exit_code;
}

/*
 * build_command_line - 从参数数组构建命令行字符串
 * 
 * @cmd_line: 输出缓冲区
 * @max_len: 缓冲区最大长度
 * @args: 参数数组
 * @argc: 参数数量
 * 
 * 将参数数组连接成单个命令行字符串。
 * 如果参数包含空格，会用引号包围。
 */
static void build_command_line(char *cmd_line, int max_len, 
                              char **args, int argc)
{
	int i;
	int pos = 0;
	
	cmd_line[0] = '\0';
	
	for (i = 0; i < argc && pos < max_len - 1; i++) {
		/* 添加空格分隔符（第一个参数前不加） */
		if (i > 0) {
			cmd_line[pos++] = ' ';
		}
		
		/* 检查参数是否需要用引号包围（包含空格或制表符） */
		if (strchr(args[i], ' ') || strchr(args[i], '\t')) {
			cmd_line[pos++] = '"';
			strncat(cmd_line + pos, args[i], max_len - pos - 2);
			pos += strlen(args[i]);
			if (pos < max_len - 1)
				cmd_line[pos++] = '"';
		} else {
			strncat(cmd_line + pos, args[i], max_len - pos - 1);
			pos += strlen(args[i]);
		}
	}
	
	cmd_line[pos] = '\0';
}

/* 前向声明 - shell_exec_file在shell_core.c中定义 */
extern int shell_exec_file(void *ctx, const char *filepath);

/*
 * get_shell_context_from_exec - 从执行上下文获取shell上下文
 * 
 * @exec_ctx: 执行上下文指针
 * @返回值: shell上下文指针
 * 
 * 说明: shell_context结构体中exec_context是第一个成员，
 * 因此两者的地址相同，可以直接转换。
 */
static void *get_shell_context_from_exec(struct exec_context *exec_ctx)
{
	/* 
	 * Shell上下文结构（在shell_core.c中定义）:
	 * struct shell_context {
	 *     struct exec_context exec_ctx;  <- 偏移量为0
	 *     shell_callbacks_t callbacks;
	 * };
	 * 所以shell_context指针等于exec_ctx指针
	 */
	return (void *)exec_ctx;
}

/*
 * is_shell_script - 检查文件是否是shell脚本
 * 
 * @filename: 文件名
 * @返回值: 是脚本返回1，否则返回0
 * 
 * 通过检查文件扩展名(.sh)来判断。
 */
static int is_shell_script(const char *filename)
{
	size_t len;
	
	if (!filename)
		return 0;
	
	len = strlen(filename);
	if (len < 4)
		return 0;
	
	/* 检查 .sh 扩展名 */
	if (strcmp(filename + len - 3, ".sh") == 0)
		return 1;
	
	return 0;
}

/*
 * file_exists_executor - 检查文件是否存在
 * 
 * @filepath: 文件路径
 * @返回值: 存在返回1，不存在返回0
 */
static int file_exists_executor(const char *filepath)
{
	DWORD attrs = GetFileAttributesA(filepath);
	return (attrs != INVALID_FILE_ATTRIBUTES && 
	        !(attrs & FILE_ATTRIBUTE_DIRECTORY));
}

/*
 * executor_run_command - 执行单个命令
 * 
 * @ctx: 执行上下文
 * @cmd: 命令节点
 * @返回值: 命令的退出码
 * 
 * 执行流程:
 * 1. 展开所有参数中的变量引用
 * 2. 检查是否是内置命令
 * 3. 检查是否是.sh脚本文件
 * 4. 如果都不是，尝试作为外部命令执行
 * 5. 清理展开的参数内存
 */
int executor_run_command(struct exec_context *ctx, struct cmd_node *cmd)
{
	char cmd_line[4096];
	char *expanded_args[MAX_CMD_ARGS];  /* 展开变量后的参数 */
	int i;
	int result;
	const char *windows_cmd;
	
	/* 参数检查 */
	if (!cmd || !cmd->name)
		return -1;
	
	/* 初始化展开参数数组为NULL（安全起见） */
	memset(expanded_args, 0, sizeof(expanded_args));
	
	/* 展开所有参数中的变量引用 */
	for (i = 0; i < cmd->argc; i++) {
		expanded_args[i] = expand_variables(ctx, cmd->args[i]);
		if (!expanded_args[i])
			expanded_args[i] = string_duplicate(cmd->args[i]);
		
		/* 如果展开仍然失败，清理并返回错误 */
		if (!expanded_args[i]) {
			int j;
			for (j = 0; j < i; j++) {
				if (expanded_args[j])
					free(expanded_args[j]);
			}
			return -1;
		}
	}
	
	/* 检查是否是内置命令 */
	if (is_builtin(expanded_args[0])) {
		/* 执行内置命令 */
		result = execute_builtin(ctx, expanded_args[0], 
		                       expanded_args, cmd->argc);
	} else if (is_shell_script(expanded_args[0]) && file_exists_executor(expanded_args[0])) {
		/* 如果是存在的.sh文件，作为脚本执行 */
		void *shell_ctx = get_shell_context_from_exec(ctx);
		result = shell_exec_file(shell_ctx, expanded_args[0]);
	} else {
		/* 外部命令 - 尝试映射Unix命令到Windows命令 */
		windows_cmd = map_unix_to_windows(expanded_args[0]);
		
		/* 构建命令行 */
		if (windows_cmd != expanded_args[0]) {
			/* 命令被映射 */
			char temp_args[MAX_CMD_ARGS][MAX_TOKEN_LEN];
			int temp_argc = 0;
			
			/* 分割映射后的命令（可能包含空格） */
			strncpy(temp_args[temp_argc++], windows_cmd, MAX_TOKEN_LEN - 1);
			
			/* 添加其余参数 */
			for (i = 1; i < cmd->argc && temp_argc < MAX_CMD_ARGS; i++) {
				strncpy(temp_args[temp_argc++], expanded_args[i], 
                       MAX_TOKEN_LEN - 1);
			}
			
			/* 构建命令行 */
			cmd_line[0] = '\0';
			for (i = 0; i < temp_argc; i++) {
				if (i > 0)
					strcat(cmd_line, " ");
				strcat(cmd_line, temp_args[i]);
			}
		} else {
			/* 没有映射 - 使用原始命令 */
			build_command_line(cmd_line, sizeof(cmd_line), 
			                  expanded_args, cmd->argc);
		}
		
		/* 执行Windows命令 */
		result = execute_windows_command(ctx, cmd_line);
	}
	
	/* 释放展开的参数并置NULL防止重复释放 */
	for (i = 0; i < cmd->argc; i++) {
		if (expanded_args[i]) {
			free(expanded_args[i]);
			expanded_args[i] = NULL;
		}
	}
	
	return result;
}

/*
 * executor_run_pipeline - 执行管道
 * 
 * @ctx: 执行上下文
 * @pipeline: 管道节点
 * @返回值: 管道中最后一个命令的退出码
 * 
 * 管道执行原理:
 * 1. 创建管道连接相邻命令
 * 2. 为每个命令创建进程
 * 3. 设置stdin/stdout重定向
 * 4. 等待所有进程完成
 * 5. 返回最后一个命令的退出码
 */
int executor_run_pipeline(struct exec_context *ctx, 
                         struct pipeline_node *pipeline)
{
	HANDLE pipes[32][2];      /* [命令索引][0=读端, 1=写端] */
	STARTUPINFOA si[32];      /* 每个进程的启动信息 */
	PROCESS_INFORMATION pi[32]; /* 每个进程的信息 */
	char cmd_lines[32][4096]; /* 每个命令的命令行 */
	int i;
	int j;
	DWORD exit_code = 0;
	SECURITY_ATTRIBUTES sa;
	
	(void)cmd_lines;  /* 某些代码路径可能不使用 */
	
	/* 参数检查 */
	if (!pipeline || pipeline->cmd_count == 0)
		return -1;
	
	/* 如果只有一个命令，直接执行（不需要管道） */
	if (pipeline->cmd_count == 1) {
		if (pipeline->commands[0]->type == AST_COMMAND)
			return executor_run_command(ctx, &pipeline->commands[0]->data.cmd);
		return -1;
	}
	
	/* 设置安全属性，允许句柄被子进程继承 */
	sa.nLength = sizeof(SECURITY_ATTRIBUTES);
	sa.bInheritHandle = TRUE;
	sa.lpSecurityDescriptor = NULL;
	
	/* 创建连接命令的管道 */
	for (i = 0; i < pipeline->cmd_count - 1; i++) {
		if (!CreatePipe(&pipes[i][0], &pipes[i][1], &sa, 0))
			return -1;
	}
	
	/* 为每个命令创建进程 */
	for (i = 0; i < pipeline->cmd_count; i++) {
		struct ast_node *node = pipeline->commands[i];
		char *args[MAX_CMD_ARGS];
		char *expanded_args[MAX_CMD_ARGS];
		int argc;
		
		if (node->type != AST_COMMAND)
			continue;
		
		/* 展开变量 */
		for (j = 0; j < node->data.cmd.argc; j++) {
			expanded_args[j] = expand_variables(ctx, node->data.cmd.args[j]);
			if (!expanded_args[j])
				expanded_args[j] = string_duplicate(node->data.cmd.args[j]);
		}
		argc = node->data.cmd.argc;
		
		/* 映射命令（如果需要） */
		const char *windows_cmd = map_unix_to_windows(expanded_args[0]);
		
		/* 构建命令行 */
		build_command_line(cmd_lines[i], sizeof(cmd_lines[i]), 
		                  expanded_args, argc);
		
		/* 设置启动信息 */
		ZeroMemory(&si[i], sizeof(STARTUPINFOA));
		si[i].cb = sizeof(STARTUPINFOA);
		si[i].dwFlags = STARTF_USESTDHANDLES;
		
		/* 设置标准输入 */
		if (i == 0) {
			/* 第一个命令：使用标准输入 */
			si[i].hStdInput = GetStdHandle(STD_INPUT_HANDLE);
		} else {
			/* 其他命令：从前一个管道读取 */
			si[i].hStdInput = pipes[i-1][0];
		}
		
		/* 设置标准输出 */
		if (i == pipeline->cmd_count - 1) {
			/* 最后一个命令：使用标准输出 */
			si[i].hStdOutput = GetStdHandle(STD_OUTPUT_HANDLE);
		} else {
			/* 其他命令：写入下一个管道 */
			si[i].hStdOutput = pipes[i][1];
		}
		
		/* 标准错误始终输出到屏幕 */
		si[i].hStdError = GetStdHandle(STD_ERROR_HANDLE);
		
		/* 创建进程 */
		ZeroMemory(&pi[i], sizeof(PROCESS_INFORMATION));
		if (!CreateProcessA(NULL, cmd_lines[i], NULL, NULL, TRUE,
		                   0, NULL, NULL, &si[i], &pi[i])) {
			/* 创建失败，清理并返回 */
			for (j = 0; j < argc; j++)
				if (expanded_args[j])
					free(expanded_args[j]);
			return -1;
		}
		
		/* 释放展开的参数 */
		for (j = 0; j < argc; j++)
			if (expanded_args[j])
				free(expanded_args[j]);
	}
	
	/* 关闭父进程中的所有管道句柄 */
	for (i = 0; i < pipeline->cmd_count - 1; i++) {
		CloseHandle(pipes[i][0]);
		CloseHandle(pipes[i][1]);
	}
	
	/* 等待所有进程完成 */
	for (i = 0; i < pipeline->cmd_count; i++) {
		WaitForSingleObject(pi[i].hProcess, INFINITE);
		
		/* 获取最后一个进程的退出码 */
		if (i == pipeline->cmd_count - 1)
			GetExitCodeProcess(pi[i].hProcess, &exit_code);
		
		/* 关闭进程句柄 */
		CloseHandle(pi[i].hProcess);
		CloseHandle(pi[i].hThread);
	}
	
	return (int)exit_code;
}

/*
 * executor_run - 执行AST
 * 
 * @ctx: 执行上下文
 * @ast: AST根节点
 * @返回值: 最后一条命令的退出码
 * 
 * 这是执行器的主入口函数。
 * 遍历AST并根据节点类型执行相应操作。
 * 
 * 处理的节点类型:
 * - AST_COMMAND: 执行单个命令
 * - AST_PIPELINE: 执行管道
 * - AST_IF: 执行条件分支
 * - AST_WHILE: 执行while循环
 * - AST_FOR: 执行for循环
 * - AST_ASSIGNMENT: 执行变量赋值
 * - AST_SEQUENCE: 顺序执行两个节点
 */
int executor_run(struct exec_context *ctx, struct ast_node *ast)
{
	int result = 0;
	struct ast_node *current = ast;
	
	/* 遍历AST节点链表 */
	while (current && !ctx->should_exit) {
		switch (current->type) {
		case AST_COMMAND:
			/* 执行命令并更新退出码 */
			result = executor_run_command(ctx, &current->data.cmd);
			ctx->last_exit_code = result;
			break;
			
		case AST_PIPELINE:
			/* 执行管道并更新退出码 */
			result = executor_run_pipeline(ctx, &current->data.pipeline);
			ctx->last_exit_code = result;
			break;
			
		case AST_IF:
			/* 执行if语句 */
			/* 首先执行条件 */
			result = executor_run(ctx, current->data.if_stmt.condition);
			
			/* 根据条件结果执行对应分支 */
			if (result == 0) {
				/* 条件为真（退出码0），执行then分支 */
				result = executor_run(ctx, current->data.if_stmt.then_body);
			} else if (current->data.if_stmt.else_body) {
				/* 条件为假且有else分支，执行else分支 */
				result = executor_run(ctx, current->data.if_stmt.else_body);
			}
			ctx->last_exit_code = result;
			break;
			
		case AST_WHILE:
			/* 执行while循环 */
			/* 循环直到条件为假（退出码非0） */
			while (1) {
				/* 执行条件 */
				result = executor_run(ctx, current->data.while_loop.condition);
				
				/* 条件为假或需要退出，退出循环 */
				if (result != 0 || ctx->should_exit)
					break;
				
				/* 执行循环体 */
				executor_run(ctx, current->data.while_loop.body);
			}
			break;
			
		case AST_FOR:
			/* 执行for循环 */
			{
				int i;
				/* 遍历单词列表 */
				for (i = 0; i < current->data.for_loop.word_count; i++) {
					/* 将当前单词赋值给循环变量 */
					var_table_set(ctx->vars, 
					             current->data.for_loop.var_name,
					             current->data.for_loop.word_list[i]);
					
					/* 执行循环体 */
					executor_run(ctx, current->data.for_loop.body);
					
					/* 检查是否需要退出 */
					if (ctx->should_exit)
						break;
				}
			}
			break;
			
		case AST_ASSIGNMENT:
			/* 执行变量赋值 */
			{
				/* 展开值中的变量引用 */
				char *expanded = expand_variables(ctx, 
				                                 current->data.assign.value);
				if (expanded) {
					/* 设置变量 */
					var_table_set(ctx->vars, 
					             current->data.assign.var_name,
					             expanded);
					free(expanded);
				}
			}
			result = 0;  /* 赋值总是成功 */
			break;
			
		case AST_SEQUENCE:
			/* 顺序执行两个节点 */
			if (current->data.sequence[0])
				result = executor_run(ctx, current->data.sequence[0]);
			if (current->data.sequence[1] && !ctx->should_exit)
				result = executor_run(ctx, current->data.sequence[1]);
			break;
			
		default:
			/* 未知节点类型 */
			result = -1;
			break;
		}
		
		/* 移动到下一个节点 */
		current = current->next;
	}
	
	return result;
}
