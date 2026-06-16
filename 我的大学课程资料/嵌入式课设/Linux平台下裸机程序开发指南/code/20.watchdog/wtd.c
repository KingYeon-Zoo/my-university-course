#include "stdio.h"

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

#define WDT_BASE			(0x7E004000)
#define WTCON				( *((volatile unsigned long *)(WDT_BASE+0x00)) )
#define WTDAT				( *((volatile unsigned long *)(WDT_BASE+0x04)) )
#define WTCNT				( *((volatile unsigned long *)(WDT_BASE+0x08)) )
#define WTCLRINT			( *((volatile unsigned long *)(WDT_BASE+0x0C)) )




void irq_init(void)
{
	/* 在中断控制器里使能这些中断 */
	VIC0INTENABLE |= (1<<26);
}

void wtd_operate(unsigned long uenreset, unsigned long uenint, unsigned long uselectclk, unsigned long uenwtd, unsigned long uprescaler,unsigned long uwtdat, unsigned long uwtcnt)
{
	WTDAT = uwtdat;
	WTCNT = uwtcnt;
	
	/*uenreset: 是否使能reset
	  *uenint: 是否使能中断
	  *uselectclk: 分频系数
	  *uenwtd:是否启动定时器
	  *uprescaler:预分频系数
	  */
	WTCON = (uenreset<<0)|(uenint<<2)|(uselectclk<<3)|(uenwtd<<5)|((uprescaler)<<8);
}

//看门狗中断处理函数
void do_irq()
{
	static int i=1;
	printf("Watchdog interrupt  occur %d\r\n",i);

	// 看门狗相关中断清除
	WTCLRINT = 1;

	if(i++==5)
	{
		// 看门狗reset
		printf("waiting system reset\r\n");
		wtd_operate(1,1,0,1,100,100000,100000);
	}
}

