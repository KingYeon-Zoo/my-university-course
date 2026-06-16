#include "stdio.h"

// GPIO和按键硬件寄存器定义
#define GPNCON (*(volatile unsigned long *)0x7F008830)  // GPN端口配置寄存器
#define GPNDAT (*(volatile unsigned long *)0x7F008834)  // GPN端口数据寄存器
#define GPKCON0 (*(volatile unsigned long *)0x7F008800)  // GPK端口配置寄存器  
#define GPKDATA (*(volatile unsigned long *)0x7F008808)  // GPK端口数据寄存器

// LED状态定义
#define LED_OFF 0  // LED熄灭状态
#define LED_ON 1   // LED点亮状态

// 中断服务函数类型定义
typedef void (isr)(void);
extern void asm_timer_irq();

// 函数声明
void timer_init(unsigned long timer_id, unsigned long prescaler_val, unsigned long divider_val, unsigned long count_buffer, unsigned long compare_buffer);
void delay_ms(int ms);
int ifpress(int id);

// 全局变量
extern int digit_units, digit_tens, digit_hundreds, digit_thousands;  // 四位数字：个位、十位、百位、千位
extern int interrupt_mode;    // 中断状态控制变量
extern int combined_value;       // 组合后的完整四位数字
extern int low_digits_counter;   // LED闪烁计数（用于低两位显示）
extern int blink_counter[4]; // 每个LED的闪烁次数数组
extern int led_status[4]; // 每个LED的当前状态数组
extern int current_led_index;    // 跑马灯当前LED索引
extern int marquee_direction;    // 跑马灯方向

int key_check_state[] = { 0,0,0,0 };  // 按键状态检查数组
int led_status[4] = { LED_OFF, LED_OFF, LED_OFF, LED_OFF };  // LED初始状态

/*
 * 计算每个LED需要闪烁的次数
 */
void ledcount_cal()
{
	blink_counter[0]=digit_units;      // LED1闪烁个位次数
	blink_counter[1]=digit_tens;      // LED2闪烁十位次数
	blink_counter[2]=digit_hundreds;  // LED3闪烁百位次数
	blink_counter[3]=digit_thousands; // LED4闪烁千位次数
}

/*
 * 计算完整的四位数字和低两位数字
 */
void cal_num()
{	
	combined_value=1000*digit_thousands+100*digit_hundreds+10*digit_tens+digit_units;  // 计算完整四位数
	low_digits_counter=10*digit_tens+digit_units;  // 计算低两位数
}

/*
 * 粗延时函数
 */
void delay(volatile unsigned int delay_count) {
	while (delay_count--) {
		delay_ms(0x7ff);
	}
}

/*
 * 毫秒级延时函数
 */
void delay_ms(int milliseconds)   
{
	int x;
	for (x = 0; x < milliseconds; x++)
	{
	}
}

/*
 * 按键引脚初始化
 */
void key_init(void)  
{
	// 配置GPN为输入功能 - K1-K4按键连接
	GPNCON = 0;
	// 配置GPK4-GPK7为输出功能 - LED1-LED4连接
	GPKCON0 = 0x11110000;
	// 初始化GPK数据寄存器
	GPKDATA = 0xff;
}

/*
 * 带消抖的按键检测函数
 */
int check(int key_id)
{
	delay(10000);  // 软件消抖延时
	if (ifpress(key_id)) {return 1;}
	else return 0;
}

/*
 * 直接按键状态检测函数
 */
int ifpress(int key_id)
{
	int gpio_data = GPNDAT;  // 读取GPN数据寄存器
	return ((gpio_data & (1 << key_id)) == 0);  // 检测对应位是否为0
}

/*
 * 主函数
 */
int main()
{
	key_init();  // 初始化按键和LED引脚
	
	while (1) {  
		// K1按键处理 - 个位数字+1或千位数字+1
		if (check(0)) //按下K1
		{
			int is_single_key = 1;  // 标记是否为单独按K1
			while (check(0))  // K1持续按下期间
			{
				if (check(1)) // 检测是否同时按下K2
				{
					while (check(1)) {}  // 等待K2释放
					is_single_key = 0;  // 标记为组合按键
					digit_thousands++;  // 千位数字+1
				}
			}
			if (is_single_key) digit_units++;  // 单独按K1，个位数字+1
			cal_num();      // 重新计算数字
			ledcount_cal(); // 重新计算LED闪烁次数
		}
		
		// K2按键处理 - 十位数字+1或百位数字+1
		if (check(1)) //按下K2
		{
			int is_single_key = 1;  // 标记是否为单独按K2
			while (check(1))  // K2持续按下期间
			{
				if (check(0)) // 检测是否同时按下K1
				{
					while (check(0)) {
					}
					is_single_key = 0;  // 标记为组合按键
					digit_hundreds++;  // 百位数字+1
				}
			}
			if (is_single_key) digit_tens++;  // 单独按K2，十位数字+1
			cal_num();      // 重新计算数字
			ledcount_cal(); // 重新计算LED闪烁次数
		}
		
		// K3按键处理 - 数字显示或清零操作
		if (check(2))
		{	
			int is_single_key=1;  // 标记是否为单独按K3
			while (check(2))  // K3持续按下期间
			{	
				if (check(3))  // 检测是否同时按下K4
				{
					// 清零所有数字
					digit_units=0;digit_tens=0;digit_hundreds=0;digit_thousands=0;
					combined_value=0;
					ledcount_cal();
					is_single_key=0;
					interrupt_mode=1;  // 设置为清零闪烁状态
					timer_init(0, 65, 4, 31250, 0);  // 0.5秒定时器
				}
			}
			if(is_single_key){
				// 单独按K3：显示当前数字
				interrupt_mode=2;  // 设置为数字显示状态
				ledcount_cal();
				timer_init(0, 65, 4, 62500, 0);  // 1秒定时器
			}
		}
		
		// K4按键处理 - 数字比较和LED显示模式控制
		if (check(3)){
			while (check(3))	
				{check(3);}  // 等待K4释放			
			// 将数字对24取模，判断是否为24的倍数
                        while(combined_value>=24)
                              {
                                combined_value-=24;  // 对24取模运算
                               }
			
			if (combined_value == 0)  // 如果是24的倍数
			{
				current_led_index = 0;  // 重置跑马灯起始位置
				marquee_direction = 1;  // 重置方向为正向
				interrupt_mode = 3;  // 双向跑马灯显示状态
				timer_init(0, 65, 4, 62500, 0);  // 1秒定时器
			}				
			else {
				interrupt_mode = 4;  // 闪烁低两位数字状态  
				timer_init(0, 65, 4,125000, 0);  // 2秒定时器
			}
		}
	}
	return 0;
}

