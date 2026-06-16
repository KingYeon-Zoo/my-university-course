/*
 * ast.c - 抽象语法树(AST)操作模块
 * 
 * 本文件实现了抽象语法树的创建、操作和销毁功能。
 * 
 * 抽象语法树(Abstract Syntax Tree)是源代码的树状表示形式，
 * 它是语法分析器的输出，也是执行器的输入。
 * 
 * AST的作用:
 * - 将线性的Token流转换为层次结构
 * - 体现代码的语法结构和运算优先级
 * - 便于执行器遍历和执行
 * 
 * 节点类型说明:
 * - AST_COMMAND: 简单命令节点，如 "ls -la"
 * - AST_PIPELINE: 管道节点，如 "cat file | grep pattern"
 * - AST_IF: if条件语句节点
 * - AST_WHILE: while循环节点
 * - AST_FOR: for循环节点
 * - AST_ASSIGNMENT: 变量赋值节点
 * - AST_SEQUENCE: 顺序执行节点
 */

#include "include/types.h"     /* 数据结构定义 */
#include "include/internal.h"  /* 内部接口定义 */
#include <stdlib.h>            /* malloc, free */
#include <string.h>            /* memset */

/*
 * ast_create_node - 创建一个新的AST节点
 * 
 * @type: 要创建的节点类型（AST_COMMAND, AST_IF等）
 * @返回值: 成功返回新节点的指针，失败返回NULL
 * 
 * 功能说明:
 * 1. 分配节点所需的内存
 * 2. 初始化所有字段为0（使用memset）
 * 3. 设置节点类型
 * 
 * 注意: 返回的节点需要调用ast_destroy释放
 */
struct ast_node *ast_create_node(ast_node_type_t type)
{
	struct ast_node *node;
	
	/* 分配内存 */
	node = (struct ast_node *)malloc(sizeof(struct ast_node));
	if (!node)
		return NULL;  /* 内存分配失败 */
	
	/* 初始化所有字段为0，确保指针为NULL */
	memset(node, 0, sizeof(struct ast_node));
	
	/* 设置节点类型 */
	node->type = type;
	node->next = NULL;  /* 初始化链表指针为空 */
	
	return node;
}

/*
 * ast_create_command - 创建一个命令节点
 * 
 * @name: 命令名称（如 ls, echo, cat）
 * @args: 参数数组（包括命令名本身）
 * @argc: 参数数量
 * @返回值: 成功返回命令节点指针，失败返回NULL
 * 
 * 命令节点表示一个简单的shell命令，包括:
 * - 命令名称
 * - 参数列表
 * - 重定向信息（初始为空）
 * - 后台执行标志（初始为0）
 * 
 * 示例: 对于命令 "ls -l -a /home"
 * - name = "ls"
 * - args = ["ls", "-l", "-a", "/home"]
 * - argc = 4
 */
struct ast_node *ast_create_command(char *name, char **args, int argc)
{
	struct ast_node *node;
	int i;
	
	/* 创建基础节点 */
	node = ast_create_node(AST_COMMAND);
	if (!node)
		return NULL;
	
	/* 设置命令名称 */
	node->data.cmd.name = name;
	
	/* 设置参数数量 */
	node->data.cmd.argc = argc;
	
	/* 复制参数数组（注意不要超过最大限制） */
	for (i = 0; i < argc && i < MAX_CMD_ARGS; i++)
		node->data.cmd.args[i] = args[i];
	
	/* 初始化其他字段 */
	node->data.cmd.redirects = NULL;   /* 无重定向 */
	node->data.cmd.background = 0;     /* 前台执行 */
	
	return node;
}

/*
 * ast_create_pipeline - 创建一个管道节点
 * 
 * @cmds: 命令节点数组
 * @count: 管道中的命令数量
 * @返回值: 成功返回管道节点指针，失败返回NULL
 * 
 * 管道节点表示多个通过管道(|)连接的命令，例如:
 *   cat file.txt | grep pattern | wc -l
 * 
 * 这会创建一个包含3个命令节点的管道节点。
 * 执行时，前一个命令的stdout会连接到后一个命令的stdin。
 */
struct ast_node *ast_create_pipeline(struct ast_node **cmds, int count)
{
	struct ast_node *node;
	int i;
	
	/* 创建基础节点 */
	node = ast_create_node(AST_PIPELINE);
	if (!node)
		return NULL;
	
	/* 设置命令数量 */
	node->data.pipeline.cmd_count = count;
	
	/* 分配命令指针数组 */
	node->data.pipeline.commands = (struct ast_node **)malloc(
		sizeof(struct ast_node *) * count);
	
	/* 检查分配是否成功 */
	if (!node->data.pipeline.commands) {
		free(node);
		return NULL;
	}
	
	/* 复制命令节点指针 */
	for (i = 0; i < count; i++)
		node->data.pipeline.commands[i] = cmds[i];
	
	return node;
}

/*
 * ast_create_if - 创建一个if语句节点
 * 
 * @cond: 条件表达式（通常是一个命令，如test或[命令）
 * @then_body: 条件为真时执行的语句体
 * @else_body: 条件为假时执行的语句体（可以为NULL）
 * @返回值: 成功返回if节点指针，失败返回NULL
 * 
 * 对应shell语法:
 *   if condition
 *   then
 *       then_body
 *   else
 *       else_body
 *   fi
 * 
 * 在shell中，条件是一个命令，退出码为0表示真，非0表示假。
 */
struct ast_node *ast_create_if(struct ast_node *cond, struct ast_node *then_body,
                               struct ast_node *else_body)
{
	struct ast_node *node;
	
	/* 创建基础节点 */
	node = ast_create_node(AST_IF);
	if (!node)
		return NULL;
	
	/* 设置条件、then分支和else分支 */
	node->data.if_stmt.condition = cond;
	node->data.if_stmt.then_body = then_body;
	node->data.if_stmt.else_body = else_body;  /* 可以为NULL */
	
	return node;
}

/*
 * ast_create_while - 创建一个while循环节点
 * 
 * @cond: 循环条件（命令，退出码为0继续循环）
 * @body: 循环体
 * @返回值: 成功返回while节点指针，失败返回NULL
 * 
 * 对应shell语法:
 *   while condition
 *   do
 *       body
 *   done
 * 
 * 当条件命令的退出码为0时，继续执行循环体；
 * 当退出码非0时，退出循环。
 */
struct ast_node *ast_create_while(struct ast_node *cond, struct ast_node *body)
{
	struct ast_node *node;
	
	/* 创建基础节点 */
	node = ast_create_node(AST_WHILE);
	if (!node)
		return NULL;
	
	/* 设置条件和循环体 */
	node->data.while_loop.condition = cond;
	node->data.while_loop.body = body;
	
	return node;
}

/*
 * ast_create_for - 创建一个for循环节点
 * 
 * @var: 循环变量名
 * @words: 要遍历的单词列表
 * @count: 单词数量
 * @body: 循环体
 * @返回值: 成功返回for节点指针，失败返回NULL
 * 
 * 对应shell语法:
 *   for var in word1 word2 word3
 *   do
 *       body  # 可以使用$var访问当前值
 *   done
 * 
 * 循环会依次将每个单词赋值给变量，然后执行循环体。
 */
struct ast_node *ast_create_for(char *var, char **words, int count,
                                struct ast_node *body)
{
	struct ast_node *node;
	int i;
	
	/* 创建基础节点 */
	node = ast_create_node(AST_FOR);
	if (!node)
		return NULL;
	
	/* 设置循环变量名 */
	node->data.for_loop.var_name = var;
	
	/* 设置单词数量 */
	node->data.for_loop.word_count = count;
	
	/* 分配单词列表数组 */
	node->data.for_loop.word_list = (char **)malloc(sizeof(char *) * count);
	if (!node->data.for_loop.word_list) {
		free(node);
		return NULL;
	}
	
	/* 复制单词指针 */
	for (i = 0; i < count; i++)
		node->data.for_loop.word_list[i] = words[i];
	
	/* 设置循环体 */
	node->data.for_loop.body = body;
	
	return node;
}

/*
 * ast_create_assignment - 创建一个变量赋值节点
 * 
 * @name: 变量名
 * @value: 要赋的值
 * @返回值: 成功返回赋值节点指针，失败返回NULL
 * 
 * 对应shell语法: VAR=value
 * 
 * 注意：赋值操作的等号两边不能有空格。
 * 正确: x=10
 * 错误: x = 10 (这会被解析为执行x命令，参数为=和10)
 */
struct ast_node *ast_create_assignment(char *name, char *value)
{
	struct ast_node *node;
	
	/* 创建基础节点 */
	node = ast_create_node(AST_ASSIGNMENT);
	if (!node)
		return NULL;
	
	/* 设置变量名和值 */
	node->data.assign.var_name = name;
	node->data.assign.value = value;
	
	return node;
}

/*
 * ast_destroy - 递归销毁AST节点及其所有子节点
 * 
 * @node: 要销毁的节点指针
 * 
 * 此函数会:
 * 1. 根据节点类型释放相应的动态分配内存
 * 2. 递归销毁所有子节点
 * 3. 释放节点本身
 * 
 * 注意: 调用此函数后，传入的指针将失效。
 */
void ast_destroy(struct ast_node *node)
{
	int i;
	
	/* NULL检查 */
	if (!node)
		return;
	
	/* 根据节点类型释放相应的资源 */
	switch (node->type) {
	case AST_COMMAND:
		/* 释放命令名 */
		if (node->data.cmd.name)
			free(node->data.cmd.name);
		
		/* 释放所有参数 */
		for (i = 0; i < node->data.cmd.argc; i++)
			if (node->data.cmd.args[i])
				free(node->data.cmd.args[i]);
		
		/* TODO: 释放重定向链表 */
		break;
		
	case AST_PIPELINE:
		/* 递归销毁管道中的所有命令 */
		for (i = 0; i < node->data.pipeline.cmd_count; i++)
			ast_destroy(node->data.pipeline.commands[i]);
		
		/* 释放命令指针数组 */
		if (node->data.pipeline.commands)
			free(node->data.pipeline.commands);
		break;
		
	case AST_IF:
		/* 递归销毁条件和两个分支 */
		ast_destroy(node->data.if_stmt.condition);
		ast_destroy(node->data.if_stmt.then_body);
		ast_destroy(node->data.if_stmt.else_body);  /* 可能为NULL，函数会处理 */
		break;
		
	case AST_WHILE:
		/* 递归销毁条件和循环体 */
		ast_destroy(node->data.while_loop.condition);
		ast_destroy(node->data.while_loop.body);
		break;
		
	case AST_FOR:
		/* 释放循环变量名 */
		if (node->data.for_loop.var_name)
			free(node->data.for_loop.var_name);
		
		/* 释放单词列表 */
		for (i = 0; i < node->data.for_loop.word_count; i++)
			if (node->data.for_loop.word_list[i])
				free(node->data.for_loop.word_list[i]);
		
		/* 释放单词数组 */
		if (node->data.for_loop.word_list)
			free(node->data.for_loop.word_list);
		
		/* 递归销毁循环体 */
		ast_destroy(node->data.for_loop.body);
		break;
		
	case AST_ASSIGNMENT:
		/* 释放变量名和值 */
		if (node->data.assign.var_name)
			free(node->data.assign.var_name);
		if (node->data.assign.value)
			free(node->data.assign.value);
		break;
		
	case AST_SEQUENCE:
		/* 递归销毁两个子节点 */
		ast_destroy(node->data.sequence[0]);
		ast_destroy(node->data.sequence[1]);
		break;
		
	default:
		/* 其他类型暂不处理 */
		break;
	}
	
	/* 释放节点本身 */
	free(node);
}
