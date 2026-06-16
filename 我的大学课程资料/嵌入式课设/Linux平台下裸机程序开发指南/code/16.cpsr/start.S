
.globl _start
_start:
	// 异常向量表
	b reset          		        	/* 复位时,cpu跳到0地址 */
	ldr 	pc, _undefined_instruction  /* 未定义指令异常 */
	ldr 	pc, _swi  		            /* swi异常，进入svc模式 */
	@ldr	pc, _prefetch_abort		 	/* 预取中止异常 */
	@ldr	pc, _data_abort     		/* 数据访问异常 */
	@ldr	pc, _not_used       		/* 没用到 */
	@ldr	pc, _irq            		/* 中断异常 */
	@ldr	pc, _fiq            		/* 快中断异常 */


reset:
	// 外设地址告诉cpu
    ldr r0, =0x70000000
    orr r0, r0, #0x13
    mcr p15,0,r0,c15,c2,4
    
	// 关看门狗
	ldr r0, =0x7E004000
	mov r1, #0
	str r1, [r0]
	
	// 设置栈
	ldr sp, =8*1024

	// 初始化时钟
	bl clock_init

	// 初始化ddr
	bl sdram_init

	// 初始化uart
	bl init_uart

	// 初始化nandflash
	bl nand_init

	// 重定位，把程序的代码段、数据段复制到它的链接地址去
	adr r0, _start   			
	ldr r1, =_start  			
	ldr r2, =bss_start      	
	sub r2, r2, r1
	cmp r0,r1
	beq clean_bss
	bl copy2ddr					
	cmp r0, #0
	bne halt

	// 清BSS，把BSS段对应的内存清零
clean_bss:
	ldr r0, =bss_start
	ldr r1, =bss_end
	mov r3, #0
	cmp r0, r1
	beq on_ddr
clean_loop:
	str r3, [r0], #4
	cmp r0, r1
	bne clean_loop

	// 跳转
	ldr pc, =on_ddr

on_ddr:	
	// 进入user 模式
	mrs r0, cpsr   
	bic	r0,r0,#0x1f
	orr	r0,r0,#0x10
	msr	cpsr,r0
	ldr sp, =0x57000000
	ldr r1, =usr_str
	bl print_cpsr
	

	// 进入svc 模式
	// cpu进入svc模式
	// 把之前的cpsr保存到spsr_svc
	// 切换到r13_svc, r14_svc
	// 把swi的下一条指令存到r14(lr)_svc
	// 跳到地址8
	swi 0


	 // cpu进入Undefined模式
	 // 把之前的cpsr保存到spsr_und
	 // 切换到r13_und, r14_und
	 // 把下一条指令存到r14(lr)_und
	 // 跳到地址4
undef:
	.word 0xff000000
	
	// 跳到main函数
	bl main
	
halt:
	b halt	


	// swi异常
_swi:
	.word swi
swi:
	/* 1. 保存现场 */
	ldr sp, =0x56000000
	stmdb sp!, {r0-r12, lr}		    /* lr就是swi的下一条指令地址 */
	/* 2. 处理异常 */
	mrs r0, cpsr
	ldr r1, =swi_str
	bl print_cpsr
	/* 3. 恢复现场 */
	ldmia sp!, {r0-r12, pc}^ 		/* ^表示把spsr恢复到cpsr */
swi_str:
	.word 0x00697773  				/* 字符串"swi" */


	// 未定义指令异常
_undefined_instruction:
	.word undefined_instruction
undefined_instruction:
	/* 1. 保存现场 */
	ldr sp, =0x55000000
	stmdb sp!, {r0-r12, lr}
	/* 2. 处理异常 */
	mrs r0, cpsr
	ldr r1, =und_str
	bl print_cpsr
	/* 3. 恢复现场 */
	ldmia sp!, {r0-r12, pc}^  		/* ^表示把spsr恢复到cpsr */
und_str:
	.word 0x00646e75  				/* 字符串"und" */


usr_str:
	.word 0x00727375  				/* 字符串"usr" */
