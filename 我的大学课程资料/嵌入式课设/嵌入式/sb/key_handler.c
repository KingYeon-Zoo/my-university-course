#include "key_led_system.h"

/* 按键状态机处理 */
void key_state_machine(uint8_t key_id)
{
    uint8_t k1_pressed, k2_pressed, k3_pressed;
    uint8_t k1_stable, k2_stable, k3_stable;
    
    /* 获取消抖后的按键状态 */
    k1_stable = get_key_state(0); /* K1 */
    k2_stable = get_key_state(1); /* K2 */
    k3_stable = get_key_state(2); /* K3 */
    
    /* 获取当前按键状态（用于检测边沿） */
    k1_pressed = g_system.key_pressed[0];
    k2_pressed = g_system.key_pressed[1];
    k3_pressed = g_system.key_pressed[2];
    
    /* 检测K3按下事件（任务2触发条件） */
    if (key_id == 2 && k3_pressed && !g_system.key_prev[2]) {
        /* K3按下，触发数字显示 */
        trigger_digit_display();
        return;
    }
    
    /* 处理K1、K2状态机（任务1核心逻辑） */
    switch (g_system.current_state) {
        case KEY_STATE_IDLE:
            handle_idle_state(key_id, k1_stable, k2_stable);
            break;
            
        case KEY_STATE_COUNTING_ONES:
            handle_counting_ones_state(key_id, k1_stable, k2_stable);
            break;
            
        case KEY_STATE_COUNTING_TENS:
            handle_counting_tens_state(key_id, k1_stable, k2_stable);
            break;
            
        case KEY_STATE_K2_HOLD_MODE:
            handle_k2_hold_mode(key_id, k1_stable, k2_stable);
            break;
            
        case KEY_STATE_K1_HOLD_MODE:
            handle_k1_hold_mode(key_id, k1_stable, k2_stable);
            break;
            
        default:
            g_system.current_state = KEY_STATE_IDLE;
            break;
    }
}

/* 处理IDLE状态 */
void handle_idle_state(uint8_t key_id, uint8_t k1_stable, uint8_t k2_stable)
{
    if (key_id == 0 && k1_stable && !g_system.key_prev[0]) {
        /* K1按下，进入个位计数模式 */
        g_system.current_state = KEY_STATE_COUNTING_ONES;
        increment_digit(0); /* 个位+1 */
    }
    else if (key_id == 1 && k2_stable && !g_system.key_prev[1]) {
        /* K2按下，进入十位计数模式 */
        g_system.current_state = KEY_STATE_COUNTING_TENS;
        increment_digit(1); /* 十位+1 */
    }
}

/* 处理个位计数状态 */
void handle_counting_ones_state(uint8_t key_id, uint8_t k1_stable, uint8_t k2_stable)
{
    if (key_id == 0 && !k1_stable && g_system.key_prev[0]) {
        /* K1释放，返回IDLE状态 */
        g_system.current_state = KEY_STATE_IDLE;
    }
    else if (key_id == 0 && k1_stable && !g_system.key_prev[0]) {
        /* K1再次按下，个位+1 */
        increment_digit(0);
    }
    else if (key_id == 1 && k2_stable && !g_system.key_prev[1]) {
        /* K2按下，检查是否进入K2保持模式 */
        if (k1_stable) {
            /* K1仍然按着，进入K2保持模式 */
            g_system.current_state = KEY_STATE_K2_HOLD_MODE;
        }
    }
}

/* 处理十位计数状态 */
void handle_counting_tens_state(uint8_t key_id, uint8_t k1_stable, uint8_t k2_stable)
{
    if (key_id == 1 && !k2_stable && g_system.key_prev[1]) {
        /* K2释放，返回IDLE状态 */
        g_system.current_state = KEY_STATE_IDLE;
    }
    else if (key_id == 1 && k2_stable && !g_system.key_prev[1]) {
        /* K2再次按下，十位+1 */
        increment_digit(1);
    }
    else if (key_id == 0 && k1_stable && !g_system.key_prev[0]) {
        /* K1按下，检查是否进入K1保持模式 */
        if (k2_stable) {
            /* K2仍然按着，进入K1保持模式 */
            g_system.current_state = KEY_STATE_K1_HOLD_MODE;
        }
    }
}

/* 处理K2保持模式（K2保持，K1计数百位） */
void handle_k2_hold_mode(uint8_t key_id, uint8_t k1_stable, uint8_t k2_stable)
{
    if (key_id == 1 && !k2_stable && g_system.key_prev[1]) {
        /* K2释放，返回IDLE状态 */
        g_system.current_state = KEY_STATE_IDLE;
    }
    else if (key_id == 0 && k1_stable && !g_system.key_prev[0]) {
        /* K1按下，百位+1 */
        increment_digit(2);
    }
}

/* 处理K1保持模式（K1保持，K2计数千位） */
void handle_k1_hold_mode(uint8_t key_id, uint8_t k1_stable, uint8_t k2_stable)
{
    if (key_id == 0 && !k1_stable && g_system.key_prev[0]) {
        /* K1释放，返回IDLE状态 */
        g_system.current_state = KEY_STATE_IDLE;
    }
    else if (key_id == 1 && k2_stable && !g_system.key_prev[1]) {
        /* K2按下，千位+1 */
        increment_digit(3);
    }
}

/* 数字递增函数（模10循环） */
void increment_digit(uint8_t digit_pos)
{
    if (digit_pos >= MAX_DIGITS) return;
    
    g_system.digits[digit_pos]++;
    if (g_system.digits[digit_pos] >= 10) {
        g_system.digits[digit_pos] = 0;
    }
}

/* 触发数字显示（任务2：K3触发） */
void trigger_digit_display(void)
{
    /* 停止当前的LED显示 */
    g_led_display.display_active = 0;
    
    /* 设置为数字显示模式 */
    g_led_display.mode = LED_MODE_SHOW_DIGIT;
    g_led_display.current_led = 0;     /* 从LED1（个位）开始 */
    g_led_display.flash_count = 0;     /* 重置闪烁计数 */
    g_led_display.flash_state = 0;     /* 开始状态为灭 */
    
    /* 设置第一个LED的目标闪烁次数 */
    g_led_display.target_flashes = g_system.digits[0]; /* 个位数字 */
    
    /* 如果数字为0，则闪烁10次 */
    if (g_led_display.target_flashes == 0) {
        g_led_display.target_flashes = 10;
    }
    
    /* 激活显示并启动定时器 */
    g_led_display.display_active = 1;
    timer_start(TIMER_1SEC); /* 1秒间隔 */
}

/* 获取当前四位数字组成的完整数值 */
uint32_t get_current_number(void)
{
    return g_system.digits[3] * 1000 + /* 千位 */
           g_system.digits[2] * 100 +  /* 百位 */
           g_system.digits[1] * 10 +   /* 十位 */
           g_system.digits[0];         /* 个位 */
}

/* 清零所有数字 */
void clear_all_digits(void)
{
    uint8_t i;
    for (i = 0; i < MAX_DIGITS; i++) {
        g_system.digits[i] = 0;
    }
    g_system.current_state = KEY_STATE_IDLE;
} 