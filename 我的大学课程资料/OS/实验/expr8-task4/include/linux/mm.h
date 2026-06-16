#ifndef _MM_H
#define _MM_H

#define PAGE_SIZE 4096		// 定义内存页面的大小(字节数)。

/* these are not to be changed without changing head.s etc */
/* 下面定义若需要改动，则需要与head.s 等文件中的相关信息一起改变 */
#define LOW_MEM 0x100000					// 内存低端（1MB）。
#define PAGING_MEMORY (15*1024*1024)		// 分页内存15MB。主内存区最多15M。
#define PAGING_PAGES (PAGING_MEMORY>>12)	// 分页后的物理内存页数。
#define MAP_NR(addr) (((addr)-LOW_MEM)>>12)	// 指定内存地址映射为页号。物理地址减去低端内存位置，再除以4KB，得页面号。
#define USED 100							// 页面被占用标志

// 取空闲页面函数。返回页面地址。扫描页面映射数组mem_map[]取空闲页面。
extern unsigned long get_free_page (void);
// 在指定物理地址处放置一页面。在页目录和页表中放置指定页面信息。
extern unsigned long put_page (unsigned long page, unsigned long address);
// 释放物理地址addr 开始的一页面内存。修改页面映射数组mem_map[]中引用次数信息。
extern void free_page (unsigned long addr);
extern unsigned char mem_map [];

#endif
