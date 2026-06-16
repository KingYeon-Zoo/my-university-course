// 启动代码
.global _start

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
	ldr sp, =8*1024
	
	// 开启icaches
#ifdef  CONFIG_SYS_ICACHE_OFF
	bic r0, r0, #0x00001000 				@ clear bit 12 (I) I-cache
#else
	orr r0, r0, #0x00001000 				@ set bit 12 (I) I-cache
#endif
	mcr p15, 0, r0, c1, c0, 0

	// 设置时钟
	bl clock_init

	// 重定位
	adr r0, _start  						
	ldr r1, =_start 						
	ldr r2, =bss_start
	cmp r0, r1
	beq clean_bss
copy_loop:
	ldr r3, [r0], #4
	str r3, [r1], #4
	cmp r1, r2
	bne copy_loop
		
	// 清BSS段
clean_bss:
	ldr r0, =bss_start
	ldr r1, =bss_end
	mov r2, #0
	cmp r0, r1
	beq on_ddr
clean_loop:
	str r2, [r0], #4
	cmp r0, r1
	bne clean_loop	

on_ddr:
	// 调用main函数
	ldr pc, =main

halt:
	b halt	
