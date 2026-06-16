#define __LIBRARY__
#include <unistd.h>
#include <linux/sched.h>
#include <linux/kernel.h>
#include <linux/mm.h>
#include <asm/system.h>
#include <asm/segment.h>
#include <signal.h>
#include <string.h>

#define ENOMEM 12
#define EINVAL 22
int vector[20]={0};

#define SEM_MAX 		20	// 最大信号量个数
#define NAME_MAX		16	// 信号量名称的最大长度

// 定义任务队列链表
typedef struct _item
{
	struct task_struct* task;	// 当前任务指针
	struct _item* next;			// 下一个链表项的指针
}item;

// 定义信号量结构体
typedef struct _sem_t
{
	char sem_name[NAME_MAX];	// 信号量的名称

	int value;  // 可用资源的数量
	int used;	// 信号量的引用计数，为0表示未使用，大于0表示已使用
	item* wait;  // 阻塞在信号量下的等待的任务
}sem_t;

sem_t sem_array[SEM_MAX];  // 系统中存放信号量的结构体数组


// 将任务插入任务等待队列的队尾
void wait_task(struct task_struct* task, sem_t* sem)
{
	item** end;
	item* new_item;
	
	// 查找任务队列尾部的最后一个任务
	for(end = &sem->wait; *end != NULL; end = &(*end)->next)
		;
	
	// 新建item节点，将新建节点插入到任务链表item的尾部	
	new_item = (item*)malloc(sizeof(item));
	new_item->task = task;
	new_item->next = NULL;
	*end = new_item;

	return;
}

// 在已有信号量中查找信号量
int find_sem(const char* name)
{
	int i;
	for(i = 0; i < SEM_MAX; i++)
	{
		// 如果在已有信号量中存在当前信号量，则返回当前信号量在信号量数组中的偏移量
		if(sem_array[i].used > 0 && 0 == strcmp(sem_array[i].sem_name, name))
		{
			return i;
		}
	}
	// 已有信号量中没有当前信号，返回-1
	return -1;
}

// 将用户输入的user_name传递到内核，再返回内核中kernel_name的地址
char* get_name(const char* user_name)
{
	static char kernel_name[NAME_MAX]={};
	char temp;
	int i = 0;
	
	while((temp = get_fs_byte(user_name + i)) != '\0') 
	{	// get_fs_byte()函数的作用是在内核空间取得用户空间的数据
		kernel_name[i] = temp;
		i++;
	}
	kernel_name[i] = '\0';
	
	return kernel_name;
}

// 创建信号量
sem_t* sys_sem_open(const char* name, unsigned int value)
{
	int i = 0;
	char* kernel_name;
	
	cli();		// 关中断
	kernel_name = get_name(name);  /* kernel_name指向了get_name()函数内定义的static变量kernel_name指向的内存 */
	
	// 如果在已有信号量中找到当前信号量，则返回信号量数组中的当前信号量
	if (-1 != (i = find_sem(kernel_name)))
	{
		sem_array[i].used++;
		
		sti();		// 开中断
		return &sem_array[i];
	}
	
	// 在已有信号中未找到当前信号量，则创建新的信号量
	for (i = 0; i < SEM_MAX; i++)
	{
		if(0 == sem_array[i].used)
		{
			strcpy(sem_array[i].sem_name, kernel_name);
			sem_array[i].value = value;
			sem_array[i].used++;
			sem_array[i].wait->next = NULL;		// 初始化信号量任务队列
			sti();		// 开中断
			return &sem_array[i];
		}
	}
	sti();		// 开中断
	return &sem_array[SEM_MAX];
}


// 等待信号量
int sys_sem_wait(sem_t* sem)
{
	cli();		// 关中断
 	sem->value--;
 	if(sem->value < 0)
 	{
 		wait_task(current, sem);
		current->state = TASK_UNINTERRUPTIBLE;
		RECORD_TASK_STATE(current->pid, TS_WAIT, jiffies);
		schedule();
	}
	sti();		// 开中断
	return 0;
}

// 释放信号量
 int sys_sem_post(sem_t* sem)
 {
 	struct task_struct* p;
 	item* first;
 	
	cli();		// 关中断
 	sem->value++;
	if(sem->value <= 0 && sem->wait != NULL)
	{
		first = sem->wait;
		
		p = first->task;
		p->state = TASK_RUNNING;
		RECORD_TASK_STATE(p->pid, TS_READY, jiffies);
		
		sem->wait = first->next;
		free(first);		
	}
	sti();		//开中断
	return 0;
}

// 关闭信号量
int sys_sem_unlink(const char *name)
{
	int locate = 0;
	char* kernel_name;
	
	cli(); 		// 关中断
	kernel_name = get_name(name); /* Tempname指向了get_name()函数内定义的static变量tempname指向的内存 */
	
	if (-1 != (locate = find_sem(kernel_name)))  //已有信号量中存在当前信号量
	{
		// 多个进程使用当前信号量，则信号量计数值减一
		sem_array[locate].used--;
		sti();		// 开中断
 		return 0;
 	}
 	sti();  // 开中断
	return -1;
}

/* 新建/打开一页共享内存，并返回该页共享内存的shmid（该块共享内存在操作系统内部的id）。*/
int sys_shmget(int key, int size)
{
	int free = 0;
	
	if(vector[key] != 0)
	{
		return vector[key];
	}

	if(size > 4096) 
		return -EINVAL;
		
	free = get_free_page();		// get_free_page()返回的是申请的空闲页面的地址
	if(!free)
	{
		return -ENOMEM;
	}
	
	vector[key] = free;		
	return vector[key];
}

/* 将shmid指定的共享页面映射到当前进程的虚拟地址空间中，并将其首地址返回。 */
void* sys_shmat(int shmid, const void *shmaddr)
{
	if(!shmid) 
		return NULL;
	put_page(shmid, current->start_code + current->brk);
	return (void*)current->brk;
}
