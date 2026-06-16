/*
 * ====================================================================
 * 嵌入式系统课程设计 - 定时器中断和LED控制文件  
 * ====================================================================
 * 功能：实现PWM定时器中断处理和LED显示控制
 * 
 * 主要功能：
 * 1. 定时器中断初始化和配置
 * 2. 中断服务程序 - 处理5种LED显示状态
 * 3. LED硬件控制 - 通过GPK寄存器控制LED1-LED4
 * 
 * 中断状态说明：
 * - irq_state=0：空闲状态，停止定时器
 * - irq_state=1：清零闪烁，所有LED闪3次后熄灭
 * - irq_state=2：数字显示，LED按位闪烁显示四位数字
 * - irq_state=3：跑马灯显示，LED双向循环点亮
 * - irq_state=4：低位闪烁，LED闪烁显示低两位数字
 * 
 * 修改指导：
 * - 【可修改】中断处理逻辑和LED显示时序
 * - 【可修改】定时器时间参数
 * - 【不可修改】寄存器地址定义和基本中断框架
 * ====================================================================
 */

#include "stdio.h"

/*
 * ====================================================================
 * GPIO寄存器定义区域 - LED控制
 * 【重要】此区域为硬件寄存器地址定义，不可修改！
 * ====================================================================
 */
#define GPKCON0     		(*((volatile unsigned long *)0x7F008800))  // GPK配置寄存器
#define GPKDATA     		(*((volatile unsigned long *)0x7F008808))  // GPK数据寄存器

/*
 * ====================================================================
 * 外部中断寄存器定义区域
 * 【重要】此区域为硬件寄存器地址定义，不可修改！
 * ====================================================================
 */
#define EINT0CON0  			(*((volatile unsigned long *)0x7F008900))  // 外部中断0配置
#define EINT0MASK  			(*((volatile unsigned long *)0x7F008920))  // 外部中断0屏蔽
#define EINT0PEND  			(*((volatile unsigned long *)0x7F008924))  // 外部中断0挂起

/*
 * ====================================================================
 * 中断控制器寄存器定义区域
 * 【重要】此区域为硬件寄存器地址定义，不可修改！
 * ====================================================================
 */
#define PRIORITY 	    	(*((volatile unsigned long *)0x7F008280))  // 中断优先级
#define SERVICE     		(*((volatile unsigned long *)0x7F008284))  // 中断服务
#define SERVICEPEND 		(*((volatile unsigned long *)0x7F008288))  // 中断服务挂起

/*
 * ====================================================================
 * VIC（向量中断控制器）寄存器定义区域
 * 【重要】此区域为硬件寄存器地址定义，不可修改！
 * ====================================================================
 */
#define VIC0IRQSTATUS  		(*((volatile unsigned long *)0x71200000))  // IRQ状态寄存器
#define VIC0FIQSTATUS  		(*((volatile unsigned long *)0x71200004))  // FIQ状态寄存器
#define VIC0RAWINTR    		(*((volatile unsigned long *)0x71200008))  // 原始中断寄存器
#define VIC0INTSELECT  		(*((volatile unsigned long *)0x7120000c))  // 中断选择寄存器
#define VIC0INTENABLE  		(*((volatile unsigned long *)0x71200010))  // 中断使能寄存器
#define VIC0INTENCLEAR 		(*((volatile unsigned long *)0x71200014))  // 中断清除寄存器
#define VIC0PROTECTION 		(*((volatile unsigned long *)0x71200020))  // 中断保护寄存器
#define VIC0SWPRIORITYMASK 	(*((volatile unsigned long *)0x71200024))  // 软件优先级屏蔽
#define VIC0PRIORITYDAISY  	(*((volatile unsigned long *)0x71200028))  // 优先级菊花链
#define VIC0ADDRESS        	(*((volatile unsigned long *)0x71200f00))  // 中断地址寄存器

/*
 * ====================================================================
 * PWM定时器寄存器定义区域
 * 【重要】此区域为硬件寄存器地址定义，不可修改！
 * ====================================================================
 */
#define		PWMTIMER_BASE			(0x7F006000)  // PWM定时器基地址
#define		TCFG0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x00)) )  // 定时器配置0
#define		TCFG1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x04)) )  // 定时器配置1
#define		TCON      	( *((volatile unsigned long *)(PWMTIMER_BASE+0x08)) )  // 定时器控制
#define		TCNTB0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x0C)) )  // 定时器0计数缓冲
#define		TCMPB0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x10)) )  // 定时器0比较缓冲
#define		TCNTO0    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x14)) )  // 定时器0计数观察
#define		TCNTB1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x18)) )  // 定时器1计数缓冲
#define		TCMPB1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x1C)) )  // 定时器1比较缓冲
#define		TCNTO1    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x20)) )  // 定时器1计数观察
#define		TCNTB2    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x24)) )  // 定时器2计数缓冲
#define		TCMPB2    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x28)) )  // 定时器2比较缓冲
#define		TCNTO2    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x2C)) )  // 定时器2计数观察
#define		TCNTB3    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x30)) )  // 定时器3计数缓冲
#define		TCMPB3    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x34)) )  // 定时器3比较缓冲
#define		TCNTO3    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x38)) )  // 定时器3计数观察
#define		TCNTB4    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x3C)) )  // 定时器4计数缓冲
#define		TCNTO4    	( *((volatile unsigned long *)(PWMTIMER_BASE+0x40)) )  // 定时器4计数观察
#define		TINT_CSTAT 	( *((volatile unsigned long *)(PWMTIMER_BASE+0x44)) )  // 定时器中断状态

/*
 * ====================================================================
 * LED和显示控制常量定义
 * 【可修改】可以根据需要扩展LED状态和方向定义
 * ====================================================================
 */
#define LED_OFF 0      // LED熄灭状态
#define LED_ON 1       // LED点亮状态
#define LED_COUNT 4    // LED总数量
#define FORWARD 1      // 跑马灯正向
#define BACKWARD 0     // 跑马灯反向

// 中断服务函数类型定义
typedef void (isr) (void);
extern void asm_timer_irq();

/*
 * ====================================================================
 * 全局变量区域 - 系统状态和LED控制
 * 【可修改】这些变量可以根据功能需求调整
 * ====================================================================
 */
int interrupt_mode;         // 中断状态控制：0-空闲,1-清零闪烁,2-数字显示,3-跑马灯,4-低位闪烁
int digit_units;              // 个位数字
int digit_tens;              // 十位数字  
int digit_hundreds;          // 百位数字
int digit_thousands;         // 千位数字
int combined_value;            // 完整四位数字

/*
 * ====================================================================
 * 中断初始化函数
 * 【不可修改】基本的中断和GPIO初始化不建议修改
 * ====================================================================
 */

/*
 * 功能：初始化中断控制器和GPIO
 * 配置定时器0中断和LED输出引脚
 */
void irq_init(void)
{
	/* 在中断控制器里使能timer0中断 */
	VIC0INTENABLE |= (1<<23);  // 使能VIC0的23号中断（定时器0）

	VIC0INTSELECT =0;  // 设置为IRQ中断（非FIQ）

	// 设置中断向量表，将定时器0中断指向asm_timer_irq
	isr** isr_array = (isr**)(0x7120015C);
	isr_array[0] = (isr*)asm_timer_irq;

	/*将GPK4-GPK7配置为输出口 - LED1-LED4连接*/
	GPKCON0 = 0x11110000;  // 配置GPK4-GPK7为输出功能
	
	/*熄灭四个LED灯 - 初始状态*/
	GPKDATA = 0xef;  // 设置GPK4-GPK7为高电平（LED熄灭）
}

/*
 * ====================================================================
 * LED显示控制变量
 * 【可修改】可以根据显示需求调整这些变量
 * ====================================================================
 */
int clear_blink_counter = 0;    // 清零时的闪烁计数器
int all_led_status = 0;     // 清零时所有LED的状态

int led_status[4];       // 每个LED的当前状态数组
int blink_counter[4];       // 每个LED需要闪烁的剩余次数数组

int current_led_index = 0;      // 跑马灯当前点亮的LED索引（0-3）
int marquee_direction = FORWARD; // 跑马灯当前方向

int low_digits_status = LED_OFF; // 低位闪烁时LED的状态
int low_digits_counter;           // 低位闪烁的剩余次数

/*
 * ====================================================================
 * 定时器0中断处理函数 - 核心LED显示逻辑
 * 【可修改】可以根据显示需求调整各种状态的处理逻辑
 * ====================================================================
 */

/*
 * 功能：定时器0中断服务程序
 * 根据irq_state的值执行不同的LED显示逻辑
 * 
 * 状态机说明：
 * irq_state=0：停止定时器，系统空闲
 * irq_state=1：清零闪烁，所有LED同时闪3次
 * irq_state=2：数字显示，LED1-LED4依次闪烁显示对应位数字
 * irq_state=3：跑马灯显示，LED双向循环点亮
 * irq_state=4：低位闪烁，显示十位和个位组合的数字
 */
void do_irq()
{
	/*
	 * ================================================================
	 * 状态0：系统空闲状态
	 * 【可修改】可以调整停止定时器的方式
	 * ================================================================
	 */
	if (interrupt_mode == 0)
	{
		TCON &= ~(1<<0)|(1<<3);  // 停止定时器0运行
	}
	/*
	 * ================================================================
	 * 状态1：清零闪烁状态 - K3+K4清零后的反馈显示
	 * 【可修改】可以调整闪烁次数和闪烁方式
	 * ================================================================
	 */
	else if (interrupt_mode == 1)
	{
		if (clear_blink_counter < 3 ) {  // 闪烁3次
			if (all_led_status == 0) {
				GPKDATA &= ~0xf0;  // 点亮所有LED（GPK4-GPK7设为低电平）
				all_led_status = 1;
			}
			else {
				GPKDATA |= 0xf0;  // 熄灭所有LED（GPK4-GPK7设为高电平）
				all_led_status = 0;
				clear_blink_counter++;  // 完成一次闪烁
			}
		}
		else {
			interrupt_mode = 0;     // 闪烁完成，恢复空闲状态
			clear_blink_counter = 0;   // 重置闪烁计数器
			GPKDATA |= 0xf0;   // 确保所有LED灯熄灭
		}
	}
	/*
	 * ================================================================
	 * 状态2：数字显示状态 - K3按下后显示四位数字
	 * 【可修改】可以调整显示顺序和闪烁方式
	 * LED控制说明：
	 * GPKDATA = 0xef -> 点亮LED1（GPK4=0）
	 * GPKDATA = 0xdf -> 点亮LED2（GPK5=0） 
	 * GPKDATA = 0xbf -> 点亮LED3（GPK6=0）
	 * GPKDATA = 0x7f -> 点亮LED4（GPK7=0）
	 * GPKDATA = 0xff -> 熄灭所有LED
	 * ================================================================
	 */
	else if (interrupt_mode == 2)
	{
		// LED1显示个位数字
		if (blink_counter[0] > 0) {
			if (led_status[0] == LED_OFF)
			{
				GPKDATA = 0xef;  // 点亮LED1
				led_status[0] = LED_ON;
			}
			else if (led_status[0] == LED_ON)
			{
				GPKDATA = 0xff;  // 熄灭LED1
				led_status[0] = LED_OFF;
				blink_counter[0]--;  // 减少剩余闪烁次数
			}
		}
		// LED2显示十位数字
		else if (blink_counter[1] > 0) {
			if (led_status[1] == LED_OFF)
			{
				GPKDATA = 0xdf;  // 点亮LED2
				led_status[1] = LED_ON;
			}
			else if (led_status[1] == LED_ON)
			{
				GPKDATA = 0xff;  // 熄灭LED2
				led_status[1] = LED_OFF;
				blink_counter[1]--;  // 减少剩余闪烁次数
			}
		}
		// LED3显示百位数字
		else if (blink_counter[2] > 0) {
			if (led_status[2] == LED_OFF)
			{
				GPKDATA = 0xbf;  // 点亮LED3
				led_status[2] = LED_ON;
			}
			else if (led_status[2] == LED_ON)
			{
				GPKDATA = 0xff;  // 熄灭LED3
				led_status[2] = LED_OFF;
				blink_counter[2]--;  // 减少剩余闪烁次数
			}
		}
		// LED4显示千位数字
		else if (blink_counter[3] > 0) {
			if (led_status[3] == LED_OFF)
			{
				GPKDATA = 0x7f;  // 点亮LED4
				led_status[3] = LED_ON;
			}
			else if (led_status[3] == LED_ON)
			{
				GPKDATA = 0xff;  // 熄灭LED4
				led_status[3] = LED_OFF;
				blink_counter[3]--;  // 减少剩余闪烁次数
			}
		}
		// 检查是否所有LED都显示完毕
		if (blink_counter[0] == 0 && blink_counter[1] == 0 && blink_counter[2] == 0 && blink_counter[3] == 0) {
			interrupt_mode = 0;  // 显示完成，进入空闲状态
		}
	}
	/*
	 * ================================================================
	 * 状态3：双向跑马灯显示状态 - K4按下且数字为比较值倍数时
	 * 【可修改】可以调整跑马灯的方向变化逻辑和速度
	 * ================================================================
	 */
	else if (interrupt_mode == 3)
	{
		GPKDATA =0xff;  // 先熄灭所有LED

		// 点亮当前LED灯
		GPKDATA &= ~(1 << (current_led_index + 4));  // 点亮对应的LED

		// 更新LED灯索引和方向
		if (marquee_direction == FORWARD) {  // 正向移动：LED1->LED2->LED3->LED4
			current_led_index++;
			if (current_led_index >= LED_COUNT) {  // 到达最后一个LED
				current_led_index = LED_COUNT - 2;  // 回到倒数第二个LED
				marquee_direction = BACKWARD;       // 改变方向为反向
			}
		}
		else {  // 反向移动：LED4->LED3->LED2->LED1
			current_led_index--;
			if (current_led_index < 0) {  // 到达第一个LED之前
				current_led_index = 1;        // 回到第二个LED
				marquee_direction = FORWARD;  // 改变方向为正向
			}
		}
	}
	/*
	 * ================================================================
	 * 状态4：低位数字闪烁显示状态 - K4按下且数字不为比较值倍数时
	 * 【可修改】可以调整闪烁的LED组合和方式
	 * ================================================================
	 */
	else if (interrupt_mode == 4)
	{
		if (low_digits_counter > 0) {  // 还有剩余闪烁次数
			if (low_digits_status == LED_OFF)
			{
				GPKDATA = 0x0f;  // 点亮低两位对应的LED（具体哪些LED取决于数字值）
				low_digits_status = LED_ON;
			}
			else if (low_digits_status == LED_ON)
			{
				GPKDATA = 0xff;  // 熄灭所有LED
				low_digits_status = LED_OFF;
				low_digits_counter--;    // 减少剩余闪烁次数
			}
		}
		else {
			interrupt_mode = 0;  // 闪烁完成，进入空闲状态
		}
	}
	
	/*
	 * ================================================================
	 * 中断处理结束 - 清除中断标志
	 * 【不可修改】中断清除操作是必需的
	 * ================================================================
	 */
	//清timer0的中断状态寄存器
	int timer_reg_value = TINT_CSTAT;
	TINT_CSTAT = timer_reg_value;     // 清除定时器中断标志
	VIC0ADDRESS=0x0;       // 清除VIC中断标志	
}

/*
 * ====================================================================
 * 定时器初始化函数
 * 【可修改】可以调整定时器参数来改变中断频率
 * ====================================================================
 */

/*
 * 功能：初始化PWM定时器0
 * 参数说明：
 * - utimer: 定时器编号（0-4）
 * - uprescaler: 预分频值（0-255）
 * - udivider: 分频值（0-15）  
 * - utcntb: 定时器计数初值
 * - utcmpb: 定时器比较值
 * 
 * 时钟计算公式：
 * 定时器频率 = PCLK / (预分频值+1) / 分频值
 * 例如：PCLK=66.5MHz, 预分频=65, 分频=16
 * 则定时器频率 = 66.5M / 66 / 16 = 62500Hz
 * 
 * 定时时间 = 计数值 / 定时器频率
 * 例如：计数值=62500, 则定时时间 = 62500/62500 = 1秒
 */
void timer_init(unsigned long timer_id,unsigned long prescaler_val,unsigned long divider_val,unsigned long count_buffer,unsigned long compare_buffer)
{
	unsigned long config_temp;

	/*
	 * 定时器时钟配置说明：
	 * 输入时钟 = PCLK / (预分频值+1) / 分频值
	 * 当前配置：PCLK/(65+1)/16 = 62500Hz
	 * 
	 * 常用定时配置：
	 * - 31250计数值 -> 0.5秒定时（用于清零闪烁）
	 * - 62500计数值 -> 1秒定时（用于数字显示和跑马灯）
	 * - 125000计数值 -> 2秒定时（用于低位闪烁）
	 */

	//设置预分频系数为65+1=66
	config_temp = TCFG0;
	config_temp = (config_temp & (~(0xff00ff))) | (prescaler_val<<0);
	TCFG0 = config_temp;

	// 设置分频为16（对应divider_val=4的配置）
	config_temp = TCFG1;
	config_temp = (config_temp & (~(0xf<<4*timer_id))& (~(1<<20))) |(divider_val<<4*timer_id);
	TCFG1 = config_temp;

	// 设置定时器计数初值（决定定时时间长度）
	TCNTB0 = count_buffer;
	TCMPB0 = compare_buffer;

	// 手动更新定时器配置
	TCON |= 1<<1;

	// 清除手动更新位
	TCON &= ~(1<<1);

	// 启动定时器：自动重载+启动timer0
	TCON |= (1<<0)|(1<<3);

	// 使能timer0中断
	config_temp = TINT_CSTAT;
	config_temp = (config_temp & (~(1<<timer_id)))|(1<<(timer_id));
	TINT_CSTAT = config_temp;
}

/*
 * ====================================================================
 * 题目扩展功能实现指导
 * ====================================================================
 * 
 * 【题目2：K3+K4精确4秒计时实现指导】
 * 
 * 当前问题：K3+K4同时按下立即清零，没有4秒计时
 * 需要实现：必须精确按4秒才执行清零
 * 
 * 实现方案：
 * 1. 添加新的中断状态 irq_state=5（4秒计时状态）
 * 2. 添加计时变量：
 *    int key_hold_counter = 0;  // 按键持续时间计数器
 *    int target_count = 8;      // 4秒对应的中断次数（0.5秒中断×8=4秒）
 * 
 * 3. 修改main.c中K3+K4检测逻辑：
 *    检测到K3+K4同时按下时：
 *    - 设置irq_state=5
 *    - 启动0.5秒定时器
 *    - 重置key_hold_counter=0
 * 
 * 4. 在do_irq()中添加状态5处理：
 *    else if (irq_state == 5) {
 *        // 检查K3+K4是否仍然按下
 *        if (检测K3和K4仍按下) {
 *            key_hold_counter++;
 *            if (key_hold_counter == target_count) {
 *                // 精确4秒，执行清零
 *                ones=0; tens=0; hundreds=0; thousands=0;
 *                irq_state = 1;  // 转到清零闪烁状态
 *            }
 *        } else {
 *            // 按键提前释放，取消清零
 *            irq_state = 0;  // 回到空闲状态
 *            key_hold_counter = 0;
 *        }
 *        
 *        // 如果超过4秒仍按着，也取消清零
 *        if (key_hold_counter > target_count) {
 *            irq_state = 0;
 *            key_hold_counter = 0;
 *        }
 *    }
 * 
 * 注意事项：
 * - 需要在中断中检测按键状态，可能需要添加按键状态检测函数
 * - 计时精度取决于定时器中断周期的选择
 * - 需要处理按键抖动和误触的情况
 * 
 * ====================================================================
 */


