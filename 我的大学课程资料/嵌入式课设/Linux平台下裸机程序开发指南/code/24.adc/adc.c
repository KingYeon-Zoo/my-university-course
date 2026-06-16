#define	 	ADCCON 			(*((volatile unsigned long *)0x7E00B000))
#define		ADCTSC 			(*((volatile unsigned long *)0x7E00B004))
#define		ADCDLY 			(*((volatile unsigned long *)0x7E00B008))
#define		ADCDAT0 		(*((volatile unsigned long *)0x7E00B00C))
#define		ADCDAT1 		(*((volatile unsigned long *)0x7E00B010))
#define		ADCUPDN 		(*((volatile unsigned long *)0x7E00B014))
#define		ADCCLRINT 		(*((volatile unsigned long *)0x7E00B018))
#define		ADCCLRINTPNDNUP (*((volatile unsigned long *)0x7E00B020))


// 使用查询方式读取A/D转换值
int read_adc(int ch)
{
    // 使能预分频功能，设置A/D转换器的时钟 = PCLK/(65+1)
	ADCCON = (1<<16)|(1 << 14) | (65 << 6) | (ch << 3);

    // 清除位[2]，设为普通转换模式,禁止read start
	ADCCON &= ~((1<<2)|(1<<1));

    // 设置位[0]为1，启动A/D转换
	ADCCON |= (1 << 0);

    // 当A/D转换真正开始时，位[0]会自动清0
    while (ADCCON & (1 << 0));

    // 检测位[15]，当它为1时表示转换结束
    while (!(ADCCON &  (1 << 15)) );

    // 读取数据
    return (ADCDAT0 & 0xfff);
}
