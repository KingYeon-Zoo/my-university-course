/*
 * internal.h - Shell内核内部接口定义文件
 * 
 * 本头文件定义了内核各模块之间使用的内部函数接口。
 * 这些函数是内核模块间通信的桥梁，不对外暴露给demo代码。
 * 
 * 注意：外部代码（如demo程序）不应该包含此头文件，
 * 应该只使用 shell_api.h 中定义的公共接口。
 * 
 * 模块划分:
 * - 内存池模块 (memory_pool.c)
 * - 词法分析模块 (lexer.c)
 * - 语法分析模块 (parser.c)
 * - AST操作模块 (ast.c)
 * - 变量表模块 (variable.c)
 * - 执行器模块 (executor.c)
 * - 内置命令模块 (builtin_cmd.c)
 * - 命令映射模块 (cmd_mapping.c)
 * - I/O重定向模块 (io_redirect.c)
 * - 工具函数模块 (utils.c)
 */

#ifndef _SHELL_INTERNAL_H
#define _SHELL_INTERNAL_H

#include "types.h"  /* 包含所有数据结构定义 */

/*============================================================================
 * 内存池操作函数
 * 
 * 提供高效的批量内存管理功能。所有通过pool_alloc分配的内存
 * 会在pool_destroy时统一释放，无需单独释放每块内存。
 *============================================================================*/

/*
 * pool_create - 创建一个新的内存池
 * 
 * @返回值: 成功返回内存池指针，失败返回NULL
 * 
 * 使用示例:
 *   struct mem_pool *pool = pool_create();
 *   if (pool) {
 *       // 使用内存池...
 *       pool_destroy(pool);
 *   }
 */
struct mem_pool *pool_create(void);

/*
 * pool_alloc - 从内存池中分配内存
 * 
 * @pool: 内存池指针
 * @size: 要分配的字节数
 * @返回值: 成功返回分配的内存指针，失败返回NULL
 * 
 * 分配的内存会被初始化为0。
 */
void *pool_alloc(struct mem_pool *pool, size_t size);

/*
 * pool_destroy - 销毁内存池并释放所有分配的内存
 * 
 * @pool: 要销毁的内存池指针
 * 
 * 调用此函数后，所有从该池分配的内存都将失效。
 */
void pool_destroy(struct mem_pool *pool);

/*============================================================================
 * Token操作函数
 * 
 * 用于创建、销毁和管理词法分析生成的Token。
 *============================================================================*/

/*
 * token_create - 创建一个新的Token
 * 
 * @type: Token类型（如TOKEN_WORD, TOKEN_PIPE等）
 * @value: Token的字符串值
 * @line: Token在源代码中的行号
 * @col: Token在源代码中的列号
 * @返回值: 成功返回Token指针，失败返回NULL
 */
struct token *token_create(token_type_t type, const char *value, int line, int col);

/*
 * token_destroy - 销毁单个Token
 * 
 * @tok: 要销毁的Token指针
 */
void token_destroy(struct token *tok);

/*
 * token_list_destroy - 销毁Token链表
 * 
 * @head: Token链表的头指针
 * 
 * 遍历链表并释放所有Token。
 */
void token_list_destroy(struct token *head);

/*============================================================================
 * AST操作函数
 * 
 * 用于创建和销毁抽象语法树节点。
 *============================================================================*/

/*
 * ast_create_node - 创建一个指定类型的AST节点
 * 
 * @type: 节点类型（如AST_COMMAND, AST_IF等）
 * @返回值: 成功返回节点指针，失败返回NULL
 */
struct ast_node *ast_create_node(ast_node_type_t type);

/*
 * ast_destroy - 递归销毁AST节点及其所有子节点
 * 
 * @node: 要销毁的节点指针
 * 
 * 此函数会递归释放节点中的所有动态分配的内存。
 */
void ast_destroy(struct ast_node *node);

/*
 * ast_create_command - 创建一个命令节点
 * 
 * @name: 命令名称
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 成功返回节点指针，失败返回NULL
 */
struct ast_node *ast_create_command(char *name, char **args, int argc);

/*
 * ast_create_pipeline - 创建一个管道节点
 * 
 * @cmds: 命令节点数组
 * @count: 命令数量
 * @返回值: 成功返回节点指针，失败返回NULL
 */
struct ast_node *ast_create_pipeline(struct ast_node **cmds, int count);

/*
 * ast_create_if - 创建一个if语句节点
 * 
 * @cond: 条件表达式节点
 * @then_body: then分支节点
 * @else_body: else分支节点（可以为NULL）
 * @返回值: 成功返回节点指针，失败返回NULL
 */
struct ast_node *ast_create_if(struct ast_node *cond, struct ast_node *then_body, 
                               struct ast_node *else_body);

/*
 * ast_create_while - 创建一个while循环节点
 * 
 * @cond: 循环条件节点
 * @body: 循环体节点
 * @返回值: 成功返回节点指针，失败返回NULL
 */
struct ast_node *ast_create_while(struct ast_node *cond, struct ast_node *body);

/*
 * ast_create_for - 创建一个for循环节点
 * 
 * @var: 循环变量名
 * @words: 要遍历的单词数组
 * @count: 单词数量
 * @body: 循环体节点
 * @返回值: 成功返回节点指针，失败返回NULL
 */
struct ast_node *ast_create_for(char *var, char **words, int count, 
                                struct ast_node *body);

/*
 * ast_create_assignment - 创建一个变量赋值节点
 * 
 * @name: 变量名
 * @value: 要赋的值
 * @返回值: 成功返回节点指针，失败返回NULL
 */
struct ast_node *ast_create_assignment(char *name, char *value);

/*============================================================================
 * 变量表操作函数
 * 
 * 提供shell变量的存储、查询、删除和导出功能。
 *============================================================================*/

/*
 * var_table_create - 创建一个新的变量表
 * 
 * @返回值: 成功返回变量表指针，失败返回NULL
 * 
 * 新创建的变量表会包含一些默认变量（如PWD, HOME）。
 */
struct var_table *var_table_create(void);

/*
 * var_table_destroy - 销毁变量表并释放所有条目
 * 
 * @table: 要销毁的变量表指针
 */
void var_table_destroy(struct var_table *table);

/*
 * var_table_set - 设置变量的值
 * 
 * @table: 变量表指针
 * @name: 变量名
 * @value: 变量值
 * @返回值: 成功返回0，失败返回-1
 * 
 * 如果变量已存在则更新其值，否则创建新变量。
 */
int var_table_set(struct var_table *table, const char *name, const char *value);

/*
 * var_table_get - 获取变量的值
 * 
 * @table: 变量表指针
 * @name: 变量名
 * @返回值: 成功返回变量值的指针，变量不存在返回NULL
 */
const char *var_table_get(struct var_table *table, const char *name);

/*
 * var_table_unset - 删除一个变量
 * 
 * @table: 变量表指针
 * @name: 要删除的变量名
 * @返回值: 成功返回0，变量不存在返回-1
 */
int var_table_unset(struct var_table *table, const char *name);

/*
 * var_table_export - 将变量导出为环境变量
 * 
 * @table: 变量表指针
 * @name: 要导出的变量名
 * 
 * 导出后，该变量会传递给子进程。
 */
void var_table_export(struct var_table *table, const char *name);

/*============================================================================
 * 词法分析函数
 * 
 * 将输入字符串分解为Token序列。
 *============================================================================*/

/*
 * lexer_tokenize - 将输入字符串转换为Token链表
 * 
 * @input: 输入的shell命令字符串
 * @error_line: 输出参数，如果发生错误则存储错误行号
 * @返回值: 成功返回Token链表头指针，失败返回NULL
 * 
 * 返回的Token链表需要调用者使用token_list_destroy释放。
 */
struct token *lexer_tokenize(const char *input, int *error_line);

/*============================================================================
 * 语法分析函数
 * 
 * 将Token序列解析为抽象语法树。
 *============================================================================*/

/*
 * parser_parse - 将Token链表解析为AST
 * 
 * @tokens: Token链表头指针
 * @error_line: 输出参数，如果发生错误则存储错误行号
 * @返回值: 成功返回AST根节点指针，失败返回NULL
 * 
 * 返回的AST需要调用者使用ast_destroy释放。
 */
struct ast_node *parser_parse(struct token *tokens, int *error_line);

/*============================================================================
 * 执行器函数
 * 
 * 遍历并执行抽象语法树。
 *============================================================================*/

/*
 * executor_run - 执行AST
 * 
 * @ctx: 执行上下文
 * @ast: AST根节点
 * @返回值: 最后一条命令的退出码
 */
int executor_run(struct exec_context *ctx, struct ast_node *ast);

/*
 * executor_run_command - 执行单个命令
 * 
 * @ctx: 执行上下文
 * @cmd: 命令节点
 * @返回值: 命令的退出码
 */
int executor_run_command(struct exec_context *ctx, struct cmd_node *cmd);

/*
 * executor_run_pipeline - 执行管道
 * 
 * @ctx: 执行上下文
 * @pipeline: 管道节点
 * @返回值: 管道中最后一条命令的退出码
 */
int executor_run_pipeline(struct exec_context *ctx, struct pipeline_node *pipeline);

/*============================================================================
 * 内置命令处理函数
 * 
 * 每个函数实现一个shell内置命令。这些命令在shell进程内部执行，
 * 不创建子进程。
 *============================================================================*/

/* cd - 切换当前工作目录 */
int builtin_cd(struct exec_context *ctx, char **args, int argc);

/* echo - 输出文本 */
int builtin_echo(struct exec_context *ctx, char **args, int argc);

/* pwd - 打印当前工作目录 */
int builtin_pwd(struct exec_context *ctx, char **args, int argc);

/* export - 设置环境变量 */
int builtin_export(struct exec_context *ctx, char **args, int argc);

/* exit - 退出shell */
int builtin_exit(struct exec_context *ctx, char **args, int argc);

/* test / [ - 条件测试 */
int builtin_test(struct exec_context *ctx, char **args, int argc);

/* ls - 列出目录内容 */
int builtin_ls(struct exec_context *ctx, char **args, int argc);

/* cat - 显示文件内容 */
int builtin_cat(struct exec_context *ctx, char **args, int argc);

/* mkdir - 创建目录 */
int builtin_mkdir(struct exec_context *ctx, char **args, int argc);

/* rmdir - 删除空目录 */
int builtin_rmdir(struct exec_context *ctx, char **args, int argc);

/* rm - 删除文件 */
int builtin_rm(struct exec_context *ctx, char **args, int argc);

/* cp - 复制文件 */
int builtin_cp(struct exec_context *ctx, char **args, int argc);

/* mv - 移动/重命名文件 */
int builtin_mv(struct exec_context *ctx, char **args, int argc);

/* touch - 创建文件或更新时间戳 */
int builtin_touch(struct exec_context *ctx, char **args, int argc);

/* help - 显示帮助信息 */
int builtin_help(struct exec_context *ctx, char **args, int argc);

/* clear - 清屏 */
int builtin_clear(struct exec_context *ctx, char **args, int argc);

/*
 * is_builtin - 检查命令是否是内置命令
 * 
 * @cmd: 命令名称
 * @返回值: 是内置命令返回1，否则返回0
 */
int is_builtin(const char *cmd);

/*
 * execute_builtin - 执行内置命令
 * 
 * @ctx: 执行上下文
 * @cmd: 命令名称
 * @args: 参数数组
 * @argc: 参数数量
 * @返回值: 命令的退出码，未找到命令返回-1
 */
int execute_builtin(struct exec_context *ctx, const char *cmd, 
                    char **args, int argc);

/*============================================================================
 * 命令映射函数
 * 
 * 将Unix命令转换为Windows等效命令。
 *============================================================================*/

/*
 * map_unix_to_windows - 将Unix命令映射为Windows命令
 * 
 * @unix_cmd: Unix命令名
 * @返回值: 对应的Windows命令名，如果没有映射则返回原命令
 */
const char *map_unix_to_windows(const char *unix_cmd);

/*============================================================================
 * I/O重定向函数
 * 
 * 处理输入/输出重定向操作。
 *============================================================================*/

/*
 * setup_redirects - 设置I/O重定向
 * 
 * @redirects: 重定向信息链表
 * @saved_fds: 输出参数，保存原始文件描述符用于后续恢复
 * @返回值: 成功返回0，失败返回-1
 */
int setup_redirects(struct redirect_info *redirects, int *saved_fds);

/*
 * restore_redirects - 恢复原始文件描述符
 * 
 * @saved_fds: setup_redirects保存的原始文件描述符
 */
void restore_redirects(int *saved_fds);

/*============================================================================
 * 工具函数
 * 
 * 提供各种辅助功能。
 *============================================================================*/

/*
 * hash_string - 计算字符串的哈希值
 * 
 * @str: 输入字符串
 * @返回值: 哈希值（0 到 HASH_TABLE_SIZE-1）
 * 
 * 使用djb2算法计算哈希。
 */
unsigned int hash_string(const char *str);

/*
 * string_duplicate - 复制字符串（类似strdup）
 * 
 * @str: 要复制的字符串
 * @返回值: 新分配的字符串副本，失败返回NULL
 * 
 * 返回的字符串需要调用者释放。
 */
char *string_duplicate(const char *str);

/*
 * string_free - 释放复制的字符串
 * 
 * @str: 要释放的字符串指针
 */
void string_free(char *str);

/*
 * string_match_pattern - 简单的通配符模式匹配
 * 
 * @str: 要匹配的字符串
 * @pattern: 模式（支持*和?通配符）
 * @返回值: 匹配成功返回1，失败返回0
 */
int string_match_pattern(const char *str, const char *pattern);

/*
 * expand_variables - 展开字符串中的变量引用
 * 
 * @ctx: 执行上下文
 * @str: 包含变量引用的字符串
 * @返回值: 展开后的新字符串，需要调用者释放
 * 
 * 支持 $var, ${var}, $((算术表达式)) 语法。
 */
char *expand_variables(struct exec_context *ctx, const char *str);

#endif /* _SHELL_INTERNAL_H */
