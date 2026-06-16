// 启动代码
.global _start
.global delay

_start:

	// 把外设的基地址告诉CPU
    ldr r0, =0x70000000 					
    orr r0, r0, #0x13					
    mcr p15,0,r0,c15,c2,4       		
    
	// 关看门狗
	ldr r0, =0x7E004000
	mov r1, #0
	str r1, [r0] 
	
	// 设置栈
	ldr sp, =0X0C002000
	
	// 调用C函数点灯
	bl main

	// 延时函数
delay:
delay_loop:		
	cmp r0, #0
	sub r0, r0, #1
	bne delay_loop
	mov pc, lr
	
