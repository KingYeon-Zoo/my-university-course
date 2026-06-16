#ifndef __KEY_LED_SYSTEM_H
#define __KEY_LED_SYSTEM_H

/* 基本类型定义 */
typedef unsigned char uint8_t;
typedef unsigned int uint32_t;

/* 端口配置预留区域 - 等待用户填写具体地址 */
#define GPNCON           0x7F008830  /* 按键端口配置寄存器 (GPN0-5) */
#define GPNDAT           0x7F008834  /* 按键数据读取寄存器 */
#define EINT0CON0        0x7F008900  /* 外部中断配置寄存器 */
#define EINT0MASK        0x7F008920  /* 外部中断屏蔽寄存器 */
#define EINT0PEND        0x7F008924  /* 外部中断标志寄存器 */

#define GPKCON0          0x7F008800  /* LED端口配置寄存器 (GPK4-7) */
#define GPKDAT           0x7F008808  /* LED数据控制寄存器 */

#define PWMTIMER_BASE    0x7F006000  /* 定时器基地址 */
#define TCFG0            0x7F006000  /* 定时器配置寄存器0 */
#define TCFG1            0x7F006004  /* 定时器配置寄存器1 */
#define TCON             0x7F006008  /* 定时器控制寄存器 */
#define TCNTB0           0x7F00600C  /* Timer0计数寄存器 */
#define TCMPB0           0x7F006010  /* Timer0比较寄存器 */
#define TINT_CSTAT       0x7F006044  /* 定时器中断状态寄存器 */

#define VIC0INTENABLE    0x71200010  /* 中断控制器使能寄存器 */
#define VIC0ADDRESS      0x71200F00  /* 中断控制器地址寄存器 */

/* 系统常量定义 */
#define MAX_DIGITS      4      /* 四位数字 */
#define MAX_KEYS        4      /* 四个按键 K1-K4 */
#define MAX_LEDS        4      /* 四个LED */
#define DEBOUNCE_TIME   50     /* 消抖时间 50ms */
#define TIMER_1SEC      62500  /* 1秒定时器计数值 */
#define TIMER_2SEC      125000 /* 2秒定时器计数值 */
#define TIMER_05SEC     31250  /* 0.5秒定时器计数值 */
#define FIXED_DATE_SUM  24     /* 固定日期2025-6-27各位数字和 */

/* 按键状态枚举 */
typedef enum {
    KEY_STATE_IDLE = 0,
    KEY_STATE_COUNTING_ONES,     /* K1计数个位 */
    KEY_STATE_COUNTING_TENS,     /* K2计数十位 */
    KEY_STATE_K2_HOLD_MODE,      /* K2保持，K1计数百位 */
    KEY_STATE_K1_HOLD_MODE       /* K1保持，K2计数千位 */
} key_state_t;

/* LED显示模式枚举 */
typedef enum {
    LED_MODE_IDLE = 0,
    LED_MODE_SHOW_DIGIT,         /* 显示数字模式 */
    LED_MODE_RUNNING,            /* 跑马灯模式 */
    LED_MODE_FLASH_LOW_DIGITS,   /* 闪烁低位模式 */
    LED_MODE_CLEAR_SEQUENCE      /* 清除序列模式 */
} led_mode_t;

/* 系统状态结构 */
typedef struct {
    uint8_t digits[MAX_DIGITS];        /* 四位数字：[0]个位 [1]十位 [2]百位 [3]千位 */
    key_state_t current_state;         /* 当前按键状态 */
    uint8_t key_pressed[MAX_KEYS];     /* K1-K4按键当前状态 */
    uint8_t key_prev[MAX_KEYS];        /* K1-K4按键上次状态 */
    uint32_t debounce_count[MAX_KEYS]; /* 消抖计数器 */
} system_state_t;

/* LED显示状态结构 */
typedef struct {
    uint8_t display_active;      /* 显示激活标志 */
    uint8_t current_led;         /* 当前显示的LED(0-3) */
    uint8_t flash_count;         /* 当前闪烁次数 */
    uint8_t target_flashes;      /* 目标闪烁次数 */
    uint8_t flash_state;         /* 闪烁状态(0=灭, 1=亮) */
    led_mode_t mode;             /* LED显示模式 */
    uint8_t timer_flag;          /* 定时器标志位 */
    uint8_t running_direction;   /* 跑马灯方向：1=正向，0=反向 */
    uint8_t clear_flash_count;   /* 清除序列闪烁计数 */
    uint8_t k3_hold_detected;    /* K3保持状态检测标志 */
    uint32_t hold_start_time;    /* 按键保持开始时间 */
} led_display_t;

/* 按键处理函数声明 */
void key_init(void);
void key_scan(void);
void key_debounce(uint8_t key_id);
void key_state_machine(uint8_t key_id);
uint8_t get_key_state(uint8_t key_id);
void handle_idle_state(uint8_t key_id, uint8_t k1_stable, uint8_t k2_stable);
void handle_counting_ones_state(uint8_t key_id, uint8_t k1_stable, uint8_t k2_stable);
void handle_counting_tens_state(uint8_t key_id, uint8_t k1_stable, uint8_t k2_stable);
void handle_k2_hold_mode(uint8_t key_id, uint8_t k1_stable, uint8_t k2_stable);
void handle_k1_hold_mode(uint8_t key_id, uint8_t k1_stable, uint8_t k2_stable);
void increment_digit(uint8_t digit_pos);
void trigger_digit_display(void);
uint32_t get_current_number(void);
void clear_all_digits(void);
void handle_k4_press(void);
uint32_t calculate_date_sum(void);
uint8_t is_multiple(uint32_t number, uint32_t base);
void detect_k3_k4_combination(void);

/* LED控制函数声明 */
void led_init(void);
void led_set(uint8_t led_id, uint8_t state);
void led_display_digit(uint8_t digit_pos);
void led_display_process(void);
void process_digit_display(void);
void next_led_digit(void);
void finish_digit_display(void);
void turn_off_all_leds(void);
void turn_on_all_leds(void);
void led_test_sequence(void);
void led_running_light(void);
void led_flash_low_digits(void);
void start_running_light(void);
void start_flash_low_digits(void);
void start_clear_sequence(void);
void process_running_light(void);
void process_flash_low_digits(void);
void process_clear_sequence(void);

/* 定时器管理函数声明 */
void timer_init(void);
void timer_start(uint32_t period);
void timer_stop(void);
void timer_isr(void);

/* 系统主函数声明 */
void system_init(void);
void system_process(void);

/* 辅助函数声明 */
void delay_ms(uint32_t ms);
void simple_delay(volatile int count);
int simple_mod10(int value);

/* 全局变量声明 */
extern system_state_t g_system;
extern led_display_t g_led_display;

#endif /* __KEY_LED_SYSTEM_H */ 