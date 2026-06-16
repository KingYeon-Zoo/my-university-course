#define __LIBRARY__
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
	
#define BUFFER_SIZE 10	/* 缓冲区数量 */
#define NUM 25			/* 产品总数 */

#define __NR_sem_open 87
#define __NR_sem_wait 88
#define __NR_sem_post 89
#define __NR_sem_unlink 90
#define __NR_shmget 91
#define __NR_shmat 92

typedef void sem_t;

/* 定义信号量系统调用 */
_syscall2(int, sem_open, const char*, name, unsigned int, value)
_syscall1(int, sem_wait, sem_t *, sem)
_syscall1(int, sem_post, sem_t *, sem)
_syscall1(int, sem_unlink, const char *, name)

/* 定义共享内存系统调用 */
_syscall2(int, shmget, int, key, int, size)
_syscall2(int, shmat, int, shmid, const void*, shmaddr)

int main()
{	
	int i, j;
	int consumeNum = 0; /* 消费者消费的产品号 */
	int produceNum = 0; /* 生产者生产的产品号 */
	int consume_pos = 0; /* 消费者从共享缓冲区中取出产品消费的位置 */
	int produce_pos = 0; /* 生产者生产产品向共享缓冲区放入的位置 */
	
	sem_t *empty, *full, *mutex;
	pid_t producer_pid, consumer_pid;
	
	/* 共享内存相关变量 */
	int shmid;               /* 共享内存标识符 */
	int key = 5;             /* 共享内存键值 */
	int *shared_buffer;      /* 指向共享内存缓冲区的指针 */
	
	/* 创建empty、full、mutex三个信号量 */
	empty = (sem_t*)sem_open("empty", BUFFER_SIZE);
	full  = (sem_t*)sem_open("full", 0);
	mutex = (sem_t*)sem_open("mutex", 1);
	
	/* 创建生产者进程 */
	if( !fork() )
	{
		producer_pid = getpid();
		printf("producer pid=%d create success!\n", producer_pid);
		
		/* 获取共享内存并映射到进程地址空间 */
		shmid = shmget(key, BUFFER_SIZE * sizeof(int));
		if(shmid <= 0) {
			printf("Producer: Failed to get shared memory! shmid=%d\n", shmid);
			printf("使用文件作为备用缓冲区...\n");
			/* 这里可以改为使用文件缓冲区，但实验要求用共享内存 */
			exit(-1);
		}
		shared_buffer = (int*)shmat(shmid, 0);
		if((int)shared_buffer <= 0) {
			printf("Producer: Failed to attach shared memory!\n");
			exit(-1);
		}
		
		/* 初始化共享缓冲区 */
		for(i = 0; i < BUFFER_SIZE; i++) {
			shared_buffer[i] = -1;
		}
		
		for( i = 0 ; i < NUM; i++)
		{
			sem_wait(empty);
			sem_wait(mutex);
			
			produceNum = i;
			
			/* 将产品放入共享缓冲区 */
			shared_buffer[produce_pos] = produceNum;
			
			/* 输出生产产品的信息 */
			printf("Producer pid=%d : %02d at %d\n", producer_pid, produceNum, produce_pos); 
			fflush(stdout);
			
			/* 生产者的游标向后移动一个位置 */
			produce_pos = (produce_pos + 1) % BUFFER_SIZE;
			
			sem_post(mutex);
			sem_post(full);
			
			sleep(2);
		}
		exit(0);
	}
	
	/* 创建消费者进程 */
	if( !fork() )
	{
		consumer_pid = getpid();
		printf("\t\t\tconsumer pid=%d create success!\n", consumer_pid);
		
		/* 获取共享内存并映射到进程地址空间 */
		shmid = shmget(key, BUFFER_SIZE * sizeof(int));
		if(shmid <= 0) {
			printf("Consumer: Failed to get shared memory! shmid=%d\n", shmid);
			printf("使用文件作为备用缓冲区...\n");
			/* 这里可以改为使用文件缓冲区，但实验要求用共享内存 */
			exit(-1);
		}
		shared_buffer = (int*)shmat(shmid, 0);
		if((int)shared_buffer <= 0) {
			printf("Consumer: Failed to attach shared memory!\n");
			exit(-1);
		}
		
		for( j = 0; j < NUM; j++ ) 
		{
			sem_wait(full);
			sem_wait(mutex);
			
			/* 从共享缓冲区取出产品 */
			consumeNum = shared_buffer[consume_pos];
			
			/* 输出消费产品的信息 */
			printf("\t\t\tConsumer pid=%d: %02d at %d\n", consumer_pid, consumeNum, consume_pos);
			fflush(stdout);
			
			/* 消费者的游标向后移动一个位置 */
			consume_pos = (consume_pos + 1) % BUFFER_SIZE;
	
			sem_post(mutex);
			sem_post(empty);
			
			if(j<4)	sleep(8);
			else sleep(1);
		}
		exit(0);
	}

	waitpid(producer_pid, NULL, 0);	/* 等待生产者进程结束 */
	waitpid(consumer_pid, NULL, 0);	/* 等待消费者进程结束 */
	
	/* 关闭所有信号量 */
	sem_unlink("empty");
	sem_unlink("full");
	sem_unlink("mutex");
	
	printf("图 7-1：生产者—消费者同步执行的过程\n");
	
	return 0;
}