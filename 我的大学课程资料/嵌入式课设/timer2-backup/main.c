#include "stdio.h"
#define GPNCON (*(volatile unsigned long *)0x7F008830)
#define GPNDAT (*(volatile unsigned long *)0x7F008834)
#define GPKCON0     		(*((volatile unsigned long *)0x7F008800))
#define GPKDATA     		(*((volatile unsigned long *)0x7F008808))
#define LED_OFF 0
#define LED_ON 1
typedef void (isr)(void);
extern void asm_timer_irq();
void timer_init(unsigned long utimer, unsigned long uprescaler, unsigned long udivider, unsigned long utcntb, unsigned long utcmpb);


extern int ones = 0, tens = 0, hundreds = 0, thousands = 0;
extern int irq_state=0;
extern int number = 0;
extern int led_count5;
extern int led_count[4];
extern int led_state[4];
int check_state[] = { 0,0,0,0 };
led_state[4] = { LED_OFF, LED_OFF, LED_OFF, LED_OFF }; 
void ledcount_cal()
{
	led_count[0]=ones;
	led_count[1]=tens;
	led_count[2]=hundreds;
	led_count[3]=thousands;
}
void cal_num()
{	number=1000*thousands+100*hundreds+10*tens+ones;
	led_count5=10*tens+ones;
}
void delay(volatile unsigned int n) {
	while (n--) {
		delay_ms(0x7ff);
	}
}
void delay_ms(int ms)   //延时函数  具体时间未知
{
	int x;
	for (x = 0; x < ms; x++)
	{
	}

}
void key_init(void)  //按键引脚初始化
{
	// 配置GPN为输入功能
	GPNCON = 0;
	GPKCON0 = 0x11110000;
	GPKDATA = 0xff;
}
int check(int id)
{
	delay(10000);
	if (ifpress(id)) {return 1;}
	else return 0;

}
int ifpress(int id)
{
	int dat = GPNDAT;
	return ((dat & (1 << id)) == 0);
}
int main()
{
	key_init();
	while (1) {
		
		
		if (check(0)) //按下K1
		{
			int flag = 1;
			while (check(0))
			{
				if (check(1)) // 按下K1同时按下K2
				{
					while (check(1)) {}
					flag = 0;
					thousands++;
				}
			}
			if (flag) ones++;
			cal_num();
			ledcount_cal();
		}
		if (check(1)) //按下K2
		{
			int flag = 1;
			while (check(1))
			{
				if (check(0)) // 按下K2同时按下K1
				{
					while (check(0)) {
					}
					flag = 0;
					hundreds++;
				}
			}
			if (flag) tens++;
			cal_num();
			ledcount_cal();
		}
		
		if (check(2))
		{	
			int flag=1;
			while (check(2))
			{	
				if (check(3)) 
				{
					ones=0;tens=0;hundreds=0;thousands=0;
					number=0;
					ledcount_cal();
					flag=0;
					irq_state=1;
					timer_init(0, 65, 4, 31250, 0);
				}
				
			}
			if(flag){
				irq_state=2;
				ledcount_cal();
				timer_init(0, 65, 4, 62500, 0);
			}
		

		}
		
		if (check(3)){
			while (check(3))	
				{check(3);}
                        while(number>=20)
                              {
                                number-=20;
                               }
                        
				if (number == 0)
				{
					irq_state = 3;
					timer_init(0, 65, 4, 62500, 0);
				}				

				else {
				irq_state = 4;
				timer_init(0, 65, 4,125000, 0);}

		}




	}
	return 0;
}

