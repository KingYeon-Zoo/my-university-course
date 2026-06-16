#include "buzzer.h"

#define GPFCON (*(volatile unsigned int *)0x7F0080A0)
#define GPFDAT (*(volatile unsigned int *)0x7F0080A4)
void buzzer_on()
{	
	GPFDAT |= 1<<14;
}

void buzzer_off()
{
	GPFDAT &= ~(1<<14);
}

void buzzer_init(void)
{
	// set GPF14 as output
	GPFCON |= 1<<28;
	GPFCON &= ~(1<<29);
}
