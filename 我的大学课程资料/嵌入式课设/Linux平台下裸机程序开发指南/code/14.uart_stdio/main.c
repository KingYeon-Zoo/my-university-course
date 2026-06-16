#include "stdio.h"

void init_uart(void);

int main()
{
	int a, b;
	
	init_uart();

	printf("hello, world\n\r");

	while (1)
	{
		printf("please enter two number: \n\r");
		scanf("%d %d", &a, &b);
		printf("\n\r");
		printf("the sum is: %d\n\r", a+b);
	}
	
	return 0;
}
