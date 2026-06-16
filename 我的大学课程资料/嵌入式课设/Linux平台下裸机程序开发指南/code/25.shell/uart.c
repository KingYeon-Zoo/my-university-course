// 功能:初始化串口
#include "uart.h"

#define ULCON0     (*((volatile unsigned long *)0x7F005000))
#define UCON0      (*((volatile unsigned long *)0x7F005004))
#define UFCON0     (*((volatile unsigned long *)0x7F005008))
#define UMCON0     (*((volatile unsigned long *)0x7F00500C))
#define UTRSTAT0   (*((volatile unsigned long *)0x7F005010))
#define UFSTAT0    (*((volatile unsigned long *)0x7F005018))
#define UTXH0      (*((volatile unsigned char *)0x7F005020))
#define URXH0      (*((volatile unsigned char *)0x7F005024))
#define UBRDIV0    (*((volatile unsigned short *)0x7F005028))
#define UDIVSLOT0  (*((volatile unsigned short *)0x7F00502C))
#define GPACON     (*((volatile unsigned long *)0x7F008000))


void init_uart(void)
{
	/* 1. 配置引脚 */
	GPACON &= ~0xff;
	GPACON |= 0x22;
	
	/* 2. 设置数据格式等 */
	ULCON0 = 0x3;  					// 数据位:8, 无校验, 停止位: 1, 8n1 
	UCON0  = 0x5;  					// 时钟：PCLK，禁止中断，使能UART发送、接收 
	UFCON0 = 0x01; 					// FIFO ENABLE
	UMCON0 = 0;						// 无流控
	
	/* 3. 设置波特率 */
	// DIV_VAL = (PCLK / (bps x 16 ) ) - 1 = (66500000/(115200x16))-1 = 35.08
	// DIV_VAL = 35.08 = UBRDIVn + (num of 1’s in UDIVSLOTn)/16 
	UBRDIV0   = 35;
	UDIVSLOT0 = 0x1;
	
}

/* 接收一个字符 */
char getc(void)
{
	while ((UFSTAT0 & 0x7f) == 0);  // 如果RX FIFO空，等待 
	return URXH0;                   // 取数据 
}

/* 发送一个字符 */
void putc(char c)
{
	while (UFSTAT0 & (1<<14)); 		// 如果TX FIFO满，等待 
	UTXH0 = c;                      // 写数据 
}

// 字符串转化为整型数
int atoi(char * buf)
{
	int value = 0;
	int base = 10;
	int i = 0;

	if (buf[0] == '0' && buf[1] == 'x')
	{
		base = 16;
		i = 2;
	}

	while (buf[i])
	{
		int tmp;

		if (buf[i] <= '9' && buf[i] >= '0')
			tmp = buf[i] - '0';
		else
			tmp = buf[i] - 'a' + 10;

		value = value * base + tmp;

		i++;
	}

	return value;
}

int putchar(int c)
{
	if (c == '\n')
		putc('\r');

	if (c == '\b')
	{
		putc('\b');
		putc(' ');
	}

	putc((char)c);

	return c;
}

int getchar(void)
{
	int c;

	c = (int)getc();

	if (c == '\r')
		return '\n';

	return c;
}

int puts(const char * s)
{
	while (*s)
		putchar(*s++);

	putchar('\n');

	return 0;
}

char * gets(char * s)
{
	char * p = s;

	while ((*p = getchar()) != '\n')
	{
		if (*p != '\b')
			putchar(*p++);
		else
			if (p > s)
				putchar(*p--);
	}

	*p = '\0';
	putchar('\n');

	return s;
}
