/*
 * io_redirect.c - I/O重定向实现模块
 *
 * 本文件实现了标准输入/输出/错误的重定向功能。
 *
 * I/O重定向是shell的核心功能之一，允许:
 * - 将命令的输入从文件读取（< file）
 * - 将命令的输出写入文件（> file）
 * - 将命令的输出追加到文件（>> file）
 *
 * 实现原理:
 * 1. 保存原始的文件描述符（stdin=0, stdout=1, stderr=2）
 * 2. 打开重定向目标文件
 * 3. 使用dup2将文件描述符复制到标准描述符
 * 4. 执行命令
 * 5. 恢复原始的文件描述符
 *
 * 文件描述符说明:
 * - 0 (stdin):  标准输入，默认从键盘读取
 * - 1 (stdout): 标准输出，默认输出到屏幕
 * - 2 (stderr): 标准错误，默认输出到屏幕
 */

#include "include/types.h"	  /* 数据结构定义 */
#include "include/internal.h" /* 内部接口定义 */
#include <windows.h>		  /* Windows API */
#include <io.h>				  /* _open, _close, _dup, _dup2 */
#include <fcntl.h>			  /* _O_RDONLY, _O_WRONLY等文件标志 */
#include <sys/stat.h>		  /* _S_IREAD, _S_IWRITE文件权限 */

/*
 * setup_redirects - 设置I/O重定向
 *
 * @redirects: 重定向信息链表（可以包含多个重定向）
 * @saved_fds: 输出参数，保存原始文件描述符，用于后续恢复
 *             saved_fds[0] = 原始stdin
 *             saved_fds[1] = 原始stdout
 *             saved_fds[2] = 原始stderr
 * @返回值: 成功返回0，失败返回-1
 *
 * 支持的重定向类型:
 * - TOKEN_REDIRECT_IN (<):   输入重定向，从文件读取
 * - TOKEN_REDIRECT_OUT (>):  输出重定向，写入文件（覆盖）
 * - TOKEN_REDIRECT_APPEND (>>): 追加重定向，追加到文件末尾
 *
 * 使用示例:
 *   int saved_fds[3];
 *   if (setup_redirects(cmd->redirects, saved_fds) == 0) {
 *       // 执行命令，此时I/O已重定向
 *       execute_command(...);
 *       restore_redirects(saved_fds);  // 恢复原始I/O
 *   }
 */
int setup_redirects(struct redirect_info *redirects, int *saved_fds)
{
	struct redirect_info *redir = redirects;
	int fd;

	/* 初始化保存的文件描述符为-1（表示未保存） */
	saved_fds[0] = -1; /* stdin 未保存 */
	saved_fds[1] = -1; /* stdout 未保存 */
	saved_fds[2] = -1; /* stderr 未保存 */

	/* 遍历重定向链表，处理每个重定向 */
	while (redir)
	{
		if (redir->type == TOKEN_REDIRECT_IN)
		{
			/*
			 * 输入重定向: < file
			 * 将stdin重定向到文件
			 */

			/* 以只读方式打开文件 */
			fd = _open(redir->filename, _O_RDONLY);
			if (fd < 0)
				return -1; /* 文件打开失败 */

			/* 保存原始的stdin（如果尚未保存） */
			saved_fds[0] = _dup(0);

			/* 将打开的文件复制到stdin(0) */
			_dup2(fd, 0);

			/* 关闭原始文件描述符（已复制到0） */
			_close(fd);
		}
		else if (redir->type == TOKEN_REDIRECT_OUT)
		{
			/*
			 * 输出重定向: > file
			 * 将stdout重定向到文件（覆盖模式）
			 */

			/* 以写入方式打开文件，如果不存在则创建，如果存在则清空 */
			fd = _open(redir->filename,
					   _O_WRONLY | _O_CREAT | _O_TRUNC,
					   _S_IREAD | _S_IWRITE);
			if (fd < 0)
				return -1; /* 文件打开/创建失败 */

			/* 保存原始的stdout（如果尚未保存） */
			saved_fds[1] = _dup(1);

			/* 将打开的文件复制到stdout(1) */
			_dup2(fd, 1);

			/* 关闭原始文件描述符 */
			_close(fd);
		}
		else if (redir->type == TOKEN_REDIRECT_APPEND)
		{
			/*
			 * 追加重定向: >> file
			 * 将stdout重定向到文件（追加模式）
			 */

			/* 以追加方式打开文件，如果不存在则创建 */
			fd = _open(redir->filename,
					   _O_WRONLY | _O_CREAT | _O_APPEND,
					   _S_IREAD | _S_IWRITE);
			if (fd < 0)
				return -1; /* 文件打开/创建失败 */

			/* 保存原始的stdout（如果尚未保存） */
			saved_fds[1] = _dup(1);

			/* 将打开的文件复制到stdout(1) */
			_dup2(fd, 1);

			/* 关闭原始文件描述符 */
			_close(fd);
		}

		/* 移动到下一个重定向 */
		redir = redir->next;
	}

	return 0; /* 设置成功 */
}

/*
 * restore_redirects - 恢复原始的文件描述符
 *
 * @saved_fds: setup_redirects保存的原始文件描述符数组
 *
 * 此函数将stdin/stdout/stderr恢复到重定向之前的状态。
 * 必须在命令执行完毕后调用，否则后续命令的I/O会出问题。
 *
 * 工作流程:
 * 1. 检查saved_fds[n]是否有效（>= 0）
 * 2. 如果有效，使用dup2将保存的描述符恢复到标准位置
 * 3. 关闭保存的描述符
 */
void restore_redirects(int *saved_fds)
{
	/* 恢复stdin（如果之前保存了） */
	if (saved_fds[0] >= 0)
	{
		_dup2(saved_fds[0], 0); /* 恢复stdin */
		_close(saved_fds[0]);	/* 关闭保存的副本 */
	}

	/* 恢复stdout（如果之前保存了） */
	if (saved_fds[1] >= 0)
	{
		_dup2(saved_fds[1], 1); /* 恢复stdout */
		_close(saved_fds[1]);	/* 关闭保存的副本 */
	}

	/* 恢复stderr（如果之前保存了） */
	if (saved_fds[2] >= 0)
	{
		_dup2(saved_fds[2], 2); /* 恢复stderr */
		_close(saved_fds[2]);	/* 关闭保存的副本 */
	}
}
