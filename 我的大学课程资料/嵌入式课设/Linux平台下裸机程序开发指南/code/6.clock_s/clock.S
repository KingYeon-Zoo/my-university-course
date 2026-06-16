// 功能:汇编初始化时钟
.global clock_init

clock_init:
	// 1. 设置各PLL的LOCK_TIME,使用默认值  
	ldr r0, =0x7E00F000  						// APLL_LOCK，供cpu使用 
	ldr r1, =0x0000FFFF
	str r1, [r0]
	
	str r1, [r0, #4]	 						// MPLL_LOCK，供AHB(存储/中断/lcd等控制器)/APB(看门狗，定时器，SD等)总线上的设备使用 
	str r1, [r0, #8]	 						// EPLL_LOCK，供UART,IIS,IIC使用 
	
	// 2. 设置为异步模式(Asynchronous mode)  
	ldr r0, =0x7E00F900							// OTHERS
												// 《linux installation for u-boot》3.7中：用MPLL作为HCLK和PCLK的Source是异步(ASYNC)模式
												// 用APLL是同步(SYNC)模式
	ldr r1, [r0]
	bic r1, r1, #0xc0							// bit[6:7]清0,即SYNCMODE=0/SYNCMUXSEL=0
	str r1, [r0]
loop:			
	ldr r0, =0x7E00F900
	ldr r1, [r0]
	and r1, r1, #0xf00					
	cmp r1, #0
	bne loop		
	
	// 3. 设置分频系数  
#define ARM_RATIO    0   						// ARMCLK 	= DOUTAPLL / (ARM_RATIO + 1)  	= 532/(0+1) = 532  MHz
#define MPLL_RATIO   0   						// DOUTMPLL = MOUTMPLL / (MPLL_RATIO + 1)   = 532/(0+1) = 532  MHz
#define HCLKX2_RATIO 1   						// HCLKX2 	= HCLKX2IN / (HCLKX2_RATIO + 1) = 532/(1+1) = 266  MHz
#define HCLK_RATIO   1   						// HCLK 	= HCLKX2   / (HCLK_RATIO + 1)   = 266/(1+1) = 133  MHz
#define PCLK_RATIO   3   						// PCLK   	= HCLKX2   / (PCLK_RATIO + 1)   = 266/(3+1) = 66.5 MHz

	ldr r0, =0x7E00F020  						// CLK_DIV0
	ldr r1, =(ARM_RATIO) | (MPLL_RATIO << 4) | (HCLK_RATIO << 8) | (HCLKX2_RATIO << 9) | (PCLK_RATIO << 12)
	str r1, [r0]
	
	// 4. 设置PLL,放大时钟  
	// 4.1 配置APLL  
#define APLL_CON_VAL  ((1<<31) | (266 << 16) | (3 << 8) | (1))
	ldr r0, =0x7E00F00C							// APLL_CON
	ldr r1, =APLL_CON_VAL						// FOUT = MDIV X FIN / (PDIV X 2SDIV) = 266*12/(3*2^1) = 532MHz
	str r1, [r0]		
	
	// 4.2 配置MPLL  
#define MPLL_CON_VAL  ((1<<31) | (266 << 16) | (3 << 8) | (1))
	ldr r0, =0x7E00F010							// MPLL_CON
	ldr r1, =MPLL_CON_VAL						// FOUT = MDIV X FIN / (PDIV X 2SDIV) = 266*12/(3*2^1) = 532MHz
	str r1, [r0]		

#define MPLL_SEL 1
#define APLL_SEL 1	
	// 5.选择PLL的输出作为时钟源  
	ldr r0, =0x7E00F01C							// CLK_SRC
	ldr r1, =(MPLL_SEL<<1) | (APLL_SEL<<0)
	str r1, [r0]
	
	mov pc, lr

