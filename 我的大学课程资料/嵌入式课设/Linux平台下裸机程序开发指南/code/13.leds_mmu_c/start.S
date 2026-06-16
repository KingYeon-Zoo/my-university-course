// 启动代码
.global _start
_start:

	// 把外设的基地址告诉CPU
	ldr r0, =0x70000000
    orr r0, r0, #0x13
    mcr p15,0,r0,c15,c2,4       @ 256M(0x70000000-0x7fffffff)
    
	// 关看门狗
	ldr r0, =0x7E004000
	mov r1, #0
	str r1, [r0]

	// 设置栈
	ldr sp, =8*1024

	// 初始化时钟
	bl clock_init

	// 初始化内存
	bl sdram_init

	// 重定位
	bl copy2ddr

	// 初始化mmu
	bl mmu_init  
	
	// 跳转
	ldr pc, =main
halt:
	b halt	
