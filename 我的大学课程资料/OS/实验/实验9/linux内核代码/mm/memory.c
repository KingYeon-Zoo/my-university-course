/*
 *  linux/mm/memory.c
 *
 *  (C) 1991  Linus Torvalds
 */

/*
 * demand-loading started 01.12.91 - seems it is high on the list of
 * things wanted, and it should be easy to implement. - Linus
 */
/*
 * 按需加载是从01.12.91 开始编写的 - 在需求列表中似乎是最重要的程序，
 * 并且应该是很容易编制的 - linus
 */

/*
 * Ok, demand-loading was easy, shared pages a little bit tricker. Shared
 * pages started 02.12.91, seems to work. - Linus.
 *
 * Tested sharing by executing about 30 /bin/sh: under the old kernel it
 * would have taken more than the 6M I have free, but it worked well as
 * far as I could see.
 *
 * Also corrected some "invalidate()"s - I wasn't doing enough of them.
 */
/*
 * OK，按需加载是比较容易编写的，而共享页面却需要有点技巧。共享页面程序是
 * 02.12.91 开始编写的，好象能够工作 - Linus。
 *
 * 通过执行大约30 个/bin/sh 对共享操作进行了测试：在老内核当中需要占用多于
 * 6M 的内存，而目前却不用。现在看来工作得很好。
 *
 * 对"invalidate()"函数也进行了修正 - 在这方面我还做的不够。
 */


#include <signal.h>					// 信号头文件。定义信号符号常量，信号结构以及信号操作函数原型。

#include <asm/system.h>				// 系统头文件。定义了设置或修改描述符/中断门等的嵌入式汇编宏。

#include <linux/sched.h>			// 调度程序头文件，定义了任务结构task_struct、初始任务0 的数据，
									// 还有一些有关描述符参数设置和获取的嵌入式汇编函数宏语句。
#include <linux/head.h>				// head 头文件，定义了段描述符的简单结构，和几个选择符常量。
#include <linux/kernel.h>			// 内核头文件。含有一些内核常用函数的原形定义。


/*
定义了一个页表的缓冲区，大小为 8 * 1024 字节，可以用来存储页目录或页表中的数据。
其中只存储有效的页表项，从而可以大大加快获取页表的速度。
*/
struct page_table_entry
{
	unsigned long index;
	unsigned long pte;
};


unsigned long dir_entry_count; 
struct page_table_entry dir_table_buffer[64];

unsigned long page_entry_count; 
struct page_table_entry page_table_buffer[1024];
unsigned long cur_dir_entry_index = -1;

void vm()
{
	unsigned long i, pte;	
	unsigned long* page_dir_base = 0;

	dir_entry_count = 0;
	
	for(i = 0; i < 1024; i++)
	{
		pte = page_dir_base[i];
		
		/* 跳过无效的 PTE */
		if(!(pte & 1))
			continue;
			
		dir_table_buffer[dir_entry_count].index = i;
		dir_table_buffer[dir_entry_count].pte = pte;
		dir_entry_count++;
	}	
}

void vm2(unsigned long subscript)
{
	unsigned long i, pte;	
	unsigned long* page_table_base;

	vm();
	
	cur_dir_entry_index = subscript;
	for (i = 0; i < dir_entry_count; i++) {
		if (dir_table_buffer[i].index == subscript) {
			page_table_base = (unsigned long*)(dir_table_buffer[i].pte & 0xFFFFF000);
		}
	}
	
	page_entry_count = 0;
	
	for(i = 0; i < 1024; i++)
	{
		pte = page_table_base[i];
		
		/* 跳过无效的 PTE */
		if(!(pte & 1))
			continue;
			
		page_table_buffer[page_entry_count].index = i;
		page_table_buffer[page_entry_count].pte = pte;
		page_entry_count++;
	}	
}


/*
定义了一个全局描述符表的缓冲区，大小为 12 * 256 字节，可以用来存储全局描述符表中的数据。
其中只存储有效的表项，从而可以大大加快获取全局描述符表的速度。
*/
struct gdt_entry
{
	unsigned long index;
	unsigned long a;
	unsigned long b;
};

struct gdt_entry gdt_buffer[256];
unsigned long gdt_entry_count;

void showgdt()
{
	unsigned long i;
	
	gdt_entry_count = 0;
	
	for(i = 0; i < 256; i++)
	{
		if(!(gdt[i].b & 0x00008000) && i >= 4)
		{
			continue;			
		}
		
		gdt_buffer[gdt_entry_count].index = i;
		gdt_buffer[gdt_entry_count].a = gdt[i].a;
		gdt_buffer[gdt_entry_count].b = gdt[i].b;
		gdt_entry_count++;
	}
}

// 函数名前的关键字 volatile 用于告诉编译器 gcc 该函数不会返回。这样可让 gcc 产生更好一些的代码
// 更重要的是使用这个关键字可以避免产生某些（未初始化的变量）假警告信息。
volatile void do_exit(long code); 	// 进程退出处理函数。 在kernel/exit.c中。

// 显示内存已用完出错信息。并退出.
static inline volatile void oom(void)
{
	printk("out of memory\n\r");
	do_exit(SIGSEGV);				// do_exit()应该使用退出代码，这里用了信号值SIGSEGV(11)
}									// 相同值得出错码含义是“资源暂时不可用”，正好同义

// 刷新页变换高速缓冲宏函数。
// 为了提高地址转换的效率，CPU 将最近使用的页表数据存放在芯片高速缓冲中。在修改过
// 页表信息之后，就需要刷新该缓冲区。这里使用重新加载页目录基质寄存器cr3的方法来
// 进行刷新。下面 eax = 0，是页目录的基址。
#define invalidate() \
__asm__("movl %%eax,%%cr3"::"a" (0))

/* these are not to be changed without changing head.s etc */
/* 下面定义若需要改动，则需要与head.s 等文件中的相关信息一起改变 */
#define LOW_MEM 0x100000					// 内存低端（1MB）。
#define PAGING_MEMORY (15*1024*1024)		// 分页内存15MB。主内存区最多15M。
#define PAGING_PAGES (PAGING_MEMORY>>12)	// 分页后的物理内存页数。
#define MAP_NR(addr) (((addr)-LOW_MEM)>>12)	// 指定内存地址映射为页号。物理地址减去低端内存位置，再除以4KB，得页面号。
#define USED 100							// 页面被占用标志

// 该宏用于判断给定线性地址是否位于当前进程的代码段中
#define CODE_SPACE(addr) ((((addr)+4095)&~4095) < \
current->start_code + current->end_code)

static long HIGH_MEMORY = 0;				// 全局变量，存放实际物理内存最高端地址。

// 从 from 复制 1 页内存到 to 处(4K 字节）。
#define copy_page(from,to) \
__asm__("cld ; rep ; movsl"::"S" (from),"D" (to),"c" (1024))

// 内存映射字节图(1 字节代表1 页内存)，每个页面对应的字节用于标志页面当前被引用（占用）次数。
static unsigned char mem_map [ PAGING_PAGES ] = {0,};

// 取得内存映射字节图中的区块数据，在一个区块中的物理页是连续的，且引用次数相同。
struct used_page_section_entry
{
	unsigned long begin;
	unsigned long end;
	unsigned long ref;
};

#define MAX_SECTION_COUNT 32
struct used_page_section_entry used_page_section_table[MAX_SECTION_COUNT];
unsigned long used_page_section_count;
unsigned long free_page_count;

void pm()
{
	int i;
	
	used_page_section_count = 0;
	free_page_count = 0;
	
	for(i=0; i<PAGING_PAGES; i++)
	{
		if(mem_map[i])
		{
			if(used_page_section_count == MAX_SECTION_COUNT)
			{
				continue;
			}
			
			if(used_page_section_count == 0)
			{
				used_page_section_table[used_page_section_count].begin = i;
				used_page_section_table[used_page_section_count].end = i;
				used_page_section_table[used_page_section_count].ref = mem_map[i];
				used_page_section_count++;
			}
			else if(used_page_section_table[used_page_section_count - 1].ref == mem_map[i]
					&& i == used_page_section_table[used_page_section_count - 1].end + 1)
			{
				used_page_section_table[used_page_section_count - 1].end = i;
			}
			else
			{
				used_page_section_table[used_page_section_count].begin = i;
				used_page_section_table[used_page_section_count].end = i;
				used_page_section_table[used_page_section_count].ref = mem_map[i];
				used_page_section_count++;
			}
		}
		else
		{
			free_page_count++;
		}
	}
}

/*
 * Get physical address of first (actually last :-) free page, and mark it
 * used. If no free pages left, return 0.
 */
/*
 * 获取首个(实际上是最后1 个:-)空闲页面，并标记为已使用。如果没有空闲页面，
 * 就返回0。
 */
//// 在主内存中取空闲页面。如果已经没有可用内存了，则返回0。
// 输入：%1(ax=0) - 0；%2(LOW_MEM)；%3(cx=PAGING PAGES)；%4(edi=mem_map+PAGING_PAGES-1)。
// 输出：返回%0(ax=页面起始地址)。
// 上面%4 寄存器实际指向mem_map[]内存字节图的最后一个字节。本函数从字节图末端开始向前扫描
// 所有页面标志（页面总数为PAGING_PAGES），若有页面空闲（其内存映像字节为0）则返回页面地址。
// 注意！本函数只是指出在主内存区的一页空闲页面，但并没有映射到某个进程的线性地址去。后面
// 的put_page()函数就是用来作映射的。
unsigned long get_free_page(void)
{
	register unsigned long __res asm("ax");

	__asm__("std ; repne ; scasb\n\t"	// 方向位置位，将al(0)与对应每个页面的(di)内容比较，
	"jne 1f\n\t"						// 如果没有等于0的字节，则跳转结束（返回0）。
	"movb $1,1(%%edi)\n\t"				// 将对应页面内存映像比特位置1.
	"sall $12,%%ecx\n\t"				// 页面数*4K = 相对页面起始地址。	
	"addl %2,%%ecx\n\t"					// 再加上低端内存地址，即获得页面实际物理起始地址。
	"movl %%ecx,%%edx\n\t"				// 将页面实际起始地址->edx 寄存器。
	"movl $1024,%%ecx\n\t"				// 寄存器ecx 置计数值1024。
	"leal 4092(%%edx),%%edi\n\t"		// 将4092+edx 的位置->edi(该页面的末端)。
	"rep ; stosl\n\t"					// 将edi 所指内存清零（反方向，也即将该页面清零）。
	"movl %%edx,%%eax\n"				// 将页面起始地址->eax（返回值）。
	"1:"
	:"=a" (__res)
	:"0" (0), "i" (LOW_MEM), "c" (PAGING_PAGES), "D" (mem_map+PAGING_PAGES-1)
	);
	return __res;							// 返回空闲页面地址（如果无空闲页则返回0）。
}

/*
 * Free a page of memory at physical address 'addr'. Used by
 * 'free_page_tables()'
 */
/*
 * 释放物理地址'addr'开始的一页内存。用于函数'free_page_tables()'。
 */
//// 释放物理地址addr 开始的一页面内存。
// 物理地址 1MB 以下的内存空间用于内核程序和缓冲，不作为分配页面的内存空间。
// 因此参数 addr 需要大于 1MB
void free_page(unsigned long addr)
{
	unsigned long page_num;
	
	if (addr < LOW_MEM) return;		// 如果物理地址addr 小于内存低端（1MB），则返回。
	if (addr >= HIGH_MEMORY)		// 如果物理地址addr>=内存最高端，则显示出错信息。
		panic("trying to free nonexistent page");
	
	page_num = MAP_NR(addr);		// 从物理地址计算得到页面号。
	
	if (mem_map[page_num] > 0)		// 如果对应内存页面映射字节大于0，说明没有出现错误，可以返回。
	{
		mem_map[page_num]--;		// 对应内存页面映射字节(页面号引用计数)减 1。
		return;	
	}
	else
	{
		mem_map[page_num]=0;		// 否则置对应页面映射字节为0，并显示出错信息，死机。
		panic("trying to free free page");
	}
}

/*
 * This function frees a continuos block of page tables, as needed
 * by 'exit()'. As does copy_page_tables(), this handles only 4Mb blocks.
 */
/*
 * 下面函数释放页表连续的内存块，'exit()'需要该函数。与copy_page_tables()
 * 类似，该函数仅处理4Mb 的内存块。
 */
//// 根据指定的线性地址和限长（页表个数），释放对应内存页表所指定的内存块并置表项空闲。
// 页目录位于物理地址0 开始处，共1024 项，每项4字节，占4K 字节。每个目录项指定一个页表。
// 内核页表从物理地址0x1000 处开始（紧接着目录空间），共4个页表。每个页表有1024 项，每项占 4 字节。
// 也占4K 内存。每个页表项对应一页物理内存（4K）。因此一个页表最多可映射 4MB 物理内存。
// 参数：from - 起始基地址；size - 释放的长度。
int free_page_tables(unsigned long from,unsigned long size)
{
	unsigned long *pg_table;
	unsigned long * dir, nr;
	
	// 首先检测参数 from 给出的线性基地址是否在 4MB的边界处。因为该函数只能处理这种情况。
	if (from & 0x3fffff)
		panic("free_page_tables called with wrong alignment");
	// 若 from =0，则出错。说明试图释放内核和缓冲所占用的空间.
	if (!from)
		panic("Trying to free up swapper memory space");
	size = (size + 0x3fffff) >> 22;
	// 下面一句计算起始目录项。对应的目录项号=from>>22，因每项占4 字节，并且由于页目录是从
	// 物理地址0 开始，因此实际的目录项指针=目录项号<<2，也即(from>>20)。与上0xffc 确保
	// 目录项指针范围有效。
	dir = (unsigned long *) ((from>>20) & 0xffc); /* _pg_dir = 0 */
	for ( ; size-->0 ; dir++) {
		// size 现在是需要被释放内存的目录项数。
		if (!(1 & *dir))	// 如果该目录项无效(P 位=0)，则继续。
			continue;		// 目录项的位0(P 位)表示对应页表是否存在。
		pg_table = (unsigned long *) (0xfffff000 & *dir);	// 取目录项中页表地址。
		for (nr=0 ; nr<1024 ; nr++) {
			// 每个页表有1024 个页项。
			if (1 & *pg_table)		// 若该页表项有效(P 位=1)，则释放对应内存页。
				free_page(0xfffff000 & *pg_table);
			*pg_table = 0;			// 该页表项内容清零。
			pg_table++;				// 指向页表中下一项。
		}
		free_page(0xfffff000 & *dir);	// 释放该页表所占内存页面。但由于页表在
										// 物理地址1M 以内，所以这句什么都不做。
		*dir = 0;					// 对相应页表的目录项清零。
	}
	invalidate();					// 刷新页变换高速缓冲。
	return 0;
}

/*
 *  Well, here is one of the most complicated functions in mm. It
 * copies a range of linerar addresses by copying only the pages.
 * Let's hope this is bug-free, 'cause this one I don't want to debug :-)
 *
 * Note! We don't copy just any chunks of memory - addresses have to
 * be divisible by 4Mb (one page-directory entry), as this makes the
 * function easier. It's used only by fork anyway.
 *
 * NOTE 2!! When from==0 we are copying kernel space for the first
 * fork(). Then we DONT want to copy a full page-directory entry, as
 * that would lead to some serious memory waste - we just copy the
 * first 160 pages - 640kB. Even that is more than we need, but it
 * doesn't take any more memory - we don't copy-on-write in the low
 * 1 Mb-range, so the pages can be shared with the kernel. Thus the
 * special case for nr=xxxx.
 */
/*
 * 好了，下面是内存管理mm 中最为复杂的程序之一。它通过只复制内存页面
 * 来拷贝一定范围内线性地址中的内容。希望代码中没有错误，因为我不想
 * 再调试这块代码了?。
 *
 * 注意！我们并不是仅复制任何内存块 - 内存块的地址需要是4Mb 的倍数（正好
 * 一个页目录项对应的内存大小），因为这样处理可使函数很简单。不管怎样，
 * 它仅被fork()使用（fork.c 第56 行）。
 *
 * 注意2！！当from==0 时，是在为第一次fork()调用复制内核空间。此时我们
 * 不想复制整个页目录项对应的内存，因为这样做会导致内存严重的浪费 - 我们
 * 只复制头160 个页面 - 对应640kB。即使是复制这些页面也已经超出我们的需求，
 * 但这不会占用更多的内存 - 在低1Mb 内存范围内我们不执行写时复制操作，所以
 * 这些页面可以与内核共享。因此这是nr=xxxx 的特殊情况（nr 在程序中指页面数）。
 */
//// 复制指定线性地址和长度（页表个数）内存对应的页目录项和页表，从而被复制的页目录和
//// 页表对应的原物理内存区被共享使用。
// 复制指定地址和长度的内存对应的页目录项和页表项。需申请页面来存放新页表，原内存区被共享；
// 此后两个进程将共享内存区，直到有一个进程执行写操作时，才分配新的内存页（写时复制机制）。
int copy_page_tables(unsigned long from,unsigned long to,long size)
{
	unsigned long * from_page_table;
	unsigned long * to_page_table;
	unsigned long this_page;
	unsigned long * from_dir, * to_dir;
	unsigned long nr;

	// 源地址和目的地址都需要是在4Mb 的内存边界地址上。否则出错，死机。
	if ((from&0x3fffff) || (to&0x3fffff))
		panic("copy_page_tables called with wrong alignment");
	// 取得源地址和目的地址的目录项(from_dir 和to_dir)。
	from_dir = (unsigned long *) ((from>>20) & 0xffc); /* _pg_dir = 0 */
	to_dir = (unsigned long *) ((to>>20) & 0xffc);
	// 计算要复制的内存块占用的页表数（也即目录项数）。
	size = ((unsigned) (size+0x3fffff)) >> 22;
	// 下面开始对每个占用的页表依次进行复制操作。
	for( ; size-->0 ; from_dir++,to_dir++) {
		// 如果目的目录项指定的页表已经存在(P=1)，则出错，死机。
		if (1 & *to_dir)
			panic("copy_page_tables: already exist");
		// 如果此源目录项未被使用，则不用复制对应页表，跳过。
		if (!(1 & *from_dir))
			continue;
		// 取当前源目录项中页表的地址??from_page_table。
		from_page_table = (unsigned long *) (0xfffff000 & *from_dir);
		// 为目的页表取一页空闲内存，如果返回是0 则说明没有申请到空闲内存页面。返回值=-1，退出。
		if (!(to_page_table = (unsigned long *) get_free_page()))
			return -1;	/* Out of memory, see freeing */
		// 设置目的目录项信息。7 是标志信息，表示(Usr, R/W, Present)。
		*to_dir = ((unsigned long) to_page_table) | 7;
		// 针对当前处理的页表，设置需复制的页面数。如果是在内核空间，则仅需复制头160 页，否则需要
		// 复制1 个页表中的所有1024 页面。
		nr = (from==0)?0xA0:1024;
		// 对于当前页表，开始复制指定数目nr 个内存页面。
		for ( ; nr-- > 0 ; from_page_table++,to_page_table++) {
			this_page = *from_page_table;		// 取源页表项内容。
			if (!(1 & this_page))				// 如果当前源页面没有使用，则不用复制。
				continue;
			// 复位页表项中R/W 标志(置0)。(如果U/S 位是0，则R/W 就没有作用。如果U/S 是1，而R/W 是0，
			// 那么运行在用户层的代码就只能读页面。如果U/S 和R/W 都置位，则就有写的权限。)
			this_page &= ~2;
			*to_page_table = this_page;			// 将该页表项复制到目的页表中。
			// 如果该页表项所指页面的地址在1M 以上，则需要设置内存页面映射数组mem_map[]，于是计算
			// 页面号，并以它为索引在页面映射数组相应项中增加引用次数。
			if (this_page > LOW_MEM) {
				// 下面这句的含义是令源页表项所指内存页也为只读。因为现在开始有两个进程共用内存区了。
				// 若其中一个内存需要进行写操作，则可以通过页异常的写保护处理，为执行写操作的进程分配
				// 一页新的空闲页面，也即进行写时复制的操作。
				*from_page_table = this_page;	// 令源页表项也只读。
				this_page -= LOW_MEM;
				this_page >>= 12;
				mem_map[this_page]++;
			}
		}
	}
	invalidate();				// 刷新页变换高速缓冲。
	return 0;
}

/*
 * This function puts a page in memory at the wanted address.
 * It returns the physical address of the page gotten, 0 if
 * out of memory (either when trying to access page-table or
 * page.)
 */
/*
 * 下面函数将一内存页面放置在指定地址处。它返回页面的物理地址，如果
 * 内存不够(在访问页表或页面时)，则返回0。
 */
//// 把一物理内存页面映射到指定的线性地址处。
// 主要工作是在页目录和页表中设置指定页面的信息。若成功则返回页面地址。
unsigned long put_page(unsigned long page,unsigned long address)
{
	unsigned long tmp, *page_table;

	/* NOTE !!! This uses the fact that _pg_dir=0 */
	/* 注意!!!这里使用了页目录基址_pg_dir=0 的条件 */
	
	// 如果申请的页面位置低于LOW_MEM(1Mb)或超出系统实际含有内存高端HIGH_MEMORY，则发出警告。
	if (page < LOW_MEM || page >= HIGH_MEMORY)
		printk("Trying to put page %p at %p\n",page,address);
	// 如果申请的页面在内存页面映射字节图中没有置位，则显示警告信息。
	if (mem_map[(page-LOW_MEM)>>12] != 1)
		printk("mem_map disagrees with %p at %p\n",page,address);
	// 计算指定地址在页目录表中对应的目录项指针。
	page_table = (unsigned long *) ((address>>20) & 0xffc);
	// 如果该目录项有效(P=1)(也即指定的页表在内存中)，则从中取得指定页表的地址 page_table。
	if ((*page_table)&1)
		page_table = (unsigned long *) (0xfffff000 & *page_table);
	else {
	// 否则，申请空闲页面给页表使用，并在对应目录项中置相应标志7（User, U/S, R/W）。然后将
	// 该页表的地址page_table。
		if (!(tmp=get_free_page()))
			return 0;
		*page_table = tmp|7;
		page_table = (unsigned long *) tmp;
	}
	// 在页表中设置指定地址的物理内存页面的页表项内容。每个页表共可有1024 项(0x3ff)。
	page_table[(address>>12) & 0x3ff] = page | 7;
	/* no need for invalidate */
	/* 不需要刷新页变换高速缓冲 */
	return page;			// 返回页面地址。
}

//// 取消写保护页面函数。用于页异常中断过程中写保护异常的处理（写时复制）。
// 输入参数为页表项指针。
// [ un_wp_page 意思是取消页面的写保护：Un-Write Protected。]
void un_wp_page(unsigned long * table_entry)
{
	unsigned long old_page,new_page;

	old_page = 0xfffff000 & *table_entry;		// 取原页面对应的目录项号。
	// 如果原页面地址大于内存低端LOW_MEM(1Mb)，并且其在页面映射字节图数组中值为1（表示仅
	// 被引用1 次，页面没有被共享），则在该页面的页表项中置R/W 标志（可写），并刷新页变换
	// 高速缓冲，然后返回。
	if (old_page >= LOW_MEM && mem_map[MAP_NR(old_page)]==1) {
		*table_entry |= 2;
		invalidate();
		return;
	}
	// 否则，在主内存区内申请一页空闲页面。
	if (!(new_page=get_free_page()))
		oom();								// Out of Memory。内存不够处理。
	// 如果原页面大于内存低端（则意味着mem_map[]>1，页面是共享的），则将原页面的页面映射
	// 数组值递减1。然后将指定页表项内容更新为新页面的地址，并置可读写等标志(U/S, R/W, P)。
	// 刷新页变换高速缓冲。最后将原页面内容复制到新页面。
	if (old_page >= LOW_MEM)
		mem_map[MAP_NR(old_page)]--;
	*table_entry = new_page | 7;
	invalidate();
	copy_page(old_page,new_page);
}	

/*
 * This routine handles present pages, when users try to write
 * to a shared page. It is done by copying the page to a new address
 * and decrementing the shared-page counter for the old page.
 *
 * If it's in code space we exit with a segment error.
 */
/*
 * 当用户试图往一个共享页面上写时，该函数处理已存在的内存页面，（写时复制）
 * 它是通过将页面复制到一个新地址上并递减原页面的共享页面计数值实现的。
 *
 * 如果它在代码空间，我们就以段错误信息退出。
 */
//// 页异常中断处理调用的C 函数。写共享页面处理函数。在page.s 程序中被调用。
// 参数error_code 是由CPU 自动产生，address 是页面线性地址。
// 写共享页面时，需复制页面（写时复制）。
void do_wp_page(unsigned long error_code,unsigned long address)
{
#if 0
/* we cannot do this yet: the estdio library writes to code space */
/* stupid, stupid. I really want the libc.a from GNU */
/* 我们现在还不能这样做：因为estdio 库会在代码空间执行写操作 */
/* 真是太愚蠢了。我真想从GNU 得到libc.a 库。*/
	if (CODE_SPACE(address))
		do_exit(SIGSEGV);
#endif
// 处理取消页面保护。参数指定页面在页表中的页表项指针，其计算方法是：
// ((address>>10) & 0xffc)：计算指定地址的页面在页表中的偏移地址；
// (0xfffff000 &((address>>20) &0xffc))：取目录项中页表的地址值，
// 其中((address>>20) &0xffc)计算页面所在页表的目录项指针；
// 两者相加即得指定地址对应页面的页表项指针。这里对共享的页面进行复制。
	un_wp_page((unsigned long *)
		(((address>>10) & 0xffc) + (0xfffff000 &
		*((unsigned long *) ((address>>20) &0xffc)))));

}

//// 写页面验证。
// 若页面不可写，则复制页面。在fork.c 中被调用.
void write_verify(unsigned long address)
{
	unsigned long page;

	// 判断指定地址所对应页目录项的页表是否存在(P)，若不存在(P=0)则返回。
	if (!( (page = *((unsigned long *) ((address>>20) & 0xffc)) )&1))
		return;
	// 取页表的地址，加上指定地址的页面在页表中的页表项偏移值，得对应物理页面的页表项指针。
	page &= 0xfffff000;
	page += ((address>>10) & 0xffc);
	// 如果该页面不可写(标志R/W 没有置位)，则执行共享检验和复制页面操作（写时复制）。
	if ((3 & *(unsigned long *) page) == 1)  /* non-writeable, present */
		un_wp_page((unsigned long *) page);
	return;
}

//// 取得一页空闲内存并映射到指定线性地址处。
// 与get_free_page()不同。get_free_page()仅是申请取得了主内存区的一页物理内存。而该函数
// 不仅是获取到一页物理内存页面，还进一步调用put_page()，将物理页面映射到指定的线性地址
// 处。
void get_empty_page(unsigned long address)
{
	unsigned long tmp;
	
	// 若不能取得一空闲页面，或者不能将页面放置到指定地址处，则显示内存不够的信息。
	// 【标号1】处的英文注释的含义是：即使执行get_free_page()返回0 也无所谓，因为put_page()
	// 中还会对此情况再次申请空闲物理页面的。
	if (!(tmp=get_free_page()) || !put_page(tmp,address)) {
		free_page(tmp);		/* 0 is ok - ignored */ //【标号1】
		oom();
	}
}

/*
 * try_to_share() checks the page at address "address" in the task "p",
 * to see if it exists, and if it is clean. If so, share it with the current
 * task.
 *
 * NOTE! This assumes we have checked that p != current, and that they
 * share the same executable.
 */
/*
 * try_to_share()在任务"p"中检查位于地址"address"处的页面，看页面是否存在，是否干净。
 * 如果是干净的话，就与当前任务共享。
 *
 * 注意！这里我们已假定p !=当前任务，并且它们共享同一个执行程序。
 */
//// 尝试对进程指定地址处的页面进行共享操作。
// 同时还验证指定的地址处是否已经申请了页面，若是则出错，死机。
// 返回1-成功，0-失败。
static int try_to_share(unsigned long address, struct task_struct * p)
{
	unsigned long from;
	unsigned long to;
	unsigned long from_page;
	unsigned long to_page;
	unsigned long phys_addr;
	
	// 求指定内存地址的页目录项。
	from_page = to_page = ((address>>20) & 0xffc);
	// 计算进程p 的代码起始地址所对应的页目录项。
	from_page += ((p->start_code>>20) & 0xffc);
	// 计算当前进程中代码起始地址所对应的页目录项。
	to_page += ((current->start_code>>20) & 0xffc);
/* is there a page-directory at from? */
/* 在from 处是否存在页目录？*/
	// *** 对p 进程页面进行操作。
	// 取页目录项内容。如果该目录项无效(P=0)，则返回。否则取该目录项对应页表地址from。
	from = *(unsigned long *) from_page;
	if (!(from & 1))
		return 0;
	from &= 0xfffff000;
	// 计算地址对应的页表项指针值，并取出该页表项内容phys_addr。
	from_page = from + ((address>>10) & 0xffc);
	phys_addr = *(unsigned long *) from_page;
/* is the page clean and present? */
/* 页面干净并且存在吗？*/
	// 0x41 对应页表项中的Dirty 和Present 标志。如果页面不干净或无效则返回。
	if ((phys_addr & 0x41) != 0x01)
		return 0;
	// 取页面的地址phys_addr。如果该页面地址不存在或小于内存低端(1M)也返回退出。
	phys_addr &= 0xfffff000;
	if (phys_addr >= HIGH_MEMORY || phys_addr < LOW_MEM)
		return 0;
	// *** 对当前进程页面进行操作。
	// 取页目录项内容to。如果该目录项无效(P=0)，则取空闲页面，并更新to_page 所指的目录项。
	to = *(unsigned long *) to_page;
	if (!(to & 1)) {
		if ((to = get_free_page()))
			*(unsigned long *) to_page = to | 7;
		else
			oom();
	}
	// 取对应页表地址to，页表项地址to_page。如果对应的页面已经存在，则出错，死机。
	to &= 0xfffff000;
	to_page = to + ((address>>10) & 0xffc);
	if (1 & *(unsigned long *) to_page)
		panic("try_to_share: to_page already exists");
/* share them: write-protect */
/* 对它们进行共享处理：写保护 */
	// 对p 进程中页面置写保护标志(置R/W=0 只读)。并且当前进程中的对应页表项指向它。
	*(unsigned long *) from_page &= ~2;
	*(unsigned long *) to_page = *(unsigned long *) from_page;
	// 刷新页变换高速缓冲。
	invalidate();
	// 计算所操作页面的页面号，并将对应页面映射数组项中的引用递增1。
	phys_addr -= LOW_MEM;
	phys_addr >>= 12;
	mem_map[phys_addr]++;
	return 1;
}

/*
 * share_page() tries to find a process that could share a page with
 * the current one. Address is the address of the wanted page relative
 * to the current data space.
 *
 * We first check if it is at all feasible by checking executable->i_count.
 * It should be >1 if there are other tasks sharing this inode.
 */
/*
 * share_page()试图找到一个进程，它可以与当前进程共享页面。参数address 是
 * 当前数据空间中期望共享的某页面地址。
 *
 * 首先我们通过检测executable->i_count 来查证是否可行。如果有其它任务已共享
 * 该inode，则它应该大于1。
 */
//// 共享页面。在缺页处理时看看能否共享页面。
// 返回1 - 成功，0 - 失败。
static int share_page(unsigned long address)
{
	struct task_struct ** p;
	
	// 如果是不可执行的，则返回。excutable 是执行进程的内存i 节点结构。
	if (!current->executable)
		return 0;
	// 如果只能单独执行(executable->i_count=1)，也退出。
	if (current->executable->i_count < 2)
		return 0;
	// 搜索任务数组中所有任务。寻找与当前进程可共享页面的进程，并尝试对指定地址的页面进行共享。
	for (p = &LAST_TASK ; p > &FIRST_TASK ; --p) {
		if (!*p)				// 如果该任务项空闲，则继续寻找。
			continue;
		if (current == *p)		// 如果就是当前任务，也继续寻找。
			continue;
		if ((*p)->executable != current->executable)		// 如果executable 不等，也继续。
			continue;
		if (try_to_share(address,*p))						// 尝试共享页面。
			return 1;
	}
	return 0;
}

//// 页异常中断处理调用的函数。处理缺页异常情况。在page.s 程序中被调用。
// 参数error_code 是由CPU 自动产生，address 是页面线性地址。
void do_no_page(unsigned long error_code,unsigned long address)
{
	int nr[4];
	unsigned long tmp;
	unsigned long page;
	int block,i;

	address &= 0xfffff000;				// 页面地址。
	// 首先算出指定线性地址在进程空间中相对于进程基址的偏移长度值。
	tmp = address - current->start_code;
	// 若当前进程的executable 空，或者指定地址超出代码+数据长度，则申请一页物理内存，并映射
	// 影射到指定的线性地址处。executable 是进程的i 节点结构。该值为0，表明进程刚开始设置，
	// 需要内存；而指定的线性地址超出代码加数据长度，表明进程在申请新的内存空间，也需要给予。
	// 因此就直接调用get_empty_page()函数，申请一页物理内存并映射到指定线性地址处即可。
	// start_code 是进程代码段地址，end_data 是代码加数据长度。对于linux 内核，它的代码段和
	// 数据段是起始基址是相同的。
	if (!current->executable || tmp >= current->end_data) {
		get_empty_page(address);
		return;
	}
	// 如果尝试共享页面成功，则退出。
	if (share_page(tmp))
		return;
	// 取空闲页面，如果内存不够了，则显示内存不够，终止进程。
	if (!(page = get_free_page()))
		oom();
/* remember that 1 block is used for header */
/* 记住，（程序）头要使用1 个数据块 */
	// 首先计算缺页所在的数据块项。BLOCK_SIZE = 1024 字节，因此一页内存需要4 个数据块。
	block = 1 + tmp/BLOCK_SIZE;
	// 根据i 节点信息，取数据块在设备上的对应的逻辑块号。
	for (i=0 ; i<4 ; block++,i++)
		nr[i] = bmap(current->executable,block);
	// 读设备上一个页面的数据（4 个逻辑块）到指定物理地址page 处。
	bread_page(page,current->executable->i_dev,nr);
	// 在增加了一页内存后，该页内存的部分可能会超过进程的end_data 位置。下面的循环即是对物理
	// 页面超出的部分进行清零处理。
	i = tmp + 4096 - current->end_data;
	tmp = page + 4096;
	while (i-- > 0) {
		tmp--;
		*(char *)tmp = 0;
	}
	// 如果把物理页面映射到指定线性地址的操作成功，就返回。否则就释放内存页，显示内存不够。
	if (put_page(page,address))
		return;
	free_page(page);
	oom();
}

//// 物理内存初始化。
// 参数：start_mem - 可用作分页处理的物理内存起始位置（已去除RAMDISK 所占内存空间等）。
// end_mem - 实际物理内存最大地址。
// 在该版的linux 内核中，最多能使用16Mb 的内存，大于16Mb 的内存将不于考虑，弃置不用。
// 0 - 1Mb 内存空间用于内核系统（其实是0-640Kb）。
void mem_init(long start_mem, long end_mem)
{
	int i;

	HIGH_MEMORY = end_mem;				// 设置内存最高端。
  	for (i = 0; i < PAGING_PAGES; i++)	// 首先置所有页面为已占用(USED=100)状态，
    	mem_map[i] = USED;				// 即将页面映射数组全置成USED。
  	i = MAP_NR (start_mem);				// 然后计算可使用起始内存的页面号。
  	end_mem -= start_mem;				// 再计算可分页处理的内存块大小。
  	end_mem >>= 12;						// 从而计算出可用于分页处理的页面数。
  	while (end_mem-- > 0)				// 最后将这些可用页面对应的页面映射数组清零。
    	mem_map[i++] = 0;
}

// 计算内存空闲页面数并显示。
void calc_mem(void)
{
	int i,j,k,free=0;
	long * pg_tbl;

	// 扫描内存页面映射数组mem_map[]，获取空闲页面数并显示。
	for(i=0 ; i<PAGING_PAGES ; i++)
		if (!mem_map[i]) free++;
	printk("%d pages free (of %d)\n\r",free,PAGING_PAGES);
	// 扫描所有页目录项（除0，1 项），如果页目录项有效，则统计对应页表中有效页面数，并显示。
	for(i=2 ; i<1024 ; i++) {
		if (1&pg_dir[i]) {
			pg_tbl=(long *) (0xfffff000 & pg_dir[i]);
			for(j=k=0 ; j<1024 ; j++)
				if (pg_tbl[j]&1)
					k++;
			printk("Pg-dir[%d] uses %d pages\n",i,k);
		}
	}
}
