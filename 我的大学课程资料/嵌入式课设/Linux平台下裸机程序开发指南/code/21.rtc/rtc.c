#include "stdio.h"
#include "rtc.h"

#define 	RTC_BASE	 (0x7E005000)
#define		INTP      	 ( *((volatile unsigned long *)(RTC_BASE + 0x30)) )
#define		RTCCON    	 ( *((volatile unsigned long *)(RTC_BASE + 0x40)) )
#define		TICCNT    	 ( *((volatile unsigned long *)(RTC_BASE + 0x44)) )
#define		RTCALM    	 ( *((volatile unsigned long *)(RTC_BASE + 0x50)) )
#define		ALMSEC    	 ( *((volatile unsigned long *)(RTC_BASE + 0x54)) )
#define		ALMMIN    	 ( *((volatile unsigned long *)(RTC_BASE + 0x58)) )
#define		ALMHOUR  	 ( *((volatile unsigned long *)(RTC_BASE + 0x5c)) )
#define		ALMDATE    	 ( *((volatile unsigned long *)(RTC_BASE + 0x60)) )
#define		ALMMON    	 ( *((volatile unsigned long *)(RTC_BASE + 0x64)) )
#define		ALMYEAR  	 ( *((volatile unsigned long *)(RTC_BASE + 0x68)) )
#define		BCDSEC    	 ( *((volatile unsigned long *)(RTC_BASE + 0x70)) )
#define		BCDMIN   	 ( *((volatile unsigned long *)(RTC_BASE + 0x74)) )
#define		BCDHOUR    	 ( *((volatile unsigned long *)(RTC_BASE + 0x78)) )
#define		BCDDATE    	 ( *((volatile unsigned long *)(RTC_BASE + 0x7c)) )
#define		BCDDAY     	 ( *((volatile unsigned long *)(RTC_BASE + 0x80)) )
#define		BCDMON     	 ( *((volatile unsigned long *)(RTC_BASE + 0x84)) )
#define		BCDYEAR      ( *((volatile unsigned long *)(RTC_BASE + 0x88)) )
#define		CURTICCNT    ( *((volatile unsigned long *)(RTC_BASE + 0x90)) )


#define true  1
#define false 0

char *day[8] = {" ","Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"};

void delay(volatile int count)
{
	while (count--);
}

void rtc_realtime_display(void)
{
	int counter = 0;
	
	// 使能rtc控制器
	rtc_enable(true);
	// 使能rtc tick timer
	rtc_ticktime_enable(true);

	// 打印5次时间
	while( (counter++) < 5)
	{
		rtc_print();
		delay(0x1000000/5);
	}
	
	// 关闭rtc控制器
	rtc_ticktime_enable(false);
	// 关闭rtc tick timer
	rtc_enable(false);
	
}

// 使能/关闭rtc控制器
void rtc_enable(unsigned char bdata)
{
	unsigned long uread;

	uread = RTCCON;
	RTCCON = (uread&~(1<<0))|(bdata);
}

// 使能/关闭Tick timer
void rtc_ticktime_enable(unsigned char bdata)
{
	unsigned long uread;
	uread = RTCCON;
	RTCCON = ( uread&~(1<<8) ) | (bdata<<8);
}

// 打印时间
void rtc_print(void)
{
	unsigned long uyear,umonth,udate,uday,uhour,umin,usec;

	uyear = BCDYEAR;
	uyear = 0x2000 + uyear;
	umonth= BCDMON;
	udate = BCDDATE;
	uhour = BCDHOUR;
	umin  = BCDMIN;
	usec  = BCDSEC;
	uday  = BCDDAY;

	printf("%2x : %2x : %2x  %10s,  %2x/%2x/%4x\r\n", uhour, umin, usec, day[uday], umonth, udate, uyear);
}

void rtc_settime(void)
{
	// 重置值
	unsigned long year = 12;
	unsigned long month = 5;
	unsigned long	date = 1;
	unsigned long hour = 12;
	unsigned long min = 0;
	unsigned long sec = 0;
	unsigned long weekday= 3;

	//将时间转化为BCD码
	year = ( ((year/100)<<8) +(((year/10)%10)<<4) + (year%10)  );
	month  = ( ((month/10)<<4)+ (month%10) );
	date = ( ((date/10)<<4) + (date%10) );
	weekday = (weekday%10);							
	hour =( ((hour/10)<<4) + (hour%10) );
	min  =( ((min/10)<<4)  + (min%10) );
	sec  =( ((sec/10)<<4)  + (sec%10) );

	rtc_enable(true);
	// 保存BCD码
	BCDSEC  = sec;
	BCDMIN  = min;
	BCDHOUR = hour;
	BCDDATE = date;
	BCDDAY  = weekday;
	BCDMON  = month;
	BCDYEAR = year;
	rtc_enable(false);
	
	printf("reset success\r\n");
}
