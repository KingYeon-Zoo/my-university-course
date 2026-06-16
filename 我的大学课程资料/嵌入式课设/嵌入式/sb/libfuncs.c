/* 简单的嵌入式系统库函数 */

/* 简单的模运算，避免使用除法库 */
int simple_mod10(int value)
{
    while (value >= 10) {
        value -= 10;
    }
    return value;
}

/* 简单的软件延时 */
void simple_delay(volatile int count)
{
    volatile int i;
    for (i = 0; i < count; i++) {
        /* 空循环延时 */
    }
} 