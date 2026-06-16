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
		// 打印蜂鸣器测试菜单
		printf("\r\n\r\n###############Buzzer Test###############\r\n");
		printf("[n]buzzer on\r\n");
		printf("[f]buzzer off\r\n");
		printf("Enter your choice:");
		c = getc();
		printf("%c\r\n",c);
		switch(c)
		{
			case 'n':
				// 打开蜂鸣器
				buzzer_on();
				break;
			case 'f':
				// 关闭蜂鸣器
				buzzer_off();
				break;
		}
	}
	
	return 0;
}
