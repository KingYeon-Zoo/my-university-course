#include "key_led_system.h"

/* LED显示处理主函数 */
void led_display_process(void)
{
    /* 检查定时器标志位 */
    if (g_led_display.timer_flag) {
        g_led_display.timer_flag = 0; /* 清除标志位 */
        
        /* 根据当前显示模式处理 */
        switch (g_led_display.mode) {
            case LED_MODE_SHOW_DIGIT:
                process_digit_display();
                break;
                
            case LED_MODE_RUNNING:
                /* 跑马灯模式，后续任务实现 */
                break;
                
            case LED_MODE_FLASH_LOW_DIGITS:
                /* 闪烁低位模式，后续任务实现 */
                break;
                
            default:
                /* 空闲模式，关闭所有LED */
                turn_off_all_leds();
                break;
        }
    }
}

/* 处理数字显示模式 */
void process_digit_display(void)
{
    if (!g_led_display.display_active) {
        return; /* 显示未激活 */
    }
    
    /* 切换LED状态 */
    if (g_led_display.flash_state == 0) {
        /* 当前是灭状态，点亮LED */
        led_set(g_led_display.current_led, 1);
        g_led_display.flash_state = 1;
    } else {
        /* 当前是亮状态，熄灭LED */
        led_set(g_led_display.current_led, 0);
        g_led_display.flash_state = 0;
        
        /* 完成了一次闪烁 */
        g_led_display.flash_count++;
        
        /* 检查是否完成了当前LED的所有闪烁 */
        if (g_led_display.flash_count >= g_led_display.target_flashes) {
            /* 切换到下一个LED */
            next_led_digit();
        }
    }
}

/* 切换到下一个LED数字显示 */
void next_led_digit(void)
{
    /* 关闭当前LED */
    led_set(g_led_display.current_led, 0);
    
    /* 切换到下一个LED */
    g_led_display.current_led++;
    
    if (g_led_display.current_led >= MAX_LEDS) {
        /* 所有LED都显示完毕，结束显示 */
        finish_digit_display();
        return;
    }
    
    /* 设置新LED的闪烁参数 */
    g_led_display.flash_count = 0;
    g_led_display.flash_state = 0;
    
    /* 获取对应位的数字 */
    g_led_display.target_flashes = g_system.digits[g_led_display.current_led];
    
    /* 如果数字为0，则闪烁10次 */
    if (g_led_display.target_flashes == 0) {
        g_led_display.target_flashes = 10;
    }
}

/* 完成数字显示 */
void finish_digit_display(void)
{
    /* 关闭所有LED */
    turn_off_all_leds();
    
    /* 重置显示状态 */
    g_led_display.display_active = 0;
    g_led_display.mode = LED_MODE_IDLE;
    g_led_display.current_led = 0;
    g_led_display.flash_count = 0;
    g_led_display.target_flashes = 0;
    g_led_display.flash_state = 0;
    
    /* 停止定时器 */
    timer_stop();
}

/* 关闭所有LED */
void turn_off_all_leds(void)
{
    uint8_t i;
    for (i = 0; i < MAX_LEDS; i++) {
        led_set(i, 0);
    }
}

/* 点亮所有LED */
void turn_on_all_leds(void)
{
    uint8_t i;
    for (i = 0; i < MAX_LEDS; i++) {
        led_set(i, 1);
    }
}

/* 显示指定位的数字 */
void led_display_digit(uint8_t digit_pos)
{
    uint8_t digit_value;
    uint8_t flash_times;
    uint8_t i;
    
    if (digit_pos >= MAX_DIGITS) return;
    
    digit_value = g_system.digits[digit_pos];
    flash_times = (digit_value == 0) ? 10 : digit_value;
    
    /* 简单的阻塞式显示，用于测试 */
    for (i = 0; i < flash_times; i++) {
        led_set(digit_pos, 1);  /* 点亮 */
        /* delay_ms(500); */    /* 0.5秒 - 注释掉避免编译错误 */
        led_set(digit_pos, 0);  /* 熄灭 */
        /* delay_ms(500); */    /* 0.5秒 - 注释掉避免编译错误 */
    }
}

/* 测试LED功能 */
void led_test_sequence(void)
{
    uint8_t i;
    
    /* 逐个点亮LED测试 */
    for (i = 0; i < MAX_LEDS; i++) {
        led_set(i, 1);
        /* delay_ms(500); */
        led_set(i, 0);
        /* delay_ms(200); */
    }
    
    /* 全部点亮测试 */
    turn_on_all_leds();
    /* delay_ms(1000); */
    turn_off_all_leds();
    /* delay_ms(500); */
}

/* LED跑马灯效果（为后续任务预留） */
void led_running_light(void)
{
    static uint8_t current_pos = 0;
    static uint8_t direction = 1; /* 1=正向, 0=反向 */
    
    /* 关闭所有LED */
    turn_off_all_leds();
    
    /* 点亮当前位置的LED */
    led_set(current_pos, 1);
    
    /* 计算下一个位置 */
    if (direction == 1) {
        current_pos++;
        if (current_pos >= MAX_LEDS) {
            current_pos = MAX_LEDS - 2;
            direction = 0; /* 改为反向 */
        }
    } else {
        if (current_pos == 0) {
            current_pos = 1;
            direction = 1; /* 改为正向 */
        } else {
            current_pos--;
        }
    }
}

/* LED闪烁低两位数字（为后续任务预留） */
void led_flash_low_digits(void)
{
    static uint8_t flash_state = 0;
    uint8_t ones_digit;
    uint8_t tens_digit;
    
    ones_digit = g_system.digits[0];  /* 个位 */
    tens_digit = g_system.digits[1];  /* 十位 */
    
    if (flash_state == 0) {
        /* 显示个位 */
        turn_off_all_leds();
        if (ones_digit > 0) {
            led_set(0, 1); /* LED1亮 */
        }
        flash_state = 1;
    } else {
        /* 显示十位 */
        turn_off_all_leds();
        if (tens_digit > 0) {
            led_set(1, 1); /* LED2亮 */
        }
        flash_state = 0;
    }
} 