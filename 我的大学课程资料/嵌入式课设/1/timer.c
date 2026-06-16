#include "stdio.h"

// GPIO寄存器定义 - LED控制
#define GPKCON0     		(*((volatile unsigned long *)0x7F008800))  // GPK配置寄存器
#define GPKDATA     		(*((volatile unsigned long *)0x7F008808))  // GPK数据寄存器

// 外部中断寄存器定义
#define EINT0CON0  			(*((volatile unsigned long *)0x7F008900))  // 外部中断0配置
#define EINT0MASK  			(*((volatile unsigned long *)0x7F008920))  // 外部中断0屏蔽
#define EINT0PEND  			(*((volatile unsigned long *)0x7F008924))  // 外部中断0挂起

// 中断控制器寄存器定义
#define PRIORITY 	    	(*((volatile unsigned long *)0x7F008280))  // 中断优先级
#define SERVICE     		(*((volatile unsigned long *)0x7F008284))  // 中断服务
#define SERVICEPEND 		(*((volatile unsigned long *)0x7F008288))  // 中断服务挂起

// VIC（向量中断控制器）寄存器定义
#define VIC0IRQSTATUS  		(*((volatile unsigned long *)0x71200000))  // IRQ状态寄存器
#define VIC0FIQSTATUS  		(*((volatile unsigned long *)0x71200004))  // FIQ状态寄存器
#define VIC0RAWINTR    		(*((volatile unsigned long *)0x71200008))  // 原始中断寄存器
#define VIC0INTSELECT  		(*((volatile unsigned long *)0x7120000c))  // 中断选择寄存器
#define VIC0INTENABLE  		(*((volatile unsigned long *)0x71200010))  // 中断使能寄存器
#define VIC0INTENCLEAR 		(*((volatile unsigned long *)0x71200014))  // 中断清除寄存器
#define VIC0PROTECTION 		(*((volatile unsigned long *)0x71200020))  // 中断保护寄存器
#define VIC0SWPRIORITYMASK 	(*((volatile unsigned long *)0x71200024))  // 软件优先级屏蔽
#define VIC0PRIORITYDAISY  	(*((volatile unsigned long *)0x71200028))  // 优先级菊花链
#define VIC0ADDRESS        	(*((volatile unsigned long *)0x71200f00))  // 中断地址寄存器

// PWM定时器寄存器定义
#define		PWMTIMER_BASE			(0x7F006000)  // PWM定时器基地址
#define		TCFG0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x00)) )  // 定时器配置0
#define		TCFG1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x04)) )  // 定时器配置1
#define		TCON      	( *((volatile unsigned long *)(PWMTIMER_BASE+0x08)) )  // 定时器控制
#define		TCNTB0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x0C)) )  // 定时器0计数缓冲
#define		TCMPB0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x10)) )  // 定时器0比较缓冲
#define		TCNTO0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x14)) )  // 定时器0计数观察
#define		TCNTB1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x18)) )  // 定时器1计数缓冲
#define		TCMPB1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x1C)) )  // 定时器1比较缓冲
#define		TCNTO1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x20)) )  // 定时器1计数观察
#define		TCNTB2    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x24)) )  // 定时器2计数缓冲
#define		TCMPB2    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x28)) )  // 定时器2比较缓冲
#define		TCNTO2    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x2C)) )  // 定时器2计数观察
#define		TCNTB3    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x30)) )  // 定时器3计数缓冲
#define		TCMPB3    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x34)) )  // 定时器3比较缓冲
#define		TCNTO3    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x38)) )  // 定时器3计数观察
#define		TCNTB4    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x3C)) )  // 定时器4计数缓冲
#define		TCNTO4    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x40)) )  // 定时器4计数观察
#define		TINT_CSTAT 	( *((volatile unsigned long *)(PWMTIMER_BASE+0x44)) )  // 定时器中断状态

// LED和显示控制常量定义
#define LED_OFF 0      // LED熄灭状态
#define LED_ON 1       // LED点亮状态
#define LED_COUNT 4    // LED总数量
#define FORWARD 1      // 跑马灯正向
#define BACKWARD 0     // 跑马灯反向

// 中断服务函数类型定义
typedef void (isr) (void);
extern void asm_timer_irq();

// 全局变量 - 系统状态和LED控制
int interrupt_mode;         // 中断状态控制：0-空闲,1-清零闪烁,2-数字显示,3-跑马灯,4-低位闪烁
int digit_units;              // 个位数字
int digit_tens;              // 十位数字  
int digit_hundreds;          // 百位数字
int digit_thousands;         // 千位数字
int combined_value;            // 完整四位数字

/*
 * 初始化中断控制器和GPIO
 */
void irq_init(void)
{
	/* 在中断控制器里使能timer0中断 */
	VIC0INTENABLE |= (1<<23);  // 使能VIC0的23号中断（定时器0）

	VIC0INTSELECT =0;  // 设置为IRQ中断（非FIQ）

	// 设置中断向量表，将定时器0中断指向asm_timer_irq
	isr** isr_array = (isr**)(0x7120015C);
	isr_array[0] = (isr*)asm_timer_irq;

	/*将GPK4-GPK7配置为输出口 - LED1-LED4连接*/
	GPKCON0 = 0x11110000;  // 配置GPK4-GPK7为输出功能
	
	/*熄灭四个LED灯 - 初始状态*/
	GPKDATA = 0xef;  // 设置GPK4-GPK7为高电平（LED熄灭）
}

// LED显示控制变量
int clear_blink_counter = 0;    // 清零时的闪烁计数器
int all_led_status = 0;     // 清零时所有LED的状态

int led_status[4];       // 每个LED的当前状态数组
int blink_counter[4];       // 每个LED需要闪烁的剩余次数数组

int current_led_index = 0;      // 跑马灯当前点亮的LED索引（0-3）
int marquee_direction = FORWARD; // 跑马灯当前方向

int low_digits_status = LED_OFF; // 低位闪烁时LED的状态
int low_digits_counter;           // 低位闪烁的剩余次数

/*
 * 定时器0中断服务程序
 * 根据interrupt_mode的值执行不同的LED显示逻辑
 */
void do_irq()
{
	// 状态0：系统空闲状态
	if (interrupt_mode == 0)
	{
		TCON &= ~(1<<0)|(1<<3);  // 停止定时器0运行
	}
	// 状态1：清零闪烁状态
	else if (interrupt_mode == 1)
	{
		if (clear_blink_counter < 3 ) {  // 闪烁3次
			if (all_led_status == 0) {
				GPKDATA &= ~0xf0;  // 点亮所有LED
				all_led_status = 1;
			}
			else {
				GPKDATA |= 0xf0;  // 熄灭所有LED
				all_led_status = 0;
				clear_blink_counter++;  // 完成一次闪烁
			}
		}
		else {
			interrupt_mode = 0;     // 闪烁完成，恢复空闲状态
			clear_blink_counter = 0;   // 重置闪烁计数器
			GPKDATA |= 0xf0;   // 确保所有LED灯熄灭
		}
	}
	// 状态2：数字显示状态
	else if (interrupt_mode == 2)
	{
		// LED1显示个位数字
		if (blink_counter[0] > 0) {
			if (led_status[0] == LED_OFF)
			{
				GPKDATA = 0xef;  // 点亮LED1
				led_status[0] = LED_ON;
			}
			else if (led_status[0] == LED_ON)
			{
				GPKDATA = 0xff;  // 熄灭LED1
				led_status[0] = LED_OFF;
				blink_counter[0]--;  // 减少剩余闪烁次数
			}
		}
		// LED2显示十位数字
		else if (blink_counter[1] > 0) {
			if (led_status[1] == LED_OFF)
			{
				GPKDATA = 0xdf;  // 点亮LED2
				led_status[1] = LED_ON;
			}
			else if (led_status[1] == LED_ON)
			{
				GPKDATA = 0xff;  // 熄灭LED2
				led_status[1] = LED_OFF;
				blink_counter[1]--;  // 减少剩余闪烁次数
			}
		}
		// LED3显示百位数字
		else if (blink_counter[2] > 0) {
			if (led_status[2] == LED_OFF)
			{
				GPKDATA = 0xbf;  // 点亮LED3
				led_status[2] = LED_ON;
			}
			else if (led_status[2] == LED_ON)
			{
				GPKDATA = 0xff;  // 熄灭LED3
				led_status[2] = LED_OFF;
				blink_counter[2]--;  // 减少剩余闪烁次数
			}
		}
		// LED4显示千位数字
		else if (blink_counter[3] > 0) {
			if (led_status[3] == LED_OFF)
			{
				GPKDATA = 0x7f;  // 点亮LED4
				led_status[3] = LED_ON;
			}
			else if (led_status[3] == LED_ON)
			{
				GPKDATA = 0xff;  // 熄灭LED4
				led_status[3] = LED_OFF;
				blink_counter[3]--;  // 减少剩余闪烁次数
			}
		}
		// 检查是否所有LED都显示完毕
		if (blink_counter[0] == 0 && blink_counter[1] == 0 && blink_counter[2] == 0 && blink_counter[3] == 0) {
			interrupt_mode = 0;  // 显示完成，进入空闲状态
		}
	}
	// 状态3：双向跑马灯显示状态
	else if (interrupt_mode == 3)
	{
		GPKDATA =0xff;  // 先熄灭所有LED

		// 点亮当前LED灯
		GPKDATA &= ~(1 << (current_led_index + 4));  // 点亮对应的LED

		// 更新LED灯索引和方向
		if (marquee_direction == FORWARD) {  // 正向移动
			current_led_index++;
			if (current_led_index >= LED_COUNT) {  // 到达最后一个LED
				current_led_index = LED_COUNT - 2;  // 回到倒数第二个LED
				marquee_direction = BACKWARD;       // 改变方向为反向
			}
		}
		else {  // 反向移动
			current_led_index--;
			if (current_led_index < 0) {  // 到达第一个LED之前
				current_led_index = 1;        // 回到第二个LED
				marquee_direction = FORWARD;  // 改变方向为正向
			}
		}
	}
	// 状态4：低位数字闪烁显示状态
	else if (interrupt_mode == 4)
	{
		if (low_digits_counter > 0) {  // 还有剩余闪烁次数
			if (low_digits_status == LED_OFF)
			{
				GPKDATA = 0x0f;  // 点亮低两位对应的LED
				low_digits_status = LED_ON;
			}
			else if (low_digits_status == LED_ON)
			{
				GPKDATA = 0xff;  // 熄灭所有LED
				low_digits_status = LED_OFF;
				low_digits_counter--;    // 减少剩余闪烁次数
			}
		}
		else {
			interrupt_mode = 0;  // 闪烁完成，进入空闲状态
		}
	}
	
	// 清除中断标志
	int timer_reg_value = TINT_CSTAT;
	TINT_CSTAT = timer_reg_value;     // 清除定时器中断标志
	VIC0ADDRESS=0x0;       // 清除VIC中断标志	
}

/*
 * 初始化PWM定时器0
 */
void timer_init(unsigned long timer_id,unsigned long prescaler_val,unsigned long divider_val,unsigned long count_buffer,unsigned long compare_buffer)
{
	unsigned long config_temp;

	// 设置预分频系数
	config_temp = TCFG0;
	config_temp = (config_temp & (~(0xff00ff))) | (prescaler_val<<0);
	TCFG0 = config_temp;

	// 设置分频
	config_temp = TCFG1;
	config_temp = (config_temp & (~(0xf<<4*timer_id))& (~(1<<20))) |(divider_val<<4*timer_id);
	TCFG1 = config_temp;

	// 设置定时器计数初值
	TCNTB0 = count_buffer;
	TCMPB0 = compare_buffer;

	// 手动更新定时器配置
	TCON |= 1<<1;

	// 清除手动更新位
	TCON &= ~(1<<1);

	// 启动定时器
	TCON |= (1<<0)|(1<<3);

	// 使能timer0中断
	config_temp = TINT_CSTAT;
	config_temp = (config_temp & (~(1<<timer_id)))|(1<<(timer_id));
	TINT_CSTAT = config_temp;
}


