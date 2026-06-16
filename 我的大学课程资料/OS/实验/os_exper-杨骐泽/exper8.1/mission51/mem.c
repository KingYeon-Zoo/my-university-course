int physical_mem()
{
	int i, free=0;	/* free表示空闲页的总数 */

	__asm("cli");
	
	/* PAGING_PAGES 是在本文件第 137 行处定义，表示分页后的物理内存页数。*/
	/* mem_map[] 是在第 152 行定义的内存映射字节图(1 字节代表 1 页内存)，
		每个页面对应的字节用于标志页面当前被引用（占用）次数。*/
	for(i=0 ; i<PAGING_PAGES ; i++)
	{
		if (0 == mem_map[i])
		{
			free++;
		}
	}
	
	printk("Page Count : %d\n", PAGING_PAGES);
	printk("Memory Count : %d * 4096 = %d Byte\n\n", PAGING_PAGES, PAGING_PAGES * 4096);
	
	printk("Free Page Count : %d\n", free);
	printk("Used Page Count : %d\n", PAGING_PAGES - free);
	
	__asm("sti");
	
	return 0;
}

