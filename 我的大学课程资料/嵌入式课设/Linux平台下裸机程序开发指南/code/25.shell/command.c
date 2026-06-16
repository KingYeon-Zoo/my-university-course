#include "stdio.h"
#include "uart.h"
#include "string.h"

// help 命令
int help(int argc, char * argv[])
{
	printf("help usage:\r\n");
	printf("md - memory dispaly\r\n");
	printf("mw - memory write\r\n");
	printf("loadb - loadb filesize addr\r\n");
	printf("go - go addr\r\n");

	return 0;
}

// 读内存
int md(int argc, char * argv[])
{	
	int * p = (int *)0;
	int i, j;
	
	if (argc >= 2)
		p = (int *)atoi(argv[1]);
		
	for (j = 0; j < 16; j++)
	{	
		printf("%2x: ", (int)p);
		for (i = 0; i < 4; i++)
			printf("%8x ", *p++);	
		printf("\r\n");
	}
		
	return 0;
}

// 写内存
int mw(int argc, char * argv[])
{	
	int * p = (int *)0;
	int v = 0;
	
	if (argc >= 2)
		p = (int *)atoi(argv[1]);
		
	if (argc >= 3)
		v = atoi(argv[2]);
		
	*p = v;
	
	return 0;
}

// 串口下载
int loadb(int argc, char * argv[])
{
	int i = 0;
	int size = 0;
	char *p = NULL;

	// 文件大小
	if (argc >= 2)
	{
		size = atoi(argv[1]);
		
	}
	
	// 下载地址
	if(argc == 3)
	{
		p = (char *)atoi(argv[2]);
	}

	
	printf("load bin file to address 0x%x\r\n", (unsigned int)p);

	
	for (i = 0; i < size; i++)
		*p++ = getc();
	
	printf("load finished! \r\n");
	
	return 0;
}

// 执行内存中的bin文件
int go(int argc, char * argv[])
{
	int addr = 0x51000000;
	void (*fp)(void);
	
	if (argc >= 2)
		addr = atoi(argv[1]);
	
	printf("go to address 0x%x\r\n", addr);

	fp = (void (*)(void))addr;
	
	fp();
	
	return 0;
}


// 根据命令执行对应的代码
int command_do(int argc, char * argv[])
{
	if (argc == 0)
		return -1;

	if (strcmp(argv[0], "help") == 0)
		help(argc, argv);
		
	if (strcmp(argv[0], "md") == 0)
		md(argc, argv);

	if (strcmp(argv[0], "mw") == 0)
		mw(argc, argv);
	
	if (strcmp(argv[0], "loadb") == 0)
		loadb(argc, argv);

	if (strcmp(argv[0], "go") == 0)
		go(argc, argv);
		
	return 0;
}
