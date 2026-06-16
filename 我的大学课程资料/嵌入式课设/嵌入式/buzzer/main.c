#include "stdio.h"
#include "buzzer.h"

void init_uart(void);

int main()
{
	char c;
	
	init_uart();

	printf("hello, world\n\r");

	// 初始化buzzer
	buzzer_init();

	while (1)
	{

				// 打开蜂鸣器
				buzzer_on();
				break;
	}
	
	return 0;
}
