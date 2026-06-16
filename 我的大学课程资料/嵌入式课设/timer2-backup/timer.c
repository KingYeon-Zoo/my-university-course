#include "stdio.h"
#define GPKCON0     		(*((volatile unsigned long *)0x7F008800))
#define GPKDATA     		(*((volatile unsigned long *)0x7F008808))

#define EINT0CON0  			(*((volatile unsigned long *)0x7F008900))
#define EINT0MASK  			(*((volatile unsigned long *)0x7F008920))
#define EINT0PEND  			(*((volatile unsigned long *)0x7F008924))
#define PRIORITY 	    	(*((volatile unsigned long *)0x7F008280))
#define SERVICE     		(*((volatile unsigned long *)0x7F008284))
#define SERVICEPEND 		(*((volatile unsigned long *)0x7F008288))
#define VIC0IRQSTATUS  		(*((volatile unsigned long *)0x71200000))
#define VIC0FIQSTATUS  		(*((volatile unsigned long *)0x71200004))
#define VIC0RAWINTR    		(*((volatile unsigned long *)0x71200008))
#define VIC0INTSELECT  		(*((volatile unsigned long *)0x7120000c))
#define VIC0INTENABLE  		(*((volatile unsigned long *)0x71200010))
#define VIC0INTENCLEAR 		(*((volatile unsigned long *)0x71200014))
#define VIC0PROTECTION 		(*((volatile unsigned long *)0x71200020))
#define VIC0SWPRIORITYMASK 	(*((volatile unsigned long *)0x71200024))
#define VIC0PRIORITYDAISY  	(*((volatile unsigned long *)0x71200028))
#define VIC0ADDRESS        	(*((volatile unsigned long *)0x71200f00))

#define		PWMTIMER_BASE			(0x7F006000)
#define		TCFG0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x00)) )
#define		TCFG1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x04)) )
#define		TCON      	( *((volatile unsigned long *)(PWMTIMER_BASE+0x08)) )
#define		TCNTB0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x0C)) )
#define		TCMPB0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x10)) )
#define		TCNTO0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x14)) )
#define		TCNTB1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x18)) )
#define		TCMPB1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x1C)) )
#define		TCNTO1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x20)) )
#define		TCNTB2    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x24)) )
#define		TCMPB2    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x28)) )
#define		TCNTO2    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x2C)) )
#define		TCNTB3    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x30)) )
#define		TCMPB3    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x34)) )
#define		TCNTO3    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x38)) )
#define		TCNTB4    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x3C)) )
#define		TCNTO4    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x40)) )
#define		TINT_CSTAT 	( *((volatile unsigned long *)(PWMTIMER_BASE+0x44)) )
#define LED_OFF 0
#define LED_ON 1

#define LED_COUNT 4
#define FORWARD 1
#define BACKWARD 0

typedef void (isr) (void);
extern void asm_timer_irq();
int irq_state;
int ones;
int tens;
int hundreds;
int thousands;
int number;

void irq_init(void)
{
	/* 在中断控制器里使能timer0中断 */
	VIC0INTENABLE |= (1<<23);

	VIC0INTSELECT =0;

	isr** isr_array = (isr**)(0x7120015C);

	isr_array[0] = (isr*)asm_timer_irq;

	/*将GPK4-GPK7配置为输出口*/
	GPKCON0 = 0x11110000;
	
	/*熄灭四个LED灯*/
	GPKDATA = 0xef;
}
int flash_count = 0;
int led_state1 = 0;

int led_state[4];  // 每个LED的状态
int led_count[4];  // 每个LED需要闪烁的次数

int led_index = 0;  // 当前点亮的LED灯
int direction = FORWARD;  // 跑马灯方向

int led_state5 = LED_OFF;
int led_count5;
// timer0中断的中断处理函数
void do_irq()
{
	if (irq_state == 0)
	{
		TCON &= ~(1<<0)|(1<<3);
	}
	else if (irq_state == 1)
	{
		if (flash_count < 3 ) {
			if (led_state1 == 0) {
				GPKDATA &= ~0xf0;  // 亮起所有LED灯
				led_state1 = 1;
			}
			else {
				GPKDATA |= 0xf0;  // 熄灭所有LED灯
				led_state1 = 0;
				flash_count++;
			}
		}
		else {
			irq_state = 0;// 闪烁完成，恢复初始状态
			flash_count = 0;
			GPKDATA |= 0xf0;  // 确保所有LED灯熄灭
		}
	}
	else if (irq_state == 2)
	{
		
		if (led_count[0] > 0) {
			if (led_state[0] == LED_OFF)
			{
				GPKDATA = 0xef;
				led_state[0] = LED_ON;
			}
			else if (led_state[0] == LED_ON)
			{
				GPKDATA = 0xff;
				led_state[0] = LED_OFF;
				led_count[0]--;
			}
		}
		else if (led_count[1] > 0) {
			if (led_state[1] == LED_OFF)
			{
				GPKDATA = 0xdf;
				led_state[1] = LED_ON;
			}
			else if (led_state[1] == LED_ON)
			{
				GPKDATA = 0xff;
				led_state[1] = LED_OFF;
				led_count[1]--;
			}
		}
		else if (led_count[2] > 0) {
			if (led_state[2] == LED_OFF)
			{
				GPKDATA = 0xbf;
				led_state[2] = LED_ON;
			}
			else if (led_state[2] == LED_ON)
			{
				GPKDATA = 0xff;
				led_state[2] = LED_OFF;
				led_count[2]--;
			}
		}
		else if (led_count[3] > 0) {
			if (led_state[3] == LED_OFF)
			{
				GPKDATA = 0x7f;
				led_state[3] = LED_ON;
			}
			else if (led_state[3] == LED_ON)
			{
				GPKDATA = 0xff;
				led_state[3] = LED_OFF;
				led_count[3]--;
			}
		}
		if (led_count[0] == 0 && led_count[1] == 0 && led_count[2] == 0 && led_count[3] == 0) {
			irq_state = 0;  // 进入初始状态
		}
	}
	else if (irq_state == 3)
	{
		GPKDATA =0xff;;

		// 点亮当前LED灯
		GPKDATA &= ~(1 << (led_index + 4));

		// 更新LED灯索引
		if (direction == FORWARD) {
			led_index++;
			if (led_index >= LED_COUNT) {
				led_index = LED_COUNT - 2;
				direction = BACKWARD;
			}
		}
		else {
			led_index--;
			if (led_index < 0) {
				led_index = 1;
				direction = FORWARD;
			}
		}

	}
	else if (irq_state == 4)
	{
		if (led_count5 > 0) {
			if (led_state5 == LED_OFF)
			{
				GPKDATA = 0x0f;
				led_state5 = LED_ON;
			}
			else if (led_state5 == LED_ON)
			{
				GPKDATA = 0xff;
				led_state5 = LED_OFF;
				led_count5--;
			}
		}
		else {
			irq_state = 0;
		}
	}
	//清timer0的中断状态寄存器
	int uTmp = TINT_CSTAT;
	TINT_CSTAT = uTmp;
	VIC0ADDRESS=0x0;	
}

// 初始化timer
void timer_init(unsigned long utimer,unsigned long uprescaler,unsigned long udivider,unsigned long utcntb,unsigned long utcmpb)
{
	unsigned long temp0;

	// 定时器的输入时钟 = PCLK / ( {prescaler value + 1} ) / {divider value} = PCLK/(65+1)/16=62500hz

	//设置预分频系数为66
	temp0 = TCFG0;
	temp0 = (temp0 & (~(0xff00ff))) | (uprescaler<<0);
	TCFG0 = temp0;

	// 16分频
	temp0 = TCFG1;
	temp0 = (temp0 & (~(0xf<<4*utimer))& (~(1<<20))) |(udivider<<4*utimer);
	TCFG1 = temp0;

	// 1s = 62500hz
	TCNTB0 = utcntb;
	TCMPB0 = utcmpb;

	// 手动更新
	TCON |= 1<<1;

	// 清手动更新位
	TCON &= ~(1<<1);

	// 自动加载和启动timer0
	TCON |= (1<<0)|(1<<3);

	// 使能timer0中断
	temp0 = TINT_CSTAT;
	temp0 = (temp0 & (~(1<<utimer)))|(1<<(utimer));
	TINT_CSTAT = temp0;
}


