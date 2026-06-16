#include "key_led_system.h"

/* 全局变量定义 */
system_state_t g_system;
led_display_t g_led_display;

/* 延时函数 */
void delay_ms(uint32_t ms)
{
    volatile uint32_t i, j;
    for (i = 0; i < ms; i++) {
        for (j = 0; j < 1000; j++) {
            /* 简单软件延时，实际延时取决于CPU频率 */
        }
    }
}

/* 系统初始化 */
void system_init(void)
{
    uint8_t i;
    
    /* 初始化系统状态 */
    for (i = 0; i < MAX_DIGITS; i++) {
        g_system.digits[i] = 0;
    }
    g_system.current_state = KEY_STATE_IDLE;
    
    for (i = 0; i < MAX_KEYS; i++) {
        g_system.key_pressed[i] = 0;
        g_system.key_prev[i] = 0;
        g_system.debounce_count[i] = 0;
    }
    
    /* 初始化LED显示状态 */
    g_led_display.display_active = 0;
    g_led_display.current_led = 0;
    g_led_display.flash_count = 0;
    g_led_display.target_flashes = 0;
    g_led_display.flash_state = 0;
    g_led_display.mode = LED_MODE_IDLE;
    g_led_display.timer_flag = 0;
    
    /* 初始化硬件 */
    key_init();
    led_init();
    timer_init();
}

/* 系统主处理循环 */
void system_process(void)
{
    /* 按键扫描处理 */
    key_scan();
    
    /* LED显示处理 */
    led_display_process();
    
    /* 简短延时以控制扫描频率 */
    delay_ms(1); /* 1ms延时，确保1KHz扫描频率 */
}

/* 主函数 */
int main(void)
{
    /* 系统初始化 */
    system_init();
    
    /* 主循环 */
    while (1) {
        system_process();
    }
    
    return 0;
}

/* 按键初始化 */
void key_init(void)
{
    /* 配置GPN0-3为中断功能 (参考 irq.c) */
    *(volatile uint32_t *)GPNCON &= ~(0xfff);      /* 清除低12位 */
    *(volatile uint32_t *)GPNCON |= 0xaaa;         /* 设置为中断功能 */
    
    /* 配置外部中断触发方式：双边沿触发 */
    *(volatile uint32_t *)EINT0CON0 &= ~(0xfff);   /* 清除配置 */
    *(volatile uint32_t *)EINT0CON0 |= 0x777;      /* 双边沿触发 */
    
    /* 禁止屏蔽中断 */
    *(volatile uint32_t *)EINT0MASK &= ~(0xf);     /* 使能K1-K4 */
    
    /* 在中断控制器里使能这些中断 */
    *(volatile uint32_t *)VIC0INTENABLE |= (0x3);  /* bit0: eint0~3, bit1: eint4~11 */
}

/* 按键扫描 */
void key_scan(void)
{
    uint8_t i;
    uint8_t key_data;
    
    /* 读取按键状态 (参考 irq.c) */
    key_data = *(volatile uint32_t *)GPNDAT;
    
    /* 更新按键状态 */
    for (i = 0; i < MAX_KEYS; i++) {
        g_system.key_prev[i] = g_system.key_pressed[i];
        
        /* 从key_data中提取第i位的状态，按下为低电平 */
        g_system.key_pressed[i] = (key_data & (1 << i)) ? 0 : 1;
        
        /* 进行消抖处理 */
        key_debounce(i);
        
        /* 检测到按键状态变化时，进入状态机处理 */
        if (g_system.key_pressed[i] != g_system.key_prev[i]) {
            key_state_machine(i);
        }
    }
}

/* 软件消抖 */
void key_debounce(uint8_t key_id)
{
    if (key_id >= MAX_KEYS) return;
    
    /* 如果按键状态发生变化，重置消抖计数器 */
    if (g_system.key_pressed[key_id] != g_system.key_prev[key_id]) {
        g_system.debounce_count[key_id] = 0;
    } else {
        /* 状态稳定，增加计数器 */
        if (g_system.debounce_count[key_id] < DEBOUNCE_TIME) {
            g_system.debounce_count[key_id]++;
        }
    }
}

/* 获取消抖后的按键状态 */
uint8_t get_key_state(uint8_t key_id)
{
    if (key_id >= MAX_KEYS) return 0;
    
    /* 只有消抖时间达到要求才返回稳定状态 */
    if (g_system.debounce_count[key_id] >= DEBOUNCE_TIME) {
        return g_system.key_pressed[key_id];
    }
    
    return g_system.key_prev[key_id]; /* 返回上一次的稳定状态 */
}

/* LED初始化 */
void led_init(void)
{
    /* 配置GPK4-7为输出功能 (参考 start.S) */
    *(volatile uint32_t *)GPKCON0 = 0x11110000;    /* GPK4-7设为输出 */
    
    /* 初始状态：所有LED熄灭（高电平） */
    *(volatile uint32_t *)GPKDAT |= (0xf << 4);    /* GPK4-7置高 */
}

/* 设置单个LED状态 */
void led_set(uint8_t led_id, uint8_t state)
{
    uint32_t led_reg;
    if (led_id >= MAX_LEDS) return;
    
    /* LED控制：亮=低电平，灭=高电平 (参考 start.S) */
    led_reg = *(volatile uint32_t *)GPKDAT;
    if (state) {
        led_reg &= ~(1 << (led_id + 4));  /* LED亮（低电平） */
    } else {
        led_reg |= (1 << (led_id + 4));   /* LED灭（高电平） */
    }
    *(volatile uint32_t *)GPKDAT = led_reg;
}

/* 定时器初始化 */
void timer_init(void)
{
    uint32_t temp0;
    
    /* 配置Timer0：预分频65，16分频 (参考 timer.c) */
    /* 设置预分频系数为66 (65+1) */
    temp0 = *(volatile uint32_t *)TCFG0;
    temp0 = (temp0 & (~(0xff))) | (65 << 0);
    *(volatile uint32_t *)TCFG0 = temp0;
    
    /* 16分频 */
    temp0 = *(volatile uint32_t *)TCFG1;
    temp0 = (temp0 & (~(0xf))) | (4 << 0);
    *(volatile uint32_t *)TCFG1 = temp0;
    
    /* 在中断控制器里使能timer0中断 */
    *(volatile uint32_t *)VIC0INTENABLE |= (1 << 23);
}

/* 启动定时器 */
void timer_start(uint32_t period)
{
    uint32_t temp0;
    
    /* 设置计数值并启动Timer0 (参考 timer.c) */
    *(volatile uint32_t *)TCNTB0 = period;          /* 设置计数值 */
    *(volatile uint32_t *)TCMPB0 = 0;               /* 比较值设为0 */
    
    /* 手动更新 */
    *(volatile uint32_t *)TCON |= (1 << 1);
    
    /* 清手动更新位 */
    *(volatile uint32_t *)TCON &= ~(1 << 1);
    
    /* 自动加载和启动timer0 */
    *(volatile uint32_t *)TCON |= (1 << 0) | (1 << 3);
    
    /* 使能timer0中断 */
    temp0 = *(volatile uint32_t *)TINT_CSTAT;
    temp0 = (temp0 & (~(1 << 0))) | (1 << 0);
    *(volatile uint32_t *)TINT_CSTAT = temp0;
}

/* 停止定时器 */
void timer_stop(void)
{
    /* 停止Timer0 (参考 timer.c) */
    *(volatile uint32_t *)TCON &= ~((1 << 0) | (1 << 3));  /* 停止定时器 */
    
    /* 禁用timer0中断 */
    *(volatile uint32_t *)TINT_CSTAT &= ~(1 << 0);
}

/* 定时器中断服务程序 */
void timer_isr(void)
{
    uint32_t uTmp;
    
    /* 清除Timer0中断标志 (参考 timer.c) */
    uTmp = *(volatile uint32_t *)TINT_CSTAT;
    *(volatile uint32_t *)TINT_CSTAT = uTmp;      /* 清除中断状态 */
    
    /* 清除中断控制器 */
    *(volatile uint32_t *)VIC0ADDRESS = 0;
    
    /* 设置定时器标志位，供主循环处理 */
    g_led_display.timer_flag = 1;
} 