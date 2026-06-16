#define ENABLE_DCACHE_ICACHE  0

	// 把页表项的基地址告诉MMU,启动MMU
.globl mmu_enable
mmu_enable:
	// 使无效cache/TLB
	mov r1, #0
	mcr p15, 0, r1, c7, c7, 0  		/* 使无效ICaches和DCaches */
	mcr p15, 0, r1, c7, c10, 4   	/* drain write buffer on v4 */
	mcr p15, 0, r1, c8, c7, 0    	/* 使无效指令、数据TLB */

	// 将页表基址告诉mmu
	mcr p15, 0, r0, c2, c0, 0 		/* write TTB register,r0为页表基址 */

	// 设置域
	mrc p15, 0, r1, c3, c0, 0 		/* read domain 15:0 access permissions */
	orr r1, r1, #3            		/* domain 0, Accesses are not checked */
	mcr p15, 0, r1, c3, c0, 0 		/* write domain 15:0 access permissions */

	// 使能icaches/dchaces
	mrc p15, 0, r1, c1, c0, 0 		/* Read control register */
#if ENABLE_DCACHE_ICACHE
	orr r1, r1, #(1<<2)    		     /* Data cache enable */
	orr r1, r1, #(1<<12)   		     /* Instruction cache enable */
	orr r1, r1, #(1<<14)   		   	 /* Round robin replacement */
#endif

	// 使能mmu
	orr r1, r1, #(1<<0)     		 /* MMU enable */
	mcr p15,0,r1,c1, c0,0   		 /* write control register */

	// 返回
	mov pc, lr

