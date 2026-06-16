/*
 * ====================================================================
 * 嵌入式系统课程设计 - 主程序文件
 * ====================================================================
 * 功能：实现按键组合识别和LED显示控制
 * 
 * 按键功能：
 * - K1单击：个位数字+1
 * - K2单击：十位数字+1  
 * - K1保持按下+K2点击：千位数字+1
 * - K2保持按下+K1点击：百位数字+1
 * - K3单击：LED显示当前四位数字（每位闪烁对应次数）
 * - K4单击：判断数字是否为比较值的整数倍，控制LED显示模式
 * - K3+K4同时按下：清零所有数字，LED闪3次
 * 
 * 修改指导：
 * - 【可修改】按键处理逻辑部分可以调整
 * - 【可修改】比较值计算可以修改（当前为24）  
 * - 【不可修改】寄存器定义和基础配置不建议改动
 * ====================================================================
 */

#include "stdio.h"

/*
 * ====================================================================
 * GPIO和按键硬件寄存器定义区域
 * 【重要】此区域为硬件寄存器地址定义，不可修改！
 * ====================================================================
 */
#define GPNCON (*(volatile unsigned long *)0x7F008830)  // GPN端口配置寄存器
#define GPNDAT (*(volatile unsigned long *)0x7F008834)  // GPN端口数据寄存器
#define GPKCON0     		(*((volatile unsigned long *)0x7F008800))  // GPK端口配置寄存器  
#define GPKDATA     		(*((volatile unsigned long *)0x7F008808))  // GPK端口数据寄存器

/*
 * LED状态定义
 * 【可修改】如果需要可以扩展LED状态定义
 */
#define LED_OFF 0  // LED熄灭状态
#define LED_ON 1   // LED点亮状态

// 中断服务函数类型定义
typedef void (isr)(void);
extern void asm_timer_irq();

// 定时器初始化函数声明
void timer_init(unsigned long timer_id, unsigned long prescaler_val, unsigned long divider_val, unsigned long count_buffer, unsigned long compare_buffer);

// 延时和按键检测函数前向声明
void delay_ms(int ms);
int ifpress(int id);

/*
 * ====================================================================
 * 全局变量区域 - 存储四位数字和系统状态
 * 【可修改】数字变量可以根据需要调整
 * ====================================================================
 */
extern int digit_units, digit_tens, digit_hundreds, digit_thousands;  // 四位数字：个位、十位、百位、千位
extern int interrupt_mode;    // 中断状态控制变量
extern int combined_value;       // 组合后的完整四位数字
extern int low_digits_counter;   // LED闪烁计数（用于低两位显示）
extern int blink_counter[4]; // 每个LED的闪烁次数数组
extern int led_status[4]; // 每个LED的当前状态数组
extern int current_led_index;    // 跑马灯当前LED索引
extern int marquee_direction;    // 跑马灯方向

int key_check_state[] = { 0,0,0,0 };  // 按键状态检查数组
int led_status[4] = { LED_OFF, LED_OFF, LED_OFF, LED_OFF };  // LED初始状态

/*
 * ====================================================================
 * 数字计算相关函数
 * 【可修改】这些函数可以根据显示需求调整
 * ====================================================================
 */

/*
 * 功能：计算每个LED需要闪烁的次数
 * 将四位数字分别赋值给led_count数组
 */
void ledcount_cal()
{
	blink_counter[0]=digit_units;      // LED1闪烁个位次数
	blink_counter[1]=digit_tens;      // LED2闪烁十位次数
	blink_counter[2]=digit_hundreds;  // LED3闪烁百位次数
	blink_counter[3]=digit_thousands; // LED4闪烁千位次数
}

/*
 * 功能：计算完整的四位数字和低两位数字
 * 【题目1修改点】这里可以修改比较值的计算方法
 * 当前：使用固定值24作为比较基准
 * 需求：改为千位+百位 与 个位+十位 的比较
 */
void cal_num()
{	
	combined_value=1000*digit_thousands+100*digit_hundreds+10*digit_tens+digit_units;  // 计算完整四位数
	low_digits_counter=10*digit_tens+digit_units;  // 计算低两位数（十位和个位组合）
	
	/*
	 * 【题目1实现指导】
	 * 要实现千位+百位与个位+十位的比较，可以在这里添加：
	 * int high_two = digit_thousands + digit_hundreds;  // 千位+百位
	 * int low_two = digit_tens + digit_units;            // 十位+个位  
	 * 然后在K4按键处理中使用这两个值进行比较
	 */
}

/*
 * ====================================================================
 * 延时函数区域
 * 【可修改】延时时间可以根据需要调整
 * ====================================================================
 */

/*
 * 粗延时函数 - 用于大的延时需求
 */
void delay(volatile unsigned int delay_count) {
	while (delay_count--) {
		delay_ms(0x7ff);
	}
}

/*
 * 毫秒级延时函数 - 用于按键消抖等精确延时
 * 注意：具体延时时间与系统时钟相关，可能需要校准
 */
void delay_ms(int milliseconds)   
{
	int x;
	for (x = 0; x < milliseconds; x++)
	{
	}
}

/*
 * ====================================================================
 * 按键初始化和检测函数
 * 【不可修改】硬件初始化函数不建议修改
 * ====================================================================
 */

/*
 * 按键引脚初始化函数
 * 配置GPN为输入功能（连接按键K1-K4）
 * 配置GPK为输出功能（连接LED1-LED4）
 */
void key_init(void)  
{
	// 配置GPN为输入功能 - K1-K4按键连接
	GPNCON = 0;
	// 配置GPK4-GPK7为输出功能 - LED1-LED4连接
	GPKCON0 = 0x11110000;
	// 初始化GPK数据寄存器
	GPKDATA = 0xff;
}

/*
 * ====================================================================
 * 按键检测函数
 * 【可修改】按键检测逻辑可以根据需要调整消抖时间等
 * ====================================================================
 */

/*
 * 带消抖的按键检测函数
 * 参数：id - 按键编号（0-3对应K1-K4）
 * 返回：1-按键被按下，0-按键未按下
 */
int check(int key_id)
{
	delay(10000);  // 软件消抖延时
	if (ifpress(key_id)) {return 1;}
	else return 0;
}

/*
 * 直接按键状态检测函数  
 * 参数：id - 按键编号（0-3对应K1-K4）
 * 返回：1-按键被按下，0-按键未按下
 * 原理：按键按下时对应位为0，通过位操作检测
 */
int ifpress(int key_id)
{
	int gpio_data = GPNDAT;  // 读取GPN数据寄存器
	return ((gpio_data & (1 << key_id)) == 0);  // 检测对应位是否为0
}

/*
 * ====================================================================
 * 主函数 - 系统核心控制逻辑
 * 【部分可修改】按键处理逻辑可以调整，但基本框架不建议修改
 * ====================================================================
 */
int main()
{
	key_init();  // 初始化按键和LED引脚
	
	while (1) {  // 主循环 - 持续扫描按键状态
		
		/*
		 * ================================================================
		 * K1按键处理 - 个位数字输入和千位数字输入
		 * 【可修改】可以调整数字输入逻辑
		 * ================================================================
		 */
		if (check(0)) //按下K1
		{
			int is_single_key = 1;  // 标记是否为单独按K1
			while (check(0))  // K1持续按下期间
			{
				if (check(1)) // 检测是否同时按下K2
				{
					while (check(1)) {}  // 等待K2释放
					is_single_key = 0;  // 标记为组合按键
					digit_thousands++;  // 千位数字+1
				}
			}
			if (is_single_key) digit_units++;  // 单独按K1，个位数字+1
			cal_num();      // 重新计算数字
			ledcount_cal(); // 重新计算LED闪烁次数
		}
		
		/*
		 * ================================================================  
		 * K2按键处理 - 十位数字输入和百位数字输入
		 * 【可修改】可以调整数字输入逻辑
		 * ================================================================
		 */
		if (check(1)) //按下K2
		{
			int is_single_key = 1;  // 标记是否为单独按K2
			while (check(1))  // K2持续按下期间
			{
				if (check(0)) // 检测是否同时按下K1
				{
					while (check(0)) {
					}
					is_single_key = 0;  // 标记为组合按键
					digit_hundreds++;  // 百位数字+1
				}
			}
			if (is_single_key) digit_tens++;  // 单独按K2，十位数字+1
			cal_num();      // 重新计算数字
			ledcount_cal(); // 重新计算LED闪烁次数
		}
		
		/*
		 * ================================================================
		 * K3按键处理 - 数字显示和清零操作
		 * 【题目2修改点】需要实现精确4秒计时的K3+K4清零
		 * ================================================================
		 */
		if (check(2))
		{	
			int is_single_key=1;  // 标记是否为单独按K3
			while (check(2))  // K3持续按下期间
			{	
				if (check(3))  // 检测是否同时按下K4
				{
					// 清零所有数字
					digit_units=0;digit_tens=0;digit_hundreds=0;digit_thousands=0;
					combined_value=0;
					ledcount_cal();
					is_single_key=0;
					interrupt_mode=1;  // 设置为清零闪烁状态
					timer_init(0, 65, 4, 31250, 0);  // 0.5秒定时器
					
					/*
					 * 【题目2实现指导】
					 * 当前实现：K3+K4同时按下即清零
					 * 需求：必须精确按4秒才清零
					 * 
					 * 实现思路：
					 * 1. 检测到K3+K4同时按下时，启动4秒定时器
					 * 2. 在定时器中断中计时4秒
					 * 3. 4秒后检查K3+K4是否仍然按下
					 * 4. 如果仍按下且时间精确为4秒，则执行清零
					 * 5. 时间不足或超过4秒则不执行清零
					 * 
					 * 可能需要添加：
					 * - 4秒计时状态（如irq_state=5）
					 * - 按键持续时间计数器
					 * - 精确时间判断逻辑
					 */
				}
			}
			if(is_single_key){
				// 单独按K3：显示当前数字
				interrupt_mode=2;  // 设置为数字显示状态
				ledcount_cal();
				timer_init(0, 65, 4, 62500, 0);  // 1秒定时器
			}
		}
		
		/*
		 * ================================================================
		 * K4按键处理 - 数字比较和LED显示模式控制
		 * 【题目1修改点】需要修改比较逻辑
		 * ================================================================
		 */
		if (check(3)){
			while (check(3))	
				{check(3);}  // 等待K4释放
			
			/*
			 * 【当前实现】将数字对24取模，判断是否为24的倍数
			 * 【题目1需求】改为千位+百位与个位+十位的比较
			 */
                        while(combined_value>=24)
                              {
                                combined_value-=24;  // 对24取模运算
                               }
                        
			/*
			 * 【题目1实现指导】
			 * 当前比较逻辑：combined_value是否为24的倍数
			 * 需要改为：千位+百位 与 个位+十位 的比较
			 * 
			 * 实现思路：
			 * int high_sum = digit_thousands + digit_hundreds;  // 千位+百位
			 * int low_sum = digit_tens + digit_units;            // 十位+个位
			 * 
			 * 然后根据high_sum和low_sum的关系决定显示模式：
			 * - 相等：双向跑马灯显示
			 * - 不等：闪烁低两位数字
			 */
			
			if (combined_value == 0)  // 如果是24的倍数（余数为0）
			{
				current_led_index = 0;  // 重置跑马灯起始位置为LED1
				marquee_direction = 1;  // 重置方向为正向（FORWARD=1）
				interrupt_mode = 3;  // 双向跑马灯显示状态
				timer_init(0, 65, 4, 62500, 0);  // 1秒定时器
			}				
			else {
				interrupt_mode = 4;  // 闪烁低两位数字状态  
				timer_init(0, 65, 4,125000, 0);  // 2秒定时器
			}
		}
	}
	return 0;
}

