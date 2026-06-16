/*
 * shell_api.h - Shell内核公共API定义文件
 * 
 * 这是shell内核对外暴露的唯一头文件。
 * 所有使用shell内核的外部代码（如demo程序）只需要包含此文件。
 * 
 * 设计原则:
 * - 使用不透明句柄(opaque handle)隐藏内部实现细节
 * - 通过回调函数处理输出和错误信息
 * - 提供简洁明了的API接口
 * 
 * 使用示例:
 *   // 1. 设置回调函数
 *   shell_callbacks_t callbacks = {
 *       .output_cb = my_output_handler,
 *       .error_cb = my_error_handler,
 *       .user_data = NULL
 *   };
 *   
 *   // 2. 初始化shell
 *   shell_context_t ctx = shell_init(&callbacks);
 *   
 *   // 3. 执行命令
 *   shell_exec_line(ctx, "echo Hello World");
 *   
 *   // 4. 清理资源
 *   shell_destroy(ctx);
 */

#ifndef _SHELL_API_H
#define _SHELL_API_H

/*============================================================================
 * 类型定义
 *============================================================================*/

/*
 * shell_context_t - Shell上下文的不透明句柄
 * 
 * 这是一个不透明指针类型，隐藏了内部实现细节。
 * 用户只需要持有这个句柄，不需要了解其内部结构。
 */
typedef void* shell_context_t;

/*
 * shell_output_callback_t - 输出回调函数类型
 * 
 * 当shell需要输出文本时会调用此回调函数。
 * 
 * @user_data: 用户在初始化时提供的自定义数据指针
 * @output: 要输出的文本字符串
 */
typedef void (*shell_output_callback_t)(void *user_data, const char *output);

/*
 * shell_error_callback_t - 错误回调函数类型
 * 
 * 当shell遇到错误时会调用此回调函数。
 * 
 * @user_data: 用户在初始化时提供的自定义数据指针
 * @error: 错误信息字符串
 * @line_number: 错误发生的行号（如果适用），0表示无特定行号
 */
typedef void (*shell_error_callback_t)(void *user_data, const char *error, 
                                       int line_number);

/*
 * shell_callbacks_t - 回调函数结构体
 * 
 * 在初始化shell时传入，用于接收shell的输出和错误信息。
 */
typedef struct {
	shell_output_callback_t output_cb;  /* 输出回调函数 */
	shell_error_callback_t error_cb;    /* 错误回调函数 */
	void *user_data;                    /* 传递给回调函数的用户数据 */
} shell_callbacks_t;

/*============================================================================
 * 核心API函数
 *============================================================================*/

/*
 * shell_init - 初始化shell环境
 * 
 * @callbacks: 回调函数结构体指针，包含输出和错误处理函数
 * @返回值: 成功返回shell上下文句柄，失败返回NULL
 * 
 * 此函数创建一个新的shell实例，包括:
 * - 初始化变量表
 * - 设置当前工作目录
 * - 注册回调函数
 * 
 * 注意: 使用完毕后必须调用shell_destroy释放资源。
 */
shell_context_t shell_init(const shell_callbacks_t *callbacks);

/*
 * shell_exec_line - 执行单行shell命令
 * 
 * @ctx: shell上下文句柄
 * @line: 要执行的命令行字符串
 * @返回值: 命令的退出码（0表示成功，非0表示失败）
 * 
 * 执行流程:
 * 1. 词法分析 - 将命令行分解为Token
 * 2. 语法分析 - 将Token解析为AST
 * 3. 执行 - 遍历AST并执行命令
 * 
 * 示例:
 *   shell_exec_line(ctx, "ls -la");
 *   shell_exec_line(ctx, "x=10");
 *   shell_exec_line(ctx, "echo $x");
 */
int shell_exec_line(shell_context_t ctx, const char *line);

/*
 * shell_exec_file - 执行shell脚本文件
 * 
 * @ctx: shell上下文句柄
 * @filepath: 脚本文件路径（.sh文件）
 * @返回值: 脚本的退出码（0表示成功，非0表示失败）
 * 
 * 此函数会:
 * 1. 读取整个脚本文件
 * 2. 切换到脚本所在目录（执行完后恢复）
 * 3. 解析并执行脚本内容
 * 
 * 示例:
 *   shell_exec_file(ctx, "test/test_basic.sh");
 */
int shell_exec_file(shell_context_t ctx, const char *filepath);

/*
 * shell_get_var - 获取变量的值
 * 
 * @ctx: shell上下文句柄
 * @name: 变量名
 * @返回值: 变量值的指针，如果变量不存在返回NULL
 * 
 * 示例:
 *   const char *pwd = shell_get_var(ctx, "PWD");
 */
const char *shell_get_var(shell_context_t ctx, const char *name);

/*
 * shell_set_var - 设置变量的值
 * 
 * @ctx: shell上下文句柄
 * @name: 变量名
 * @value: 变量值
 * @返回值: 成功返回0，失败返回-1
 * 
 * 示例:
 *   shell_set_var(ctx, "MY_VAR", "Hello");
 */
int shell_set_var(shell_context_t ctx, const char *name, const char *value);

/*
 * shell_get_exit_code - 获取上一个命令的退出码
 * 
 * @ctx: shell上下文句柄
 * @返回值: 上一个命令的退出码
 * 
 * 这对应于shell中的 $? 变量。
 */
int shell_get_exit_code(shell_context_t ctx);

/*
 * shell_should_exit - 检查shell是否应该退出
 * 
 * @ctx: shell上下文句柄
 * @返回值: 如果应该退出返回1，否则返回0
 * 
 * 当用户执行exit命令后，此函数返回1。
 */
int shell_should_exit(shell_context_t ctx);

/*
 * shell_destroy - 销毁shell环境并释放资源
 * 
 * @ctx: shell上下文句柄
 * 
 * 此函数会释放所有分配的内存，包括变量表。
 * 调用后，ctx句柄将不再有效。
 */
void shell_destroy(shell_context_t ctx);

/*============================================================================
 * 调试API函数
 * 
 * 这些函数用于开发和调试目的，可以查看词法分析和语法分析的结果。
 *============================================================================*/

/*
 * shell_debug_tokenize - 对命令行进行词法分析并返回Token信息
 * 
 * @ctx: shell上下文句柄
 * @line: 要分析的命令行
 * @token_count: 输出参数，返回Token的数量
 * @返回值: Token描述字符串数组，需要调用者释放
 * 
 * 每个字符串格式为: "[行号] Type=类型 Value='值'"
 * 
 * 使用完毕后需调用shell_debug_free_tokens释放内存。
 */
char **shell_debug_tokenize(shell_context_t ctx, const char *line, 
                            int *token_count);

/*
 * shell_debug_parse - 对命令行进行语法分析并返回AST描述
 * 
 * @ctx: shell上下文句柄
 * @line: 要分析的命令行
 * @返回值: AST的描述字符串，需要调用者释放
 * 
 * 使用完毕后需调用shell_debug_free_ast释放内存。
 */
char *shell_debug_parse(shell_context_t ctx, const char *line);

/*
 * shell_debug_free_tokens - 释放shell_debug_tokenize返回的数组
 * 
 * @tokens: Token描述字符串数组
 * @count: Token数量
 */
void shell_debug_free_tokens(char **tokens, int count);

/*
 * shell_debug_free_ast - 释放shell_debug_parse返回的字符串
 * 
 * @ast_str: AST描述字符串
 */
void shell_debug_free_ast(char *ast_str);

#endif /* _SHELL_API_H */
