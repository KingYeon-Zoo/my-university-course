/*
 *  linux/lib/_exit.c
 *
 *  (C) 1991  Linus Torvalds
 */

#define __LIBRARY__				// 定义一个符号常量，见下行说明。
#include <unistd.h>				// Linux 标准头文件。定义了各种符号常数和类型，并申明了各种函数。
								// 如定义了__LIBRARY__，则还包括系统调用号和内嵌汇编_syscall0()等。

//// 内核使用的程序(退出)终止函数。
// 直接调用系统中断int 0x80，功能号__NR_exit。
// 参数：exit_code - 退出码。
volatile void _exit(int exit_code)
{	
	__asm("INT $0x03");
	// %0 - eax(系统调用号__NR_exit)；%1 - ebx(退出码exit_code)。
	__asm__("int $0x80"::"a" (__NR_exit),"b" (exit_code));
}
