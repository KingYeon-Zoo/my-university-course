void delay()
{
	volatile int i = 0x10000;
	while (i--);
}

int main()
{
	int i = 0;
	
	// 虚拟地址
	volatile unsigned long *gpkcon0 = (volatile unsigned long *)0x10008800;
	volatile unsigned long *gpkdat = (volatile unsigned long *)0x10008808;
	
	*gpkcon0 = (*gpkcon0 & ~(0xffff<<16)) | (0x1111<<16);
	
	while (1)
	{
		*gpkdat = (*gpkdat & ~(0xf<<4)) | (i<<4);
		i++;
		if (i == 16)
			i = 0;
		delay(0x10000);
	}
	
	return 0;
}

