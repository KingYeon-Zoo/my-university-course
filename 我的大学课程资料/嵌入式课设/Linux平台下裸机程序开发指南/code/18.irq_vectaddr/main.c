#include "stdio.h"

void init_uart();

void delay()
{
	volatile int i = 0x100000;
	while (i--);
}

int main()
{
	int i = 0;

	init_uart();

	printf("\r\n\r\n#############irq_vectaddr test#############\r\n");
	while (1)
	{
		printf("%d\r\n",i++);
		delay();
	}

	return 0;
}
