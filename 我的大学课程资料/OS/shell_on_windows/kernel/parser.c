/*
 * parser.c - 语法分析器模块
 * 
 * 本文件实现了shell脚本的语法分析（Syntax Analysis）功能。
 * 
 * 语法分析是编译/解释过程的第二阶段，其任务是:
 * 1. 接收词法分析器产生的Token流
 * 2. 根据语法规则分析Token序列
 * 3. 构建抽象语法树（AST）
 * 
 * 实现方法：递归下降解析（Recursive Descent Parsing）
 * 
 * 支持的语法结构:
 * - 简单命令: command arg1 arg2 ...
 * - 管道: cmd1 | cmd2 | cmd3
 * - 变量赋值: VAR=value
 * - if语句: if cond; then body; [else body;] fi
 * - while循环: while cond; do body; done
 * - for循环: for var in words; do body; done
 * - 命令分隔: cmd1; cmd2; cmd3
 * - I/O重定向: cmd < input > output >> append
 * 
 * 语法分析器的核心是一组相互递归的解析函数:
 * - parse_statement_list: 解析语句列表
 * - parse_statement: 解析单个语句
 * - parse_pipeline: 解析管道
 * - parse_command: 解析简单命令
 * - parse_if: 解析if语句
 * - parse_while: 解析while循环
 * - parse_for: 解析for循环
 * - parse_assignment: 解析变量赋值
 */

#include "include/types.h"     /* 数据结构定义 */
#include "include/internal.h"  /* 内部接口定义 */
#include <stdlib.h>            /* malloc, free */
#include <string.h>            /* strcmp */

/*
 * 解析器状态结构体
 * 
 * 在解析过程中维护解析器的当前状态。
 */
struct parser_state {
	struct token *current;     /* 当前正在处理的Token */
	struct token *lookahead;   /* 下一个Token（用于向前看） */
	int error_line;            /* 发生错误的行号 */
};

/* 前向声明 - 解析函数相互递归调用 */
static struct ast_node *parse_statement_list(struct parser_state *state);
static struct ast_node *parse_statement(struct parser_state *state);
static struct ast_node *parse_pipeline(struct parser_state *state);
static struct ast_node *parse_command(struct parser_state *state);

/*
 * advance - 前进到下一个Token
 * 
 * @state: 解析器状态
 * 
 * 将current移动到下一个Token，同时更新lookahead。
 */
static void advance(struct parser_state *state)
{
	if (state->current)
		state->current = state->current->next;
	if (state->current)
		state->lookahead = state->current->next;
	else
		state->lookahead = NULL;
}

/*
 * skip_newlines - 跳过所有换行Token
 * 
 * @state: 解析器状态
 * 
 * shell语法中，换行符可以出现在很多地方，需要跳过它们。
 */
static void skip_newlines(struct parser_state *state)
{
	while (state->current && state->current->type == TOKEN_NEWLINE)
		advance(state);
}

/*
 * match - 检查当前Token是否匹配预期类型
 * 
 * @state: 解析器状态
 * @type: 预期的Token类型
 * @返回值: 匹配返回1，不匹配返回0
 */
static int match(struct parser_state *state, token_type_t type)
{
	return state->current && state->current->type == type;
}

/*
 * expect - 期望当前Token是指定类型，并前进
 * 
 * @state: 解析器状态
 * @type: 预期的Token类型
 * @返回值: 成功返回0，失败返回-1
 * 
 * 如果当前Token不是预期类型，设置错误行号。
 */
static int expect(struct parser_state *state, token_type_t type)
{
	if (!match(state, type)) {
		/* Token类型不匹配，记录错误位置 */
		if (state->current)
			state->error_line = state->current->line;
		return -1;
	}
	advance(state);  /* 匹配成功，前进到下一个Token */
	return 0;
}

/*
 * parse_arguments - 解析命令参数
 * 
 * @state: 解析器状态
 * @args: 输出参数数组
 * @argc: 输出参数计数
 * @返回值: 成功返回0
 * 
 * 读取连续的WORD或VARIABLE Token作为命令参数。
 */
static int parse_arguments(struct parser_state *state, char **args, int *argc)
{
	int count = 0;
	
	/* 读取所有参数 */
	while (state->current && 
	       (state->current->type == TOKEN_WORD ||
	        state->current->type == TOKEN_VARIABLE) &&
	       count < MAX_CMD_ARGS - 1) {
		args[count++] = string_duplicate(state->current->value);
		advance(state);
	}
	
	*argc = count;
	return 0;
}

/*
 * parse_command - 解析简单命令
 * 
 * @state: 解析器状态
 * @返回值: 成功返回命令节点，失败返回NULL
 * 
 * 简单命令格式: command arg1 arg2 ... [< input] [> output]
 * 
 * 处理流程:
 * 1. 读取命令名
 * 2. 读取所有参数
 * 3. 处理I/O重定向
 * 4. 检查后台执行标志
 */
static struct ast_node *parse_command(struct parser_state *state)
{
	char *cmd_name;
	char *args[MAX_CMD_ARGS];
	int argc = 0;
	int i;
	struct ast_node *node;
	
	/* 检查当前Token是否是命令名 */
	if (!state->current || 
	    (state->current->type != TOKEN_WORD &&
	     state->current->type != TOKEN_VARIABLE))
		return NULL;
	
	/* 获取命令名 */
	cmd_name = string_duplicate(state->current->value);
	args[argc++] = string_duplicate(state->current->value);  /* args[0]也是命令名 */
	advance(state);
	
	/* 解析参数 */
	while (state->current &&
	       (state->current->type == TOKEN_WORD ||
	        state->current->type == TOKEN_VARIABLE)) {
		if (argc < MAX_CMD_ARGS - 1) {
			args[argc++] = string_duplicate(state->current->value);
		}
		advance(state);
	}
	
	/* 创建命令节点 */
	node = ast_create_command(cmd_name, args, argc);
	
	/* 处理I/O重定向 */
	while (state->current &&
	       (state->current->type == TOKEN_REDIRECT_IN ||
	        state->current->type == TOKEN_REDIRECT_OUT ||
	        state->current->type == TOKEN_REDIRECT_APPEND)) {
		struct redirect_info *redir;
		token_type_t redir_type = state->current->type;
		
		advance(state);  /* 跳过重定向符号 */
		
		/* 重定向后必须跟文件名 */
		if (!state->current || state->current->type != TOKEN_WORD) {
			ast_destroy(node);
			return NULL;
		}
		
		/* 创建重定向信息 */
		redir = (struct redirect_info *)malloc(sizeof(struct redirect_info));
		if (redir) {
			redir->type = redir_type;
			redir->filename = string_duplicate(state->current->value);
			redir->fd = -1;
			/* 将新重定向插入链表头部 */
			redir->next = node->data.cmd.redirects;
			node->data.cmd.redirects = redir;
		}
		
		advance(state);  /* 跳过文件名 */
	}
	
	/* 检查后台执行标志 (&) */
	if (match(state, TOKEN_BACKGROUND)) {
		node->data.cmd.background = 1;
		advance(state);
	}
	
	return node;
}

/*
 * parse_pipeline - 解析管道
 * 
 * @state: 解析器状态
 * @返回值: 成功返回管道节点或命令节点，失败返回NULL
 * 
 * 管道格式: cmd1 | cmd2 | cmd3
 * 
 * 如果只有一个命令，直接返回命令节点（不创建管道节点）。
 * 如果有多个命令通过 | 连接，创建管道节点。
 */
static struct ast_node *parse_pipeline(struct parser_state *state)
{
	struct ast_node *cmds[32];  /* 临时存储管道中的命令 */
	int cmd_count = 0;
	struct ast_node *cmd;
	
	/* 解析第一个命令 */
	cmd = parse_command(state);
	if (!cmd)
		return NULL;
	
	cmds[cmd_count++] = cmd;
	
	/* 解析后续的管道命令 */
	while (match(state, TOKEN_PIPE)) {
		advance(state);        /* 跳过 | */
		skip_newlines(state);  /* 管道后可以换行 */
		
		/* 解析下一个命令 */
		cmd = parse_command(state);
		if (!cmd) {
			/* 解析失败，清理已解析的命令 */
			int i;
			for (i = 0; i < cmd_count; i++)
				ast_destroy(cmds[i]);
			return NULL;
		}
		
		if (cmd_count < 32)
			cmds[cmd_count++] = cmd;
	}
	
	/* 如果只有一个命令，直接返回它 */
	if (cmd_count == 1)
		return cmds[0];
	
	/* 创建管道节点 */
	return ast_create_pipeline(cmds, cmd_count);
}

/*
 * parse_if - 解析if语句
 * 
 * @state: 解析器状态
 * @返回值: 成功返回if节点，失败返回NULL
 * 
 * if语句格式:
 *   if condition
 *   then
 *       commands
 *   [else
 *       commands]
 *   fi
 */
static struct ast_node *parse_if(struct parser_state *state)
{
	struct ast_node *condition, *then_body, *else_body = NULL;
	
	/* 期望 'if' 关键字 */
	if (expect(state, TOKEN_IF) < 0)
		return NULL;
	
	skip_newlines(state);
	
	/* 解析条件表达式 */
	condition = parse_pipeline(state);
	if (!condition)
		return NULL;
	
	skip_newlines(state);
	
	/* 期望 'then' 关键字 */
	if (expect(state, TOKEN_THEN) < 0) {
		ast_destroy(condition);
		return NULL;
	}
	
	skip_newlines(state);
	
	/* 解析then分支的命令列表 */
	then_body = parse_statement_list(state);
	
	skip_newlines(state);
	
	/* 可选的else分支 */
	if (match(state, TOKEN_ELSE)) {
		advance(state);
		skip_newlines(state);
		else_body = parse_statement_list(state);
		skip_newlines(state);
	}
	
	/* 期望 'fi' 关键字 */
	if (expect(state, TOKEN_FI) < 0) {
		ast_destroy(condition);
		ast_destroy(then_body);
		ast_destroy(else_body);
		return NULL;
	}
	
	return ast_create_if(condition, then_body, else_body);
}

/*
 * parse_while - 解析while循环
 * 
 * @state: 解析器状态
 * @返回值: 成功返回while节点，失败返回NULL
 * 
 * while循环格式:
 *   while condition
 *   do
 *       commands
 *   done
 */
static struct ast_node *parse_while(struct parser_state *state)
{
	struct ast_node *condition, *body;
	
	/* 期望 'while' 关键字 */
	if (expect(state, TOKEN_WHILE) < 0)
		return NULL;
	
	skip_newlines(state);
	
	/* 解析循环条件 */
	condition = parse_pipeline(state);
	if (!condition)
		return NULL;
	
	skip_newlines(state);
	
	/* 期望 'do' 关键字 */
	if (expect(state, TOKEN_DO) < 0) {
		ast_destroy(condition);
		return NULL;
	}
	
	skip_newlines(state);
	
	/* 解析循环体 */
	body = parse_statement_list(state);
	
	skip_newlines(state);
	
	/* 期望 'done' 关键字 */
	if (expect(state, TOKEN_DONE) < 0) {
		ast_destroy(condition);
		ast_destroy(body);
		return NULL;
	}
	
	return ast_create_while(condition, body);
}

/*
 * parse_for - 解析for循环
 * 
 * @state: 解析器状态
 * @返回值: 成功返回for节点，失败返回NULL
 * 
 * for循环格式:
 *   for variable in word1 word2 word3
 *   do
 *       commands
 *   done
 */
static struct ast_node *parse_for(struct parser_state *state)
{
	char *var_name;
	char *words[64];       /* 临时存储单词列表 */
	int word_count = 0;
	struct ast_node *body;
	
	/* 期望 'for' 关键字 */
	if (expect(state, TOKEN_FOR) < 0)
		return NULL;
	
	skip_newlines(state);
	
	/* 获取循环变量名 */
	if (!match(state, TOKEN_WORD)) {
		state->error_line = state->current ? state->current->line : 0;
		return NULL;
	}
	
	var_name = string_duplicate(state->current->value);
	advance(state);
	
	skip_newlines(state);
	
	/* 期望 'in' 关键字 */
	if (expect(state, TOKEN_IN) < 0) {
		free(var_name);
		return NULL;
	}
	
	skip_newlines(state);
	
	/* 解析单词列表（遍历值） */
	while (state->current && (state->current->type == TOKEN_WORD ||
	                          state->current->type == TOKEN_NUMBER)) {
		if (word_count < 64)
			words[word_count++] = string_duplicate(state->current->value);
		advance(state);
		skip_newlines(state);  /* 单词之间可以有换行 */
	}
	
	/* 期望 'do' 关键字 */
	if (expect(state, TOKEN_DO) < 0) {
		int i;
		free(var_name);
		for (i = 0; i < word_count; i++)
			free(words[i]);
		return NULL;
	}
	
	skip_newlines(state);
	
	/* 解析循环体 */
	body = parse_statement_list(state);
	
	skip_newlines(state);
	
	/* 期望 'done' 关键字 */
	if (expect(state, TOKEN_DONE) < 0) {
		int i;
		free(var_name);
		for (i = 0; i < word_count; i++)
			free(words[i]);
		ast_destroy(body);
		return NULL;
	}
	
	return ast_create_for(var_name, words, word_count, body);
}

/*
 * parse_assignment - 解析变量赋值
 * 
 * @state: 解析器状态
 * @返回值: 成功返回赋值节点，失败返回NULL
 * 
 * 赋值格式: VAR=value
 * 
 * 注意: 等号两边不能有空格
 */
static struct ast_node *parse_assignment(struct parser_state *state)
{
	char *var_name;
	char *value = NULL;
	
	/* 获取变量名 */
	var_name = string_duplicate(state->current->value);
	advance(state);
	
	/* 期望 '=' */
	if (expect(state, TOKEN_ASSIGN) < 0) {
		free(var_name);
		return NULL;
	}
	
	/* 获取值（可以是WORD, NUMBER, 或 VARIABLE） */
	if (state->current && (state->current->type == TOKEN_WORD || 
	                       state->current->type == TOKEN_NUMBER ||
	                       state->current->type == TOKEN_VARIABLE)) {
		value = string_duplicate(state->current->value);
		advance(state);
	} else {
		value = string_duplicate("");  /* 空值 */
	}
	
	return ast_create_assignment(var_name, value);
}

/*
 * parse_statement - 解析单个语句
 * 
 * @state: 解析器状态
 * @返回值: 成功返回语句节点，失败返回NULL
 * 
 * 语句可以是:
 * - if语句
 * - while循环
 * - for循环
 * - 变量赋值
 * - 管道/命令
 */
static struct ast_node *parse_statement(struct parser_state *state)
{
	skip_newlines(state);
	
	/* 检查是否到达输入末尾 */
	if (!state->current || state->current->type == TOKEN_EOF)
		return NULL;
	
	/* 检查是否是if语句 */
	if (match(state, TOKEN_IF))
		return parse_if(state);
	
	/* 检查是否是while循环 */
	if (match(state, TOKEN_WHILE))
		return parse_while(state);
	
	/* 检查是否是for循环 */
	if (match(state, TOKEN_FOR))
		return parse_for(state);
	
	/* 检查是否是变量赋值 (word = value) */
	if (state->current->type == TOKEN_WORD && 
	    state->lookahead && state->lookahead->type == TOKEN_ASSIGN)
		return parse_assignment(state);
	
	/* 默认解析为管道/命令 */
	return parse_pipeline(state);
}

/*
 * parse_statement_list - 解析语句列表
 * 
 * @state: 解析器状态
 * @返回值: 语句链表的头节点
 * 
 * 语句列表由多个语句组成，以分号或换行符分隔。
 * 解析直到遇到结束标记（fi, done, else, esac, EOF）。
 */
static struct ast_node *parse_statement_list(struct parser_state *state)
{
	struct ast_node *first = NULL;
	struct ast_node *current = NULL;
	
	/* 循环解析语句，直到遇到结束标记 */
	while (state->current && 
	       state->current->type != TOKEN_EOF &&
	       state->current->type != TOKEN_FI &&
	       state->current->type != TOKEN_DONE &&
	       state->current->type != TOKEN_ELSE &&
	       state->current->type != TOKEN_ESAC) {
		struct ast_node *stmt = parse_statement(state);
		
		if (!stmt)
			break;
		
		/* 将语句添加到链表 */
		if (!first) {
			first = current = stmt;
		} else {
			current->next = stmt;
			current = stmt;
		}
		
		/* 跳过语句分隔符（分号或换行） */
		while (state->current &&
		       (state->current->type == TOKEN_SEMICOLON ||
		        state->current->type == TOKEN_NEWLINE)) {
			advance(state);
		}
	}
	
	return first;  /* 返回语句链表头 */
}

/*
 * parser_parse - 语法分析器主入口函数
 * 
 * @tokens: Token链表头指针（来自词法分析器）
 * @error_line: 输出参数，如果发生错误则存储错误行号
 * @返回值: 成功返回AST根节点，失败返回NULL
 * 
 * 这是语法分析器的对外接口。
 * 
 * 使用示例:
 *   int error_line;
 *   struct ast_node *ast = parser_parse(tokens, &error_line);
 *   if (!ast) {
 *       printf("Syntax error at line %d\n", error_line);
 *   } else {
 *       // 使用AST...
 *       ast_destroy(ast);  // 用完后释放
 *   }
 */
struct ast_node *parser_parse(struct token *tokens, int *error_line)
{
	struct parser_state state;
	struct ast_node *ast;
	
	/* 参数检查 */
	if (!tokens)
		return NULL;
	
	/* 初始化解析器状态 */
	state.current = tokens;
	state.lookahead = tokens->next;
	state.error_line = 0;
	
	/* 解析语句列表 */
	ast = parse_statement_list(&state);
	
	/* 输出错误行号 */
	if (error_line)
		*error_line = state.error_line;
	
	return ast;
}
