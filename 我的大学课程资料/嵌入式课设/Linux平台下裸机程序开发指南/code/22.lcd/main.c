#include "stdio.h"
#include "lcd.h"

#define WIDTHEIGHT	480
#define HEIGHT	272

void init_uart();

int main(void)
{
	int c = 0;

	init_uart();
	
	// 初始化LCD控制器
	lcd_init();

	// 打印菜单
	while(1)
	{
		printf("\r\n###############lcd test##############\r\n");
		printf("[1] lcd_clear_screen\r\n");
		printf("[2] lcd_draw_cross\r\n");
		printf("[3] lcd_draw_hline\r\n");
		printf("[4] lcd_draw_vline\r\n");
		printf("[5] lcd_draw_circle\r\n");
		printf("Enter your choice:");
		c = getc();
		printf("%c\r\n",c);
		switch(c)
		{
		case '1':
			// 清屏
			lcd_clear_screen(0xFFFFFF);
			break;
		case '2':
			// 划十字
			lcd_draw_cross(50, 50, 20, 0x000000);
			break;
		case '3':
			// 划横线
			lcd_draw_hline(HEIGHT/2, 100, WIDTHEIGHT-100, 0xff0000);
			break;
		case '4':
			// 划竖线
			lcd_draw_vline(WIDTHEIGHT/2, 50, HEIGHT-50, 0xff0000);
			break;
		case '5':
			// 划圆
			lcd_draw_circle();
			break;
		}
	}
	return 0;
}
