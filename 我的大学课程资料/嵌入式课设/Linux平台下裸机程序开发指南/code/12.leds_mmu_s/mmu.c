
#define ENABLE_DCACHE_ICACHE  0
#define REGISTER_USE_CACHE    0

// 页表基址
#define MMU_BASE  0x51000000


#define MMU_FULL_ACCESS       (3 << 10)  /* 访问权限 */
#define MMU_DOMAIN            (0 << 5)   /* 属于哪个域 */
#define MMU_SPECIAL           (1 << 4)   /* bit 4必须是1 */
#define MMU_CACHEABLE         (1 << 3)   /* 可以使用cache */
#define MMU_BUFFERABLE        (1 << 2)   /* 可以使用write buffer */
#define MMU_SECDESC           (2)        /* 表示这是段描述符 */

#define MMU_SECDESC_WB        (MMU_FULL_ACCESS | MMU_DOMAIN | \
	                           MMU_SPECIAL | MMU_CACHEABLE | \
	                           MMU_BUFFERABLE | MMU_SECDESC)

#define MMU_SECDESC_NCNB       (MMU_FULL_ACCESS | MMU_DOMAIN | \
	                           MMU_SPECIAL | MMU_SECDESC)

extern void mmu_enable(unsigned long table);

// 初始化mmu
void mmu_init(void)
{
	volatile unsigned long *table = (volatile unsigned long *)MMU_BASE;

	// 建立页表项
	table[0x100]   = 0x7f000000 | MMU_SECDESC_NCNB;  /* va: 0x10000000 => pa: 0x7f000000 */
	table[0]     = 0 | MMU_SECDESC_WB;  		   /* MMU使能前后的代码所在的空间, 保持它们的虚拟地址等于物理地址 */
	table[0xc00] = 0x50000000 | MMU_SECDESC_WB;    /* va: 0xc0000000 => pa: 0x50000000 */

	// 启动mmu
	mmu_enable((unsigned long)table);
}

