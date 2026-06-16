/*
 * lexer.c - 词法分析器模块
 *
 * 本文件实现了shell脚本的词法分析（Lexical Analysis）功能。
 *
 * 词法分析是编译/解释过程的第一阶段，其任务是:
 * 1. 读取输入的字符流
 * 2. 将字符流分解成有意义的词法单元（Token）
 * 3. 为每个Token标注类型信息
 *
 * 支持的词法元素:
 * - 关键字: if, then, else, elif, fi, while, do, done, for, in, case, esac
 * - 运算符: |, ||, &, &&, ;, <, >, >>
 * - 变量引用: $var, ${var}, $((expr))
 * - 字符串: 单引号'...'和双引号"..."
 * - 普通单词: 命令名、参数、文件名等
 * - 注释: # 开头的行
 *
 * 输出:
 * Token链表，每个Token包含类型、值、行号和列号信息。
 */

#include "include/types.h"	  /* 数据结构定义 */
#include "include/internal.h" /* 内部接口定义 */
#include <stdlib.h>			  /* malloc, free */
#include <string.h>			  /* strcmp, strncpy */
#include <ctype.h>			  /* isspace, isalnum, isdigit */

/*
 * 关键字查找表
 *
 * 用于将普通单词识别为shell关键字。
 * 表格以NULL结尾表示结束。
 */
static const struct
{
	const char *word;  /* 关键字字符串 */
	token_type_t type; /* 对应的Token类型 */
} keywords[] = {
	{"if", TOKEN_IF},			  /* if条件语句 */
	{"then", TOKEN_THEN},		  /* then关键字 */
	{"else", TOKEN_ELSE},		  /* else关键字 */
	{"elif", TOKEN_ELIF},		  /* elif关键字 */
	{"fi", TOKEN_FI},			  /* fi结束标记 */
	{"while", TOKEN_WHILE},		  /* while循环 */
	{"do", TOKEN_DO},			  /* do关键字 */
	{"done", TOKEN_DONE},		  /* done结束标记 */
	{"for", TOKEN_FOR},			  /* for循环 */
	{"in", TOKEN_IN},			  /* in关键字 */
	{"case", TOKEN_CASE},		  /* case语句 */
	{"esac", TOKEN_ESAC},		  /* esac结束标记 */
	{"function", TOKEN_FUNCTION}, /* 函数定义 */
	{NULL, TOKEN_WORD}			  /* 表结束标记 */
};

/*
 * lookup_keyword - 检查一个单词是否是关键字
 *
 * @word: 要检查的单词
 * @返回值: 如果是关键字返回对应的Token类型，否则返回TOKEN_WORD
 *
 * 遍历关键字表进行匹配。
 */
static token_type_t lookup_keyword(const char *word)
{
	int i;

	/* 遍历关键字表 */
	for (i = 0; keywords[i].word != NULL; i++)
	{
		if (strcmp(word, keywords[i].word) == 0)
			return keywords[i].type; /* 找到匹配的关键字 */
	}

	return TOKEN_WORD; /* 不是关键字，作为普通单词处理 */
}

/*
 * token_create - 创建一个新的Token
 *
 * @type: Token类型
 * @value: Token的字符串值
 * @line: Token在源代码中的行号
 * @col: Token在源代码中的列号
 * @返回值: 成功返回Token指针，失败返回NULL
 *
 * 分配内存并初始化Token的所有字段。
 */
struct token *token_create(token_type_t type, const char *value,
						   int line, int col)
{
	struct token *tok;

	/* 分配Token内存 */
	tok = (struct token *)malloc(sizeof(struct token));
	if (!tok)
		return NULL;

	/* 设置Token属性 */
	tok->type = type;
	tok->line = line;
	tok->column = col;
	tok->next = NULL; /* 初始化链表指针 */

	/* 复制Token值 */
	if (value)
	{
		strncpy(tok->value, value, MAX_TOKEN_LEN - 1);
		tok->value[MAX_TOKEN_LEN - 1] = '\0'; /* 确保字符串结束 */
	}
	else
	{
		tok->value[0] = '\0'; /* 空值 */
	}

	return tok;
}

/*
 * token_destroy - 销毁单个Token
 *
 * @tok: 要销毁的Token指针
 *
 * 释放Token占用的内存。
 */
void token_destroy(struct token *tok)
{
	if (tok)
		free(tok);
}

/*
 * token_list_destroy - 销毁Token链表
 *
 * @head: Token链表的头指针
 *
 * 遍历链表并释放所有Token。
 */
void token_list_destroy(struct token *head)
{
	struct token *tok, *next;

	tok = head;
	while (tok)
	{
		next = tok->next;	/* 保存下一个Token的指针 */
		token_destroy(tok); /* 释放当前Token */
		tok = next;			/* 移动到下一个 */
	}
}

/*
 * skip_whitespace - 跳过空白字符（不包括换行符）
 *
 * @input: 输入字符串的当前位置
 * @返回值: 跳过空白后的位置
 *
 * 注意：换行符不被视为空白，因为它在shell中有语义作用。
 */
static const char *skip_whitespace(const char *input)
{
	while (*input && isspace(*input) && *input != '\n')
		input++;
	return input;
}

/*
 * read_quoted_string - 读取引号内的字符串
 *
 * @input: 输入字符串的当前位置（应指向开始引号）
 * @quote: 引号字符（单引号'或双引号"）
 * @buffer: 输出缓冲区
 * @max_len: 缓冲区最大长度
 * @返回值: 读取完成后的输入位置（指向引号后的字符）
 *
 * 处理转义序列:
 * - \n -> 换行符
 * - \t -> 制表符
 * - \r -> 回车符
 * - \\ -> 反斜杠
 * - \" -> 双引号
 * - \' -> 单引号
 */
static const char *read_quoted_string(const char *input, char quote,
									  char *buffer, int max_len)
{
	int i = 0;

	/* 跳过开始引号 */
	input++;

	/* 读取直到遇到结束引号或字符串结束 */
	while (*input && *input != quote && i < max_len - 1)
	{
		if (*input == '\\' && *(input + 1))
		{
			/* 处理转义序列 */
			input++; /* 跳过反斜杠 */
			switch (*input)
			{
			case 'n':
				buffer[i++] = '\n';
				break; /* 换行 */
			case 't':
				buffer[i++] = '\t';
				break; /* 制表符 */
			case 'r':
				buffer[i++] = '\r';
				break; /* 回车 */
			case '\\':
				buffer[i++] = '\\';
				break; /* 反斜杠 */
			case '"':
				buffer[i++] = '"';
				break; /* 双引号 */
			case '\'':
				buffer[i++] = '\'';
				break; /* 单引号 */
			default:
				buffer[i++] = *input;
				break; /* 其他字符原样保留 */
			}
			input++;
		}
		else
		{
			/* 普通字符，直接复制 */
			buffer[i++] = *input++;
		}
	}

	buffer[i] = '\0'; /* 字符串结束 */

	/* 跳过结束引号 */
	if (*input == quote)
		input++;

	return input;
}

/*
 * read_word - 读取一个普通单词（非引号包围的Token）
 *
 * @input: 输入字符串的当前位置
 * @buffer: 输出缓冲区
 * @max_len: 缓冲区最大长度
 * @返回值: 读取完成后的输入位置
 *
 * 单词以空白字符或特殊字符（; | & < > ( ) { } =）结束。
 */
static const char *read_word(const char *input, char *buffer, int max_len)
{
	int i = 0;

	/* 读取直到遇到分隔符 */
	while (*input && !isspace(*input) &&
		   *input != ';' && *input != '|' && *input != '&' &&
		   *input != '<' && *input != '>' && *input != '(' &&
		   *input != ')' && *input != '{' && *input != '}' &&
		   *input != '=' &&
		   i < max_len - 1)
	{
		buffer[i++] = *input++;
	}

	buffer[i] = '\0'; /* 字符串结束 */
	return input;
}

/*
 * lexer_tokenize - 将输入字符串转换为Token链表
 *
 * @input: 输入的shell命令/脚本字符串
 * @error_line: 输出参数，如果发生错误则存储错误行号
 * @返回值: 成功返回Token链表头指针，失败返回NULL
 *
 * 这是词法分析器的主入口函数。
 *
 * 处理流程:
 * 1. 跳过空白字符
 * 2. 识别并处理注释（#开头）
 * 3. 识别特殊符号（;, |, &, <, >, =等）
 * 4. 识别引号字符串
 * 5. 识别变量引用（$开头）
 * 6. 识别普通单词和关键字
 * 7. 添加EOF Token表示输入结束
 *
 * 注意: 返回的Token链表需要调用者使用token_list_destroy释放。
 */
struct token *lexer_tokenize(const char *input, int *error_line)
{
	struct token *head = NULL;	/* Token链表头 */
	struct token *tail = NULL;	/* Token链表尾 */
	struct token *tok;			/* 当前处理的Token */
	const char *p = input;		/* 输入指针 */
	char buffer[MAX_TOKEN_LEN]; /* 临时缓冲区 */
	int line = 1;				/* 当前行号 */
	int col = 1;				/* 当前列号 */

	/* 初始化错误行号 */
	if (error_line)
		*error_line = 0;

	/* 主循环：处理输入中的每个字符 */
	while (*p)
	{
		/* 跳过空白字符（不包括换行） */
		while (*p && isspace(*p) && *p != '\n')
		{
			p++;
			col++;
		}

		/* 检查是否到达输入末尾 */
		if (!*p)
			break;

		/*---------------------------------------------------
		 * 处理注释
		 * 注释以#开头，延续到行末
		 *---------------------------------------------------*/
		if (*p == '#')
		{
			/* 跳过整行注释 */
			while (*p && *p != '\n')
				p++;
			continue; /* 不生成Token，继续处理 */
		}

		/*---------------------------------------------------
		 * 处理换行符
		 * 换行符在shell中有语义作用，需要生成TOKEN_NEWLINE
		 *---------------------------------------------------*/
		if (*p == '\n')
		{
			tok = token_create(TOKEN_NEWLINE, "\\n", line, col);
			p++;
			line++;	 /* 增加行号 */
			col = 1; /* 重置列号 */
		}
		/*---------------------------------------------------
		 * 处理分号 - 命令分隔符
		 * 例如: cmd1; cmd2
		 *---------------------------------------------------*/
		else if (*p == ';')
		{
			tok = token_create(TOKEN_SEMICOLON, ";", line, col);
			p++;
			col++;
		}
		/*---------------------------------------------------
		 * 处理管道符 | 和逻辑或 ||
		 *---------------------------------------------------*/
		else if (*p == '|')
		{
			if (*(p + 1) == '|')
			{
				/* || 逻辑或运算符 */
				tok = token_create(TOKEN_OR, "||", line, col);
				p += 2;
				col += 2;
			}
			else
			{
				/* | 管道运算符 */
				tok = token_create(TOKEN_PIPE, "|", line, col);
				p++;
				col++;
			}
		}
		/*---------------------------------------------------
		 * 处理& - 后台执行符和逻辑与
		 *---------------------------------------------------*/
		else if (*p == '&')
		{
			if (*(p + 1) == '&')
			{
				/* && 逻辑与运算符 */
				tok = token_create(TOKEN_AND, "&&", line, col);
				p += 2;
				col += 2;
			}
			else
			{
				/* & 后台执行 */
				tok = token_create(TOKEN_BACKGROUND, "&", line, col);
				p++;
				col++;
			}
		}
		/*---------------------------------------------------
		 * 处理输入重定向 <
		 *---------------------------------------------------*/
		else if (*p == '<')
		{
			tok = token_create(TOKEN_REDIRECT_IN, "<", line, col);
			p++;
			col++;
		}
		/*---------------------------------------------------
		 * 处理输出重定向 > 和追加重定向 >>
		 *---------------------------------------------------*/
		else if (*p == '>')
		{
			if (*(p + 1) == '>')
			{
				/* >> 追加重定向 */
				tok = token_create(TOKEN_REDIRECT_APPEND, ">>", line, col);
				p += 2;
				col += 2;
			}
			else
			{
				/* > 输出重定向 */
				tok = token_create(TOKEN_REDIRECT_OUT, ">", line, col);
				p++;
				col++;
			}
		}
		/*---------------------------------------------------
		 * 处理赋值运算符 =
		 *---------------------------------------------------*/
		else if (*p == '=')
		{
			tok = token_create(TOKEN_ASSIGN, "=", line, col);
			p++;
			col++;
		}
		/*---------------------------------------------------
		 * 处理引号字符串
		 * 支持单引号和双引号
		 *---------------------------------------------------*/
		else if (*p == '"' || *p == '\'')
		{
			char quote = *p;
			p = read_quoted_string(p, quote, buffer, sizeof(buffer));
			tok = token_create(TOKEN_WORD, buffer, line, col);
			col += strlen(buffer) + 2; /* 加上两个引号的长度 */
		}
		/*---------------------------------------------------
		 * 处理变量引用
		 * 支持: $var, ${var}, $((expr)), $?
		 *---------------------------------------------------*/
		else if (*p == '$')
		{
			int i = 0;
			buffer[i++] = *p++; /* 保存$ */
			col++;

			/* 处理 $((算术表达式)) 语法 */
			if (*p == '(' && *(p + 1) == '(')
			{
				int depth = 2; /* 括号深度 */
				buffer[i++] = *p++;
				buffer[i++] = *p++;
				col += 2;

				/* 读取直到匹配的 )) */
				while (*p && depth > 0 && i < MAX_TOKEN_LEN - 1)
				{
					if (*p == '(')
						depth++;
					else if (*p == ')')
					{
						depth--;
						buffer[i++] = *p++;
						col++;
						if (depth == 0)
							break;
						continue;
					}
					buffer[i++] = *p++;
					col++;
				}
			}
			/* 处理 ${var} 语法 */
			else if (*p == '{')
			{
				buffer[i++] = *p++;
				col++;
				/* 读取直到 } */
				while (*p && *p != '}' && i < MAX_TOKEN_LEN - 1)
				{
					buffer[i++] = *p++;
					col++;
				}
				if (*p == '}')
				{
					buffer[i++] = *p++;
					col++;
				}
			}
			/* 处理 $var 或 $? 语法 */
			else
			{
				/* 读取变量名（字母、数字、下划线、问号） */
				while (*p && (isalnum(*p) || *p == '_' || *p == '?') &&
					   i < MAX_TOKEN_LEN - 1)
				{
					buffer[i++] = *p++;
					col++;
				}
			}

			buffer[i] = '\0';
			tok = token_create(TOKEN_VARIABLE, buffer, line, col);
		}
		/*---------------------------------------------------
		 * 处理普通单词（命令、参数、文件名等）
		 *---------------------------------------------------*/
		else if (isalnum(*p) || *p == '_' || *p == '.' || *p == '/' ||
				 *p == '-' || *p == '[' || *p == ']')
		{
			const char *start = p;
			p = read_word(p, buffer, sizeof(buffer));

			/* 检查是否是关键字 */
			token_type_t type = lookup_keyword(buffer);
			tok = token_create(type, buffer, line, col);
			col += (p - start);
		}
		/*---------------------------------------------------
		 * 未知字符 - 跳过
		 *---------------------------------------------------*/
		else
		{
			p++;
			col++;
			continue; /* 不生成Token */
		}

		/*---------------------------------------------------
		 * 将Token添加到链表
		 *---------------------------------------------------*/
		if (tok)
		{
			if (!head)
			{
				/* 第一个Token */
				head = tail = tok;
			}
			else
			{
				/* 添加到链表尾部 */
				tail->next = tok;
				tail = tok;
			}
		}
	}

	/*---------------------------------------------------
	 * 添加EOF Token表示输入结束
	 *---------------------------------------------------*/
	tok = token_create(TOKEN_EOF, "", line, col);
	if (tok)
	{
		if (!head)
		{
			head = tail = tok;
		}
		else
		{
			tail->next = tok;
			tail = tok;
		}
	}

	return head; /* 返回Token链表头 */
}
