/*
 *  linux/kernel/printk.c
 *
 *  (C) 1991  Linus Torvalds
 */

/*
 * When in kernel-mode, we cannot use printf, as fs is liable to
 * point to 'interesting' things. Make a printf with fs-saving, and
 * all is well.
 */
/*
 * 当处于内核模式时，我们不能使用printf，因为寄存器fs 指向其它不感兴趣的地方。
 * 自己编制一个printf 并在使用前保存fs，一切就解决了。
 */
#include <stdarg.h>			// 标准参数头文件。以宏的形式定义变量参数列表。主要说明了-个
							// 类型(va_list)和三个宏(va_start, va_arg 和va_end)，用于
							// vsprintf、vprintf、vfprintf 函数。
#include <stddef.h>			// 标准定义头文件。定义了NULL, offsetof(TYPE, MEMBER)。

#include <linux/kernel.h>	// 内核头文件。含有一些内核常用函数的原形定义。

static char buf[1024];

// 下面该函数vsprintf()在linux/kernel/vsprintf.c 中
extern int vsprintf(char * buf, const char * fmt, va_list args);

// 内核使用的显示函数。
int printk(const char *fmt, ...)
{
	va_list args;
	int i;

	va_start (args, fmt);				// 参数处理开始函数。在（include/stdarg.h）
  	i = vsprintf (buf, fmt, args);		// 使用格式串fmt 将参数列表args 输出到buf 中。
										// 返回值i 等于输出字符串的长度。
  	va_end (args);						// 参数处理结束函数。
 	 __asm__ ("push %%fs\n\t"			// 保存fs。
	   	"push %%ds\n\t" "pop %%fs\n\t"	// 令fs = ds。
	  	"pushl %0\n\t"					// 将字符串长度压入堆栈(这三个入栈是调用参数)。
	   	"pushl $_buf\n\t"				// 将buf 的地址压入堆栈。
	   	"pushl $0\n\t"					// 将数值0 压入堆栈。是通道号channel。
	   	"call _tty_write\n\t"			// 调用tty_write 函数。(kernel/chr_drv/tty_io.c)。
	   	"addl $8,%%esp\n\t"				// 跳过（丢弃）两个入栈参数(buf,channel)。
	   	"popl %0\n\t"					// 弹出字符串长度值，作为返回值。
	   	"pop %%fs"						// 恢复原fs 寄存器。
	::"r" (i):"ax", "cx", "dx");		// 通知编译器，寄存器ax,cx,dx 值可能已经改变。
  return i;								// 返回字符串长度。
}

#include<linux/sched.h>
#include<sys/stat.h>

static char logbuf[1024];

int fprintk( int fd, const char * fmt, ... )
{
	va_list args;
	int i;
	struct file * file;
	struct m_inode * inode;
	va_start (args, fmt);		
  	i = vsprintf (logbuf, fmt, args);
  	va_end (args);
  	
  	if( fd<3 )
  	{
  		__asm__ ("push %%fs\n\t"		
	   	"push %%ds\n\t"
	   	"pop %%fs\n\t"	
	  	"pushl %0\n\t"					
	   	"pushl $_logbuf\n\t"			
	   	"pushl %1\n\t"					
	   	"call _sys_write\n\t"			
	   	"addl $8,%%esp\n\t"				
	   	"popl %0\n\t"					
	   	"pop %%fs"						
		::"r" (i),"r" (fd):"ax",  "dx");
  	}
  	else
  	{
  		if( !( file=task[0]->filp[fd] ) )
  			return 0;
  		inode=file->f_inode;
  		__asm__ ("push %%fs\n\t"		
	   	"push %%ds\n\t"
	   	"pop %%fs\n\t"	
	  	"pushl %0\n\t"					
	   	"pushl $_logbuf\n\t"			
	   	"pushl %1\n\t"					
	   	"pushl %2\n\t"					
	   	"call _file_write\n\t"			
	   	"addl $12,%%esp\n\t"			
	   	"popl %0\n\t"					
	   	"pop %%fs"						
		::"r" (i), "r" (file), "r" (inode)   );	
  	}
  	return i;// 返回字符串长度
}

