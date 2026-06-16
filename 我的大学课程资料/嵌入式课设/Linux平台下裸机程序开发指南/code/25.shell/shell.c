
int shell_parse(char * buf, char * argv[])
{
	int argc = 0;
	int state = 0;
	
	// 逐个读出字符
	while (*buf)
	{
		// 获得一个单词
		if (*buf != ' ' && state == 0)
		{
			argv[argc++] = buf;
			state = 1;
		}
		
		// 跳过空格
		if (*buf == ' ' && state == 1)
		{
			*buf = '\0';
			state = 0;
		}
		
		buf++;	
	}
	
	return argc;
}
