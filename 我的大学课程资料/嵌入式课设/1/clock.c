/*
 * 系统时钟初始化
 * 功能：配置ARM处理器（S3C6410）的系统时钟
 */

// 锁相环锁定时间寄存器定义
#define APLL_LOCK (*((volatile unsigned long *)0x7E00F000))  // APLL锁定时间寄存器
#define MPLL_LOCK (*((volatile unsigned long *)0x7E00F004))  // MPLL锁定时间寄存器  
#define EPLL_LOCK (*((volatile unsigned long *)0x7E00F008))  // EPLL锁定时间寄存器

// 系统控制寄存器
#define OTHERS    (*((volatile unsigned long *)0x7e00f900))  // 其他控制寄存器

// 时钟分频寄存器
#define CLK_DIV0  (*((volatile unsigned long *)0x7E00F020))  // 时钟分频控制寄存器0

// 时钟分频比例定义
#define ARM_RATIO    0   // ARMCLK分频比：532MHz
#define MPLL_RATIO   0   // MPLL分频比：532MHz
#define HCLKX2_RATIO 1   // HCLKX2分频比：266MHz
#define HCLK_RATIO   1   // HCLK分频比：133MHz
#define PCLK_RATIO   3   // PCLK分频比：66.5MHz

// 锁相环控制寄存器和配置值定义
#define APLL_CON  (*((volatile unsigned long *)0x7E00F00C))  // APLL控制寄存器
#define APLL_CON_VAL  ((1<<31) | (250 << 16) | (3 << 8) | (1))  // APLL配置值

#define MPLL_CON  (*((volatile unsigned long *)0x7E00F010))  // MPLL控制寄存器  
#define MPLL_CON_VAL  ((1<<31) | (250 << 16) | (3 << 8) | (1))  // MPLL配置值

// 时钟源选择寄存器
#define CLK_SRC  (*((volatile unsigned long *)0x7E00F01C))  // 时钟源选择寄存器

/*
 * 初始化系统时钟
 */
void clock_init(void)
{	
	// 设置各PLL的锁定时间
	APLL_LOCK = 0xffff;		// APLL锁定时间
	MPLL_LOCK = 0xffff;		// MPLL锁定时间
	EPLL_LOCK = 0xffff;		// EPLL锁定时间

	// 设置为异步模式
	OTHERS &= ~0xc0;		// 设置为异步模式
	while ((OTHERS & 0xf00) != 0);	// 等待模式切换完成

	// 设置分频系数
	CLK_DIV0 = (ARM_RATIO) | (MPLL_RATIO << 4) | (HCLK_RATIO << 8) | (HCLKX2_RATIO << 9) | (PCLK_RATIO << 12);

	// 设置PLL配置，启动时钟倍频
	APLL_CON = APLL_CON_VAL;	// 配置APLL
	MPLL_CON = MPLL_CON_VAL;	// 配置MPLL

	// 选择PLL输出作为系统时钟源
	CLK_SRC = 0x03;	// 选择PLL输出作为时钟源
}

