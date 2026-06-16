#include "stdio.h"

void init_uart();
int read_adc(int ch);

void delay(volatile int count)
{
	while (count--);
}

int main(void)
{
	init_uart();
	
	printf("\r\n##################adc test################\r\n");
	while(1)
	{
		printf("adc = %d\r\n",read_adc(0));
		delay(0x100000);
	}
}
