#include "vsprintf.h"
#include "string.h"
#include "printf.h"

extern void putc(unsigned char c);
extern unsigned char getc(void);

#define	OUTBUFSIZE	1024
#define	INBUFSIZE	1024


static char output_buffer[OUTBUFSIZE];
static char input_buffer[INBUFSIZE];


int printf(const char *fmt, ...)
{
	int i;
	int len;
	va_list args;

	va_start(args, fmt);
	len = vsprintf(output_buffer,fmt,args);
	va_end(args);
	for (i = 0; i < strlen(output_buffer); i++)
	{
		putc(output_buffer[i]);
	}
	return len;
}



int scanf(const char * fmt, ...)
{
	int i = 0;
	unsigned char c;
	va_list args;
	
	while(1)
	{
		c = getc();
		putc(c);
		if((c == 0x0d) || (c == 0x0a))
		{
			input_buffer[i] = '\0';
			break;
		}
		else
		{
			input_buffer[i++] = c;
		}
	}
	
	va_start(args,fmt);
	i = vsscanf(input_buffer,fmt,args);
	va_end(args);

	return i;
}

