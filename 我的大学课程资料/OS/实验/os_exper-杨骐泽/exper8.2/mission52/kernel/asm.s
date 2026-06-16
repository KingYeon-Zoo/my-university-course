/*
 *  linux/kernel/asm.s
 *
 *  (C) 1991  Linus Torvalds
 */

/*
 * asm.s contains the low-level code for most hardware faults.
 * page_exception is handled by the mm, so that isn't here. This
 * file also handles (hopefully) fpu-exceptions due to TS-bit, as
 * the fpu must be properly saved/resored. This hasn't been tested.
 */
/*
 * asm.s 程序中包括大部分的硬件故障（或出错）处理的底层次代码。页异常是由内存管理程序
 * mm 处理的，所以不在这里。此程序还处理（希望是这样）由于TS-位而造成的fpu 异常，
 * 因为fpu 必须正确地进行保存/恢复处理，这些还没有测试过。
 */
 
# 本代码文件主要涉及对Intel 保留的中断int0--int16 的处理（int17-int31 留作今后使用）。
# 以下是一些全局函数名的声明，其原形在traps.c 中说明。
.globl _divide_error,   _debug,   _nmi,    _int3,       _overflow,_bounds,_invalid_op
.globl _double_fault,   _coprocessor_segment_overrun
.globl _invalid_TSS,    _segment_not_present,           _stack_segment
.globl _general_protection,  _coprocessor_error,_irq13, _reserved

# 下面这段程序处理无出错的情况
# int0-- 处理被零除出错的情况。 类型：错误；错误号：无
# 在执行 DIV 或 IDIV 指令时，若除数是 0，CPU 就会产生这个异常，当 EAX （或AX , AL)容纳不了
# 一个合法除操作的结果时也会产生这个异常。标号‘_do_divide_error’实际上是 C 语言函数
# ‘do_divide_error()’编译后所生产模块中对应的函数。函数‘do_divide_error’在trap.c中实现

_divide_error:
	pushl $_do_divide_error		# 首先把将要调用的函数地址入栈。这段程序的出错号为0。
no_error_code:					# 这里是无出错号处理的入口处
	xchgl %eax,(%esp)			# _do_divide_error 的地址 -> eax，eax 被交换入栈。
	pushl %ebx
	pushl %ecx
	pushl %edx
	pushl %edi
	pushl %esi
	pushl %ebp
	push %ds					# 16 位的段寄存器入栈后也要占用4 个字节。
	push %es
	push %fs
	pushl $0	# "error code"  # 将出错码入栈。
	lea 44(%esp),%edx			# 取原调用返回地址处堆栈指针位置，并压入堆栈。
	pushl %edx
	movl $0x10,%edx				# 初始化段寄存器，内核代码数据段选择符。
	mov %dx,%ds
	mov %dx,%es
	mov %dx,%fs
	call *%eax					# 调用C 函数do_divide_error()。
	addl $8,%esp				# 相当于执行两次pop操作，即丢弃最后入栈的两个 C 函数参数，
								# 让堆栈指针重新指向寄存器fs 入栈处。
	pop %fs
	pop %es
	pop %ds
	popl %ebp
	popl %esi
	popl %edi
	popl %edx
	popl %ecx
	popl %ebx
	popl %eax					# 弹出原来eax 中的内容。	
	iret

# int1 -- debug 调试中断入口点。处理过程同上。
_debug:
	pushl $_do_int3		# _do_debug
	jmp no_error_code

# int2 -- 非屏蔽中断调用入口点。
_nmi:
	pushl $_do_nmi
	jmp no_error_code

# int3 -- 断点指令引起中断的入口点
_int3:
	pushl $_do_int3
	jmp no_error_code

# int4 -- 溢出出错处理中断入口点。
_overflow:
	pushl $_do_overflow
	jmp no_error_code

# int5 -- 边界检查出错中断入口点。
_bounds:
	pushl $_do_bounds
	jmp no_error_code

# int6 -- 无效操作指令出错中断入口点。
_invalid_op:
	pushl $_do_invalid_op
	jmp no_error_code

# int9 -- 协处理器段超出出错中断入口点。
_coprocessor_segment_overrun:
	pushl $_do_coprocessor_segment_overrun
	jmp no_error_code

# int15 – 保留。
_reserved:
	pushl $_do_reserved
	jmp no_error_code

# int45 -- ( = 0x20 + 13 ) 数学协处理器（Coprocessor）发出的中断。
# 当协处理器执行完一个操作时就会发出IRQ13 中断信号，以通知CPU 操作完成。
_irq13:
	pushl %eax
	xorb %al,%al				# 80387 在执行计算时，CPU 会等待其操作的完成。
	outb %al,$0xF0				# 通过写0xF0 端口，本中断将消除CPU 的BUSY 延续信号，并重新
								# 激活80387 的处理器扩展请求引脚PEREQ。该操作主要是为了确保
								# 在继续执行80387 的任何指令之前，响应本中断。
	movb $0x20,%al
	outb %al,$0x20				# 向8259 主中断控制芯片发送EOI（中断结束）信号。
	jmp 1f						# 这两个跳转指令起延时作用。
1:	jmp 1f
1:	outb %al,$0xA0				# 再向8259 从中断控制芯片发送EOI（中断结束）信号。
	popl %eax
	jmp _coprocessor_error		# _coprocessor_error 原来在本文件中，现在已经放到system_call.s中

# 以下中断在调用时会在中断返回地址之后将出错号压入堆栈，因此返回时也需要将出错号弹出。


_double_fault:
	pushl $_do_double_fault		# C 函数地址入栈。
error_code:
	xchgl %eax,4(%esp)		# error code <-> %eax # error code <-> %eax，eax 原来的值被保存在堆栈上。
	xchgl %ebx,(%esp)		# &function <-> %ebx  # &function <-> %ebx，ebx 原来的值被保存在堆栈上。
	pushl %ecx
	pushl %edx
	pushl %edi
	pushl %esi
	pushl %ebp
	push %ds
	push %es
	push %fs
	pushl %eax				# error code  # 出错号入栈。
	lea 44(%esp),%eax		# offset	  # 程序返回地址处堆栈指针位置值入栈。
	pushl %eax
	movl $0x10,%eax			# 置内核数据段选择符。
	mov %ax,%ds
	mov %ax,%es
	mov %ax,%fs
	call *%ebx				# 调用相应的C 函数，其参数已入栈。
	addl $8,%esp			# 堆栈指针重新指向栈中放置fs 内容的位置。
	pop %fs
	pop %es
	pop %ds
	popl %ebp
	popl %esi
	popl %edi
	popl %edx
	popl %ecx
	popl %ebx
	popl %eax
	iret

# int10 -- 无效的任务状态段(TSS)。
_invalid_TSS:
	pushl $_do_invalid_TSS
	jmp error_code

# int11 -- 段不存在。
_segment_not_present:
	pushl $_do_segment_not_present
	jmp error_code

# int12 -- 堆栈段错误。
_stack_segment:
	pushl $_do_stack_segment
	jmp error_code

# int13 -- 一般保护性出错。
_general_protection:
	pushl $_do_general_protection
	jmp error_code


# int7 -- 设备不存在(_device_not_available)在(kernel/system_call.s)
# int14 -- 页错误(_page_fault)在(mm/page.s)
# int16 -- 协处理器错误(_coprocessor_error)在(kernel/system_call.s)
# 时钟中断int 0x20 (_timer_interrupt)在(kernel/system_call.s)
# 系统调用int 0x80 (_system_call)在（kernel/system_call.s）
