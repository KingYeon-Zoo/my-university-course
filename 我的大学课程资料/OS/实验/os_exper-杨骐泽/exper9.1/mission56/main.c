#include <stdio.h>
#include <stdlib.h>

int OutputBlockofMemory(int *BlockofMemory, int BlockCount, int ReplacePage, int PageNum);
void OutputPageNumofRef(int* PageNumofRef, int PageNumRefCount);
void ResetBlockofMemory(int *BlockofMemory, int BlockCount);
int PageInBlockofMemory(int PageNum, int *BlockofMemory, int BlockCount);
int DistanceOpt(int *BlockofMemory, int *PageNumofRef, int j, int i, int PageNumRefCount);
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

    ResetBlockofMemory(BlockofMemory, BlockCount);
    Lfu(BlockofMemory, PageNumofRef, BlockCount, PageNumRefCount);
    
    ResetBlockofMemory(BlockofMemory, BlockCount);
    Pba(BlockofMemory, PageNumofRef, BlockCount, PageNumRefCount);
    
    ResetBlockofMemory(BlockofMemory, BlockCount);
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
//最近最久未使用页面置换算法
void Lru(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount)
{
	int i, j;
	int ReplacePage;
	int MissCount = 0;
	int EmptyBlockCount = BlockCount;
	int *LastUsedTime = (int*)malloc(BlockCount * sizeof(int)); // 记录每个内存块中页面的最近访问时间
	int time = 0; // 全局时间戳

	printf("************最近最久未使用页面置换算法：************\n");
	
	//输出页面引用串号
	OutputPageNumofRef(PageNumofRef, PageNumRefCount);

	// 初始化最近访问时间数组
	for(i = 0; i < BlockCount; i++)
		LastUsedTime[i] = -1;

	for(i = 0; i < PageNumRefCount; i++)
	{
		int pageInMemory = PageInBlockofMemory(PageNumofRef[i], BlockofMemory, BlockCount);
		
		if(!pageInMemory) //页不在内存中
		{
			MissCount++;

			if(EmptyBlockCount > 0)
			{
				// 找到第一个空闲块
				for(j = 0; j < BlockCount; j++)
				{
					if(BlockofMemory[j] == -1)
					{
						BlockofMemory[j] = PageNumofRef[i];
						LastUsedTime[j] = time++; // 更新访问时间
						OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
						EmptyBlockCount--;
						break;
					}
				}
			}
			else
			{
				// 找到最久未使用的页面（LastUsedTime最小的）
				int lruIndex = 0;
				int minTime = LastUsedTime[0];
				
				for(j = 1; j < BlockCount; j++)
				{
					if(LastUsedTime[j] < minTime)
					{
						minTime = LastUsedTime[j];
						lruIndex = j;
					}
				}
				
				ReplacePage = BlockofMemory[lruIndex];
				BlockofMemory[lruIndex] = PageNumofRef[i];
				LastUsedTime[lruIndex] = time++; // 更新访问时间
				OutputBlockofMemory(BlockofMemory, BlockCount, ReplacePage, PageNumofRef[i]);
			}
		}
		else
		{
			// 页面已在内存中，更新其最近访问时间
			for(j = 0; j < BlockCount; j++)
			{
				if(BlockofMemory[j] == PageNumofRef[i])
				{
					LastUsedTime[j] = time++; // 更新访问时间
					break;
				}
			}
			OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
		}
	}

	// 释放动态分配的内存
	free(LastUsedTime);
	
	printf("缺页次数为：%d\n", MissCount);
	printf("LRU缺页率为：%.3f\n", (float)MissCount / PageNumRefCount);
}

//最不常用页面置换算法
void Lfu(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount)
{
    int i, j;
    int ReplacePage;
    int MissCount = 0;
    int EmptyBlockCount = BlockCount;
    
    // 为每个内存块中的页面设置访问计数器
    int *AccessCount = (int*)malloc(BlockCount * sizeof(int));
    
    printf("************最不常用页面置换算法：************\n");
    
    //输出页面引用串号
    OutputPageNumofRef(PageNumofRef, PageNumRefCount);
    
    // 初始化访问计数器
    for(i = 0; i < BlockCount; i++) {
        BlockofMemory[i] = -1;
        AccessCount[i] = 0;
    }
    
    for(i = 0; i < PageNumRefCount; i++) {
        int pageFound = 0;
        int foundIndex = -1;
        
        // 检查页面是否在内存中
        for(j = 0; j < BlockCount; j++) {
            if(BlockofMemory[j] == PageNumofRef[i]) {
                pageFound = 1;
                foundIndex = j;
                break;
            }
        }
        
        if(pageFound) {
            // 页面在内存中，增加访问计数
            AccessCount[foundIndex]++;
            OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
        } else {
            // 页面不在内存中，发生缺页
            MissCount++;
            
            if(EmptyBlockCount > 0) {
                // 有空闲块，直接放入
                for(j = 0; j < BlockCount; j++) {
                    if(BlockofMemory[j] == -1) {
                        BlockofMemory[j] = PageNumofRef[i];
                        AccessCount[j] = 1; // 初始访问计数为1
                        EmptyBlockCount--;
                        break;
                    }
                }
                OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
            } else {
                // 没有空闲块，需要置换
                int lfuIndex = 0;
                int minCount = AccessCount[0];
                
                // 找到访问次数最少的页面
                for(j = 1; j < BlockCount; j++) {
                    if(AccessCount[j] < minCount) {
                        minCount = AccessCount[j];
                        lfuIndex = j;
                    } else if(AccessCount[j] == minCount) {
                        // 如果访问次数相同，使用FIFO策略（选择先进入的）
                        // 这里我们假设内存块索引小的先进入
                    }
                }
                
                ReplacePage = BlockofMemory[lfuIndex];
                BlockofMemory[lfuIndex] = PageNumofRef[i];
                AccessCount[lfuIndex] = 1; // 新页面访问计数设为1
                
                OutputBlockofMemory(BlockofMemory, BlockCount, ReplacePage, PageNumofRef[i]);
            }
        }
    }
    
    free(AccessCount);
    
    printf("缺页次数为：%d\n", MissCount);
    printf("LFU缺页率为：%.3f\n", (float)MissCount / PageNumRefCount);
}

// 链表节点结构
typedef struct PageNode {
    int pageNum;
    int modified;  // 0:未修改，1:已修改
    struct PageNode* next;
} PageNode;

//页面缓冲置换算法
//页面缓冲置换算法
void Pba(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount)
{
    int i, j;
    int ReplacePage;
    int MissCount = 0;
    int EmptyBlockCount = BlockCount;
    int fifoIndex = 0; // FIFO替换指针
    
    // 创建两个链表：空闲链表和已修改链表
    PageNode* freeList = NULL;
    PageNode* modifiedList = NULL;
    
    printf("************页面缓冲置换算法：************\n");
    
    //输出页面引用串号
    OutputPageNumofRef(PageNumofRef, PageNumRefCount);
    
    // 初始化内存块
    for(i = 0; i < BlockCount; i++) {
        BlockofMemory[i] = -1;
    }
    
    for(i = 0; i < PageNumRefCount; i++) {
        int pageFound = 0;
        
        // 首先检查页面是否在内存中
        for(j = 0; j < BlockCount; j++) {
            if(BlockofMemory[j] == PageNumofRef[i]) {
                pageFound = 1;
                break;
            }
        }
        
        if(!pageFound) {
            // 不在内存中，检查空闲链表
            PageNode* prev = NULL;
            PageNode* curr = freeList;
            int foundInFreeList = 0;
            
            while(curr != NULL) {
                if(curr->pageNum == PageNumofRef[i]) {
                    foundInFreeList = 1;
                    // 从链表中移除
                    if(prev == NULL) {
                        freeList = curr->next;
                    } else {
                        prev->next = curr->next;
                    }
                    break;
                }
                prev = curr;
                curr = curr->next;
            }
            
            // 如果不在空闲链表中，检查已修改链表
            int foundInModifiedList = 0;  // 在这里声明
            if(!foundInFreeList) {
                prev = NULL;
                curr = modifiedList;
                
                while(curr != NULL) {
                    if(curr->pageNum == PageNumofRef[i]) {
                        foundInModifiedList = 1;
                        // 从链表中移除
                        if(prev == NULL) {
                            modifiedList = curr->next;
                        } else {
                            prev->next = curr->next;
                        }
                        break;
                    }
                    prev = curr;
                    curr = curr->next;
                }
            }
            
            if(!foundInFreeList && !foundInModifiedList) {
                // 都不在链表中，发生缺页
                MissCount++;
                
                if(EmptyBlockCount > 0) {
                    // 有空闲块
                    for(j = 0; j < BlockCount; j++) {
                        if(BlockofMemory[j] == -1) {
                            BlockofMemory[j] = PageNumofRef[i];
                            EmptyBlockCount--;
                            break;
                        }
                    }
                    OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
                } else {
                    // 需要置换页面
                    ReplacePage = BlockofMemory[fifoIndex];
                    
                    // 随机决定页面是否被修改（实际应用中根据页表项判断）
                    int isModified = (rand() % 2);
                    
                    // 将被置换的页面放入相应的链表
                    PageNode* newNode = (PageNode*)malloc(sizeof(PageNode));
                    newNode->pageNum = ReplacePage;
                    newNode->modified = isModified;
                    newNode->next = NULL;
                    
                    if(isModified) {
                        newNode->next = modifiedList;
                        modifiedList = newNode;
                    } else {
                        newNode->next = freeList;
                        freeList = newNode;
                    }
                    
                    // 替换页面
                    BlockofMemory[fifoIndex] = PageNumofRef[i];
                    fifoIndex = (fifoIndex + 1) % BlockCount;
                    
                    OutputBlockofMemory(BlockofMemory, BlockCount, ReplacePage, PageNumofRef[i]);
                }
            } else {
                // 在链表中找到，直接调入内存
                // 这里简化处理，直接放入第一个空闲位置
                for(j = 0; j < BlockCount; j++) {
                    if(BlockofMemory[j] == -1) {
                        BlockofMemory[j] = PageNumofRef[i];
                        break;
                    }
                }
                
                // 释放链表节点
                if(curr != NULL) {
                    free(curr);
                }
                
                OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
            }
        } else {
            // 页面在内存中
            OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
        }
    }
    
    // 清理链表
    PageNode* temp;
    while(freeList != NULL) {
        temp = freeList;
        freeList = freeList->next;
        free(temp);
    }
    
    while(modifiedList != NULL) {
        temp = modifiedList;
        modifiedList = modifiedList->next;
        free(temp);
    }
    
    printf("缺页次数为：%d\n", MissCount);
    printf("PBA缺页率为：%.3f\n", (float)MissCount / PageNumRefCount);
}

//CLOCK 页面置换算法
void Clock(int *BlockofMemory, int *PageNumofRef, int BlockCount, int PageNumRefCount)
{
    int i, j;
    int ReplacePage;
    int MissCount = 0;
    int EmptyBlockCount = BlockCount;
    
    // 为每个内存块中的页面设置引用位
    int *ReferenceBit = (int*)malloc(BlockCount * sizeof(int));
    int clockHand = 0; // 时钟指针
    
    printf("************CLOCK页面置换算法：************\n");
    
    //输出页面引用串号
    OutputPageNumofRef(PageNumofRef, PageNumRefCount);
    
    // 初始化内存块和引用位
    for(i = 0; i < BlockCount; i++) {
        BlockofMemory[i] = -1;
        ReferenceBit[i] = 0;
    }
    
    for(i = 0; i < PageNumRefCount; i++) {
        int pageFound = 0;
        int foundIndex = -1;
        
        // 检查页面是否在内存中
        for(j = 0; j < BlockCount; j++) {
            if(BlockofMemory[j] == PageNumofRef[i]) {
                pageFound = 1;
                foundIndex = j;
                break;
            }
        }
        
        if(pageFound) {
            // 页面在内存中，设置引用位为1
            ReferenceBit[foundIndex] = 1;
            OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
        } else {
            // 页面不在内存中，发生缺页
            MissCount++;
            
            if(EmptyBlockCount > 0) {
                // 有空闲块，直接放入
                for(j = 0; j < BlockCount; j++) {
                    if(BlockofMemory[j] == -1) {
                        BlockofMemory[j] = PageNumofRef[i];
                        ReferenceBit[j] = 1; // 新页面引用位置为1
                        EmptyBlockCount--;
                        break;
                    }
                }
                OutputBlockofMemory(BlockofMemory, BlockCount, -1, PageNumofRef[i]);
            } else {
                // 没有空闲块，使用CLOCK算法进行置换
                int foundVictim = 0;
                
                while(!foundVictim) {
                    if(ReferenceBit[clockHand] == 0) {
                        // 找到引用位为0的页面，进行置换
                        foundVictim = 1;
                        ReplacePage = BlockofMemory[clockHand];
                        BlockofMemory[clockHand] = PageNumofRef[i];
                        ReferenceBit[clockHand] = 1; // 新页面引用位置为1
                        
                        OutputBlockofMemory(BlockofMemory, BlockCount, ReplacePage, PageNumofRef[i]);
                    } else {
                        // 引用位为1，将其置为0，给第二次机会
                        ReferenceBit[clockHand] = 0;
                    }
                    
                    // 移动时钟指针
                    clockHand = (clockHand + 1) % BlockCount;
                }
            }
        }
    }
    
    free(ReferenceBit);
    
    printf("缺页次数为：%d\n", MissCount);
    printf("CLOCK缺页率为：%.3f\n", (float)MissCount / PageNumRefCount);
}