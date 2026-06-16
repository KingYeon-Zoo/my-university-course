.global _start

_start:
	// 把外设的基地址告诉CPU
    ldr r0, =0x70000000 					//对于6410来说,内存(0x00000000～0x60000000),外设(0x70000000-0x7fffffff)
    orr r0, r0, #0x13						//外设大小:256M
    mcr p15,0,r0,c15,c2,4       			//把r0的值(包括了外设基地址+外设大小)告诉cpu
    
	// 关看门狗
	ldr r0, =0x7E004000
	mov r1, #0
	str r1, [r0] 

	// 设置栈指针
	ldr sp, =0x50000000

	// 调用C语言主函数
	bl main

halt:
	b halt 