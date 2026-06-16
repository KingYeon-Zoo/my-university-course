#include <stdio.h>
#include <stdlib.h>

int OutputBlockofMemory(int *BlockofMemory, int BlockCount, int ReplacePage, int PageNum);
void OutputPageNumofRef(int* PageNumofRef, int PageNumRefCount);
void ResetBlockofMemory(int *BlockofMemory, int BlockCount);
int PageInBlockofMemory(int PageNum, int *BlockofMemory, int BlockCount);
int DistanceOpt(int *BlockofMemory, int *PageNumofRef, int j, int i, int PageNumRefCount);
int DistanceLru(int *BlockofMemory, int *PageNumofRef, int j, int i);
void Opt(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount);
void Fifo(int *BlockofMemory,int *PageNumofRef,int BlockCount,int PageNumRefCount);
void Lru(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount);
void Lfu(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount);
void Pba(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount);
void Clock(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount);

int main()
{
	int *BlockofMemory;		//内存物理块
	const int BlockCount = 5;
	int PageNumofRef[] = {7,0,1,2,0,3,0,4,2,3,0,1,1,7,0,1,0,3};  //页面号引用串
	int PageNumRefCount = sizeof(PageNumofRef) / sizeof(PageNumofRef[0]);

	BlockofMemory = (int*)malloc(BlockCount * sizeof(int));
	if(BlockofMemory == (int*)NULL)
	{
		printf("内存分配出错\n");
		exit(1);
	}

	ResetBlockofMemory(BlockofMemory, BlockCount);
	Opt(BlockofMemory, PageNumofRef, BlockCount, PageNumRefCount);

	ResetBlockofMemory(BlockofMemory,BlockCount);
	Fifo(BlockofMemory, PageNumofRef, BlockCount, PageNumRefCount);
	
	ResetBlockofMemory(BlockofMemory,BlockCount);
	Lru(BlockofMemory, PageNumofRef, BlockCount, PageNumRefCount);

	ResetBlockofMemory(BlockofMemory,BlockCount);
	Lfu(BlockofMemory, PageNumofRef, BlockCount, PageNumRefCount);

	ResetBlockofMemory(BlockofMemory,BlockCount);
	Pba(BlockofMemory, PageNumofRef, BlockCount, PageNumRefCount);

	ResetBlockofMemory(BlockofMemory,BlockCount);
	Clock(BlockofMemory, PageNumofRef, BlockCount, PageNumRefCount);

	free(BlockofMemory);

	return 0;
}

//输出内存块页面序号
int OutputBlockofMemory(int *BlockofMemory, int BlockCount, int ReplacePage, int PageNum)
{
	int i;

	printf("访问页面 %d 后，", PageNum);
	printf("内存中的页面号为:\t");
	for(i = 0; i < BlockCount; i++)
	{
		if(BlockofMemory[i] < 0)
			printf("#  ");
		else
			printf("%d  ", BlockofMemory[i]);
	}

	if(ReplacePage != -1)
		printf("\t淘汰页面号为:%d", ReplacePage);

	printf("\n");

	return -1;
}

//输出页面引用串号
void OutputPageNumofRef(int* PageNumofRef, int PageNumRefCount)
{
	int i = 0;
	printf("页面引用串为:\t");
	for(i = 0; i < PageNumRefCount; i++)
		printf("%d  ", PageNumofRef[i]);
	printf("\n");
}

//内存块页面号清零
void ResetBlockofMemory(int *BlockofMemory, int BlockCount)
{
	int i;
	for(i = 0; i < BlockCount; i++)
		BlockofMemory[i] = -1;
}

//判断页是否在内存中，如果页在内存中，返回1，否则返回0；
int PageInBlockofMemory(int PageNum, int *BlockofMemory, int BlockCount)
{
	int i;
	for(i = 0; i < BlockCount; i++)
		if(PageNum == BlockofMemory[i])
			return 1;
	return 0;
}

//下次访问次序
//参数j:  页面在内存块中的位置
//参数i： 页面号在页面号引用串中的位置
int DistanceOpt(int *BlockofMemory, int *PageNumofRef, int j, int i, int PageNumRefCount)
{
	int k;
	for(k = i + 1; k < PageNumRefCount; k++)
		if(BlockofMemory[j] == PageNumofRef[k])
			return k;
	return PageNumRefCount;
}

//上次访问次序（LRU使用）
//参数j:  页面在内存块中的位置
//参数i： 页面号在页面号引用串中的位置
//返回值：返回该页面上次被访问的位置，如果之前未被访问过则返回-1
int DistanceLru(int *BlockofMemory, int *PageNumofRef, int j, int i)
{
	int k;
	for(k = i - 1; k >= 0; k--)
		if(BlockofMemory[j] == PageNumofRef[k])
			return k;
	return -1;
}

//最佳页面置换算法
void Opt(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount)
{
	int i, j, k;
	int MaxIndex1, MaxIndex2;
	int MissCount = 0;
	int ReplacePage;
	int EmptyBlockCount = BlockCount;

	printf("**********最佳页面置换算法：**********\n");

	//输出页面引用串号
	OutputPageNumofRef(PageNumofRef, PageNumRefCount);

	for(i = 0; i < PageNumRefCount; i++)
	{
		if(!PageInBlockofMemory(PageNumofRef[i], BlockofMemory, BlockCount)) //页不在内存中
		{
			MissCount++;

			if(EmptyBlockCount > 0)
			{
				BlockofMemory[BlockCount - EmptyBlockCount] = PageNumofRef[i];
				OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
				EmptyBlockCount--;
			}
			else
			{
				MaxIndex1 = MaxIndex2 = 0;
				//求出未来最长时间不被访问的页
				for(j = 0; j < BlockCount; j++)
				{
					MaxIndex2 = DistanceOpt(BlockofMemory, PageNumofRef, j, i, PageNumRefCount);
					if(MaxIndex1 < MaxIndex2)
					{
						MaxIndex1 = MaxIndex2;
						k = j;
					}
				}
				ReplacePage = BlockofMemory[k];
				BlockofMemory[k] = PageNumofRef[i];
				OutputBlockofMemory(BlockofMemory, BlockCount, ReplacePage, PageNumofRef[i]);
			}
		}
		else
		{
			OutputBlockofMemory(BlockofMemory,BlockCount, -1, PageNumofRef[i]);
		}
	}

	printf("缺页次数为: %d\n", MissCount);
	printf("OPT缺页率为: %.3f\n", (float)MissCount / PageNumRefCount);
}

//先进先出页面置换算法
void Fifo(int *BlockofMemory,int *PageNumofRef,int BlockCount,int PageNumRefCount)
{
	int i;
	int ReplacePage;
	int ReplaceIndex = 0;
	int MissCount = 0;
	int EmptyBlockCount = BlockCount;

	printf("**********先进先出页面置换算法：**********\n");
	
	//输出页面引用串号
	OutputPageNumofRef(PageNumofRef,PageNumRefCount);

	for(i = 0; i < PageNumRefCount; i++)
	{
		if(!PageInBlockofMemory(PageNumofRef[i], BlockofMemory, BlockCount)) //页不在内存中
		{
			MissCount++;

			if(EmptyBlockCount > 0)
			{
				BlockofMemory[BlockCount - EmptyBlockCount] = PageNumofRef[i];
				OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
				EmptyBlockCount--;
			}
			else
			{
				ReplacePage = BlockofMemory[ReplaceIndex];
				BlockofMemory[ReplaceIndex] = PageNumofRef[i];
				ReplaceIndex = (ReplaceIndex + 1) % BlockCount;
				OutputBlockofMemory(BlockofMemory, BlockCount, ReplacePage, PageNumofRef[i]);
			}
		}
		else
			OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
	}
	printf("缺页次数为：%d\n", MissCount);
	printf("FIFO缺页率为：%.3f\n", (float)MissCount / PageNumRefCount);
}

//最近最久未使用页面置换算法
void Lru(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount)
{
	int i, j, k;
	int MinIndex1, MinIndex2;
	int MissCount = 0;
	int ReplacePage;
	int EmptyBlockCount = BlockCount;

	printf("************最近最久未使用页面置换算法：************\n");
	
	//输出页面引用串号
	OutputPageNumofRef(PageNumofRef, PageNumRefCount);

	for(i = 0; i < PageNumRefCount; i++)
	{
		if(!PageInBlockofMemory(PageNumofRef[i], BlockofMemory, BlockCount)) //页不在内存中
		{
			MissCount++;

			if(EmptyBlockCount > 0)
			{
				// 如果内存还有空闲块，直接放入
				BlockofMemory[BlockCount - EmptyBlockCount] = PageNumofRef[i];
				OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
				EmptyBlockCount--;
			}
			else
			{
				// 内存已满，需要找到最久未使用的页面进行置换
				MinIndex1 = i;
				MinIndex2 = 0;
				k = 0;
				
				// 求出最长时间未被访问的页面
				for(j = 0; j < BlockCount; j++)
				{
					MinIndex2 = DistanceLru(BlockofMemory, PageNumofRef, j, i);
					if(MinIndex1 > MinIndex2)
					{
						MinIndex1 = MinIndex2;
						k = j;
					}
				}
				
				ReplacePage = BlockofMemory[k];
				BlockofMemory[k] = PageNumofRef[i];
				OutputBlockofMemory(BlockofMemory, BlockCount, ReplacePage, PageNumofRef[i]);
			}
		}
		else
			OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
	}

	printf("缺页次数为：%d\n", MissCount);
	printf("LRU缺页率为：%.3f\n", (float)MissCount / PageNumRefCount);
}

//最不常用页面置换算法(LFU)
void Lfu(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount)
{
	int i, j, k;
	int *Counter;  // 访问计数器数组
	int MinCount;
	int MissCount = 0;
	int ReplacePage;
	int EmptyBlockCount = BlockCount;

	printf("************最不常用页面置换算法：************\n");

	// 为计数器数组分配内存
	Counter = (int*)malloc(BlockCount * sizeof(int));
	if(Counter == NULL)
	{
		printf("内存分配出错\n");
		return;
	}

	// 初始化计数器
	for(i = 0; i < BlockCount; i++)
		Counter[i] = 0;

	//输出页面引用串号
	OutputPageNumofRef(PageNumofRef, PageNumRefCount);

	for(i = 0; i < PageNumRefCount; i++)
	{
		if(!PageInBlockofMemory(PageNumofRef[i], BlockofMemory, BlockCount)) //页不在内存中
		{
			MissCount++;

			if(EmptyBlockCount > 0)
			{
				// 如果内存还有空闲块，直接放入
				BlockofMemory[BlockCount - EmptyBlockCount] = PageNumofRef[i];
				Counter[BlockCount - EmptyBlockCount] = 1;  // 计数器初始化为1
				OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
				EmptyBlockCount--;
			}
			else
			{
				// 内存已满，找到访问计数最小的页面进行置换
				MinCount = Counter[0];
				k = 0;
				for(j = 1; j < BlockCount; j++)
				{
					if(Counter[j] < MinCount)
					{
						MinCount = Counter[j];
						k = j;
					}
				}

				ReplacePage = BlockofMemory[k];
				BlockofMemory[k] = PageNumofRef[i];
				Counter[k] = 1;  // 重置计数器
				OutputBlockofMemory(BlockofMemory, BlockCount, ReplacePage, PageNumofRef[i]);
			}
		}
		else
		{
			// 页面在内存中，增加对应的计数器
			for(j = 0; j < BlockCount; j++)
			{
				if(BlockofMemory[j] == PageNumofRef[i])
				{
					Counter[j]++;
					break;
				}
			}
			OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
		}
	}

	printf("缺页次数为：%d\n", MissCount);
	printf("LFU缺页率为：%.3f\n", (float)MissCount / PageNumRefCount);

	free(Counter);
}

//页面缓冲置换算法(PBA)
void Pba(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount)
{
	int i, j;
	int ReplacePage;
	int ReplaceIndex = 0;
	int MissCount = 0;
	int EmptyBlockCount = BlockCount;
	int *BufferList;  // 页面缓冲链表
	int BufferCount = 0;
	int MaxBufferSize = 3;  // 缓冲链表最大大小
	int InBuffer = 0;

	printf("************页面缓冲置换算法：************\n");

	// 为缓冲链表分配内存
	BufferList = (int*)malloc(MaxBufferSize * sizeof(int));
	if(BufferList == NULL)
	{
		printf("内存分配出错\n");
		return;
	}

	// 初始化缓冲链表
	for(i = 0; i < MaxBufferSize; i++)
		BufferList[i] = -1;

	//输出页面引用串号
	OutputPageNumofRef(PageNumofRef, PageNumRefCount);

	for(i = 0; i < PageNumRefCount; i++)
	{
		// 首先检查页面是否在缓冲链表中
		InBuffer = 0;
		for(j = 0; j < BufferCount; j++)
		{
			if(BufferList[j] == PageNumofRef[i])
			{
				InBuffer = 1;
				// 从缓冲链表中移除并放入内存
				BufferList[j] = -1;
				// 重新整理缓冲链表
				for(int m = j; m < BufferCount - 1; m++)
					BufferList[m] = BufferList[m + 1];
				BufferCount--;
				break;
			}
		}

		if(!PageInBlockofMemory(PageNumofRef[i], BlockofMemory, BlockCount)) //页不在内存中
		{
			if(!InBuffer)
				MissCount++;

			if(EmptyBlockCount > 0)
			{
				BlockofMemory[BlockCount - EmptyBlockCount] = PageNumofRef[i];
				OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
				EmptyBlockCount--;
			}
			else
			{
				ReplacePage = BlockofMemory[ReplaceIndex];
				
				// 将被置换的页面放入缓冲链表
				if(BufferCount < MaxBufferSize)
				{
					BufferList[BufferCount] = ReplacePage;
					BufferCount++;
				}
				else
				{
					// 缓冲链表已满，采用FIFO移除最旧的
					for(j = 0; j < MaxBufferSize - 1; j++)
						BufferList[j] = BufferList[j + 1];
					BufferList[MaxBufferSize - 1] = ReplacePage;
				}

				BlockofMemory[ReplaceIndex] = PageNumofRef[i];
				ReplaceIndex = (ReplaceIndex + 1) % BlockCount;
				OutputBlockofMemory(BlockofMemory, BlockCount, ReplacePage, PageNumofRef[i]);
			}
		}
		else
			OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
	}

	printf("缺页次数为：%d\n", MissCount);
	printf("PBA缺页率为：%.3f\n", (float)MissCount / PageNumRefCount);

	free(BufferList);
}

//CLOCK页面置换算法
void Clock(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount)
{
	int i, j;
	int *UseBit;  // 使用位(引用位)
	int ClockHand = 0;  // 时钟指针
	int MissCount = 0;
	int ReplacePage;
	int EmptyBlockCount = BlockCount;

	printf("************CLOCK页面置换算法：************\n");

	// 为使用位数组分配内存
	UseBit = (int*)malloc(BlockCount * sizeof(int));
	if(UseBit == NULL)
	{
		printf("内存分配出错\n");
		return;
	}

	// 初始化使用位
	for(i = 0; i < BlockCount; i++)
		UseBit[i] = 0;

	//输出页面引用串号
	OutputPageNumofRef(PageNumofRef, PageNumRefCount);

	for(i = 0; i < PageNumRefCount; i++)
	{
		if(!PageInBlockofMemory(PageNumofRef[i], BlockofMemory, BlockCount)) //页不在内存中
		{
			MissCount++;

			if(EmptyBlockCount > 0)
			{
				// 如果内存还有空闲块，直接放入
				BlockofMemory[BlockCount - EmptyBlockCount] = PageNumofRef[i];
				UseBit[BlockCount - EmptyBlockCount] = 1;  // 设置使用位
				OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
				EmptyBlockCount--;
			}
			else
			{
				// 内存已满，使用CLOCK算法找到要置换的页面
				while(1)
				{
					if(UseBit[ClockHand] == 0)
					{
						// 找到使用位为0的页面，进行置换
						ReplacePage = BlockofMemory[ClockHand];
						BlockofMemory[ClockHand] = PageNumofRef[i];
						UseBit[ClockHand] = 1;  // 设置新页面的使用位
						OutputBlockofMemory(BlockofMemory, BlockCount, ReplacePage, PageNumofRef[i]);
						ClockHand = (ClockHand + 1) % BlockCount;  // 移动指针
						break;
					}
					else
					{
						// 使用位为1，将其置为0，继续查找
						UseBit[ClockHand] = 0;
						ClockHand = (ClockHand + 1) % BlockCount;
					}
				}
			}
		}
		else
		{
			// 页面在内存中，设置使用位为1
			for(j = 0; j < BlockCount; j++)
			{
				if(BlockofMemory[j] == PageNumofRef[i])
				{
					UseBit[j] = 1;
					break;
				}
			}
			OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
		}
	}

	printf("缺页次数为：%d\n", MissCount);
	printf("CLOCK缺页率为：%.3f\n", (float)MissCount / PageNumRefCount);

	free(UseBit);
}


