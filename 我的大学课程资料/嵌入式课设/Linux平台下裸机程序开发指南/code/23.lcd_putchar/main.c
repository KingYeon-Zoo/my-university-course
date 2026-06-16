#include "stdio.h"
#include "lcd.h"

#define WIDTHEIGHT	480
#define HEIGHT	272
void init_uart();

int main(void)
{
	init_uart();

	lcd_init();

	lcd_clear_screen(0x000000);

	printf("LOVE LINUX FOREVER\r\n");
	printf("[1] lcd_clear_screen\r\n");
	printf("[2] lcd_draw_cross\r\n");
	printf("[3] lcd_draw_hline\r\n");
	printf("[4] lcd_draw_vline\r\n");
	printf("[5] lcd_draw_circle\r\n");
	printf("Enter your choice:\r\n");
	while(1);
}
