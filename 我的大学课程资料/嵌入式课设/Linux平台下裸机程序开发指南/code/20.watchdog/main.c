#include "stdio.h"

void init_uart();
void wtd_operate(unsigned long uenreset, unsigned long uenint, unsigned long uselectclk, unsigned long uenwtd, unsigned long uprescaler,unsigned long uwtdat, unsigned long uwtcnt);

void delay()
{
	volatile int i = 0x100000;
	while (i--);
}

int main()
{
	int i = 0;
	init_uart();

	// 测试看门狗的定时功能
	wtd_operate(0,1,0,1,100,100000,100000);

	printf("\r\n\r\n#############watchdog test#############\r\n");
	while (1)
	{
		printf("%d\r\n",i++);
		delay();
	}
	
	return 0;
}
