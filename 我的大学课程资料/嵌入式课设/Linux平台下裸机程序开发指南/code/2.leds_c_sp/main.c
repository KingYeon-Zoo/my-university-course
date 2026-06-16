// 功能:c实现流水灯

// 延时
void delay()
{
	volatile int i = 0x10000;
	while (i--);
}

int main()
{
	int i = 0x10;

	// 配置引脚
	volatile unsigned long *gpkcon0 = (volatile unsigned long *)0x7F008800;
	volatile unsigned long *gpkdat = (volatile unsigned long *)0x7F008808;
	
	*gpkcon0 = 0x11110000;

	// 跑马灯
	while (1)
	{
		*gpkdat = i;
		i++;
		if (i == 0x100 )
			i = 0x10;
		delay();
	}
	
	return 0;
}

