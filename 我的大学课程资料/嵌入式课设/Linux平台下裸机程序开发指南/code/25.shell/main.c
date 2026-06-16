#include "stdio.h"
#include "command.h"
#include "uart.h"
#include "lcd.h"

#define WIDTHEIGHT	480
#define HEIGHT	272

int shell_parse(char * buf, char * argv[]);

int main(void)
{
	char buf[64];
	int argc = 0;
	char * argv[10];

	init_uart();

	// 初始化LCD
	lcd_init();

	printf("\r\n");
	while (1)
		{
			printf("Tiny6410: ");
			gets(buf);								// 等待用户输入命令

			argc = shell_parse(buf, argv);			// 解析命令

			command_do(argc, argv);					// 运行命令
		}
}
