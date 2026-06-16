#include <stdio.h>
#include <windows.h>
#include <locale.h>

#define MAX_SIZE 1000
#define ALLOC_MIN_SIZE 10//最小分配空间大小.

#define RED FOREGROUND_RED
#define GREEN FOREGROUND_GREEN
#define BLUE FOREGROUND_BLUE

// 分配策略常量
#define FIRST_FIT 0        // 首次适应算法
#define NEXT_FIT 1         // 循环首次适应算法
#define BEST_FIT 2         // 最佳适应算法

typedef struct Bound{
	struct Bound * preLink;//头部域前驱
	struct Bound * upLink;//尾部域，指向结点头部
	int tag;//0标示空闲,1表示占用
	int size;//仅仅表示 可用空间，不包括 头部 和 尾部空间
	struct Bound * nextLink;//头部后继指针.
}*Space;

#define FOOT_LOC(p) ((p)+(p->size)-1)//尾部域位置

void initSpace(Space * freeSpace,Space * pav);
Space allocBoundTag(Space * pav,int size);
void reclaimBoundTag(Space * pav,Space sp);
void SetColor(int color);
void print(Space s);
void printSpace(Space pav);

Space userSpace[MAX_SIZE] = {NULL};//用户空间数组.
int usCount = 0;
int allocStrategy = FIRST_FIT; // 当前分配策略，默认为首次适应
Space nextFitStart = NULL;     // 循环首次适应算法的搜索起始位置

int main(int argc, char* argv[])
{
	// 设置控制台编码为UTF-8，解决中文乱码问题
	SetConsoleOutputCP(65001);
	setlocale(LC_ALL, "zh_CN.UTF-8");
	
	Space  freeSpace = NULL,pav = NULL;
	initSpace(&freeSpace,&pav);
	int item = 0, i = 0;
	unsigned long start = 0;
	unsigned long joblength;
	Space us = NULL;

	while(1)
	{
		SetColor(RED|BLUE|GREEN);
		printf("\n==================== 边界标识法内存管理系统 ====================\n");
		printf("选择功能项：\n");
		printf("  0 - 退出程序\n");
		printf("  1 - 分配内存\n");
		printf("  2 - 回收内存\n");
		printf("  3 - 显示内存\n");
		printf("  4 - 设置分配策略 (当前: ");
		switch(allocStrategy) {
			case FIRST_FIT: printf("首次适应"); break;
			case NEXT_FIT: printf("循环首次适应"); break;
			case BEST_FIT: printf("最佳适应"); break;
		}
		printf(")\n");
		printf("================================================================\n");
		printf("请选择功能项：");
		scanf("%d",&item);
		switch(item)
		{
			case 0:
				exit(0);
			case 1:
				SetColor(RED|GREEN);
				printf("所需内存长度：");
				scanf("%*c%ld",&joblength);
				allocBoundTag(&pav,joblength);
				break;
			case 2:
				SetColor(RED|BLUE);
				printf("输入要回收分区的首地址（十六进制）：");
				scanf("%x",&start);
				for (i = 0; i < usCount; i++){
					us = userSpace[i];
					if ((unsigned long)us == start){	 
						reclaimBoundTag(&pav, us);	
						break;
					}
				}
				if(i == usCount)
				{
					SetColor(RED);
					printf("输入要回收分区的首地址不符合要求\n");
				}
				if(pav != NULL && pav->size == MAX_SIZE)
				{
					usCount = 0;
				}
				break;
			case 3:		
				printSpace(pav);
				break;
			case 4:
				SetColor(GREEN|BLUE);
				printf("\n选择分配策略：\n");
				printf("  0 - 首次适应算法 (First Fit)\n");
				printf("  1 - 循环首次适应算法 (Next Fit)\n");
				printf("  2 - 最佳适应算法 (Best Fit)\n");
				printf("请输入策略编号：");
				scanf("%d",&allocStrategy);
				if(allocStrategy < 0 || allocStrategy > 2) {
					SetColor(RED);
					printf("无效的策略编号，已重置为首次适应算法\n");
					allocStrategy = FIRST_FIT;
				} else {
					SetColor(GREEN);
					printf("分配策略已更改为：");
					switch(allocStrategy) {
						case FIRST_FIT: printf("首次适应算法\n"); break;
						case NEXT_FIT: printf("循环首次适应算法\n"); nextFitStart = pav; break;
						case BEST_FIT: printf("最佳适应算法\n"); break;
					}
				}
				break;
			default:
				printf("没有该选项\n");
		}
	}

	return 0;
}

void initSpace(Space * freeSpace,Space * pav){
	//有2个空间是为了 查找空间的邻接点，防止出界用的。
	*freeSpace = (Space)malloc((MAX_SIZE+2)*sizeof(struct Bound));
	Space head = *freeSpace;
	head->tag = 1;//设置边界已占用
	head++;//指向第一个节点..
	head->tag = 0;//设置节点空闲.
	head->preLink = head->nextLink = head;//循环双链表..
	head->size = MAX_SIZE;
	*pav = head;//设置头指针
	Space foot = FOOT_LOC(head);
	foot->tag = 0;
	foot->upLink = head;
	foot++;
	foot->tag = 1;//设置 边界 已占用
}

// 首次适应算法 (First Fit)
Space allocFirstFit(Space * pav, int size) {
	if (*pav == NULL) return NULL;
	
	Space p = *pav;
	// 从表头开始查找第一个满足条件的空闲块
	do {
		if (p->size >= size) {
			*pav = p->nextLink;
			return p;
		}
		p = p->nextLink;
	} while (p != *pav);
	
	return NULL; // 未找到合适的空闲块
}

// 循环首次适应算法 (Next Fit)
Space allocNextFit(Space * pav, int size) {
	if (*pav == NULL) return NULL;
	
	// 如果nextFitStart为空或不在链表中，则从pav开始
	if (nextFitStart == NULL) {
		nextFitStart = *pav;
	}
	
	Space p = nextFitStart;
	Space firstCheck = p;
	
	// 从上次分配的位置开始查找
	do {
		if (p->size >= size) {
			nextFitStart = p->nextLink; // 更新下次搜索起点
			if (*pav == p) {
				*pav = p->nextLink;
			}
			return p;
		}
		p = p->nextLink;
	} while (p != firstCheck);
	
	return NULL; // 未找到合适的空闲块
}

// 最佳适应算法 (Best Fit)
Space allocBestFit(Space * pav, int size) {
	if (*pav == NULL) return NULL;
	
	Space p = *pav;
	Space bestFit = NULL;
	int minDiff = MAX_SIZE + 1;
	
	// 遍历所有空闲块，找到最适合的（大小最接近且不小于所需大小）
	do {
		if (p->size >= size) {
			int diff = p->size - size;
			if (diff < minDiff) {
				minDiff = diff;
				bestFit = p;
				// 如果找到完全匹配的块，直接返回
				if (diff == 0) break;
			}
		}
		p = p->nextLink;
	} while (p != *pav);
	
	if (bestFit != NULL) {
		// 如果最佳块是表头，则更新表头指针
		if (*pav == bestFit) {
			*pav = bestFit->nextLink;
		}
	}
	
	return bestFit;
}

Space allocBoundTag(Space * pav,int size){
	if (size <= 0) {
		SetColor(RED);
		printf("分配失败：请求的内存大小必须大于0\n");
		return NULL;
	}
	
	Space p = NULL;
	
	// 根据当前策略选择不同的分配算法
	switch(allocStrategy) {
		case FIRST_FIT:
			p = allocFirstFit(pav, size);
			break;
		case NEXT_FIT:
			p = allocNextFit(pav, size);
			break;
		case BEST_FIT:
			p = allocBestFit(pav, size);
			break;
		default:
			p = allocFirstFit(pav, size);
	}
	
	if (p == NULL) {
		SetColor(RED);
		printf("分配失败：没有足够的空闲空间\n");
		return NULL;
	}
	
	// 执行实际的分配操作
	if (p->size - size > ALLOC_MIN_SIZE){
		// 从高位截取p，不破坏指针间的关系
		p->size -= size;
		Space foot = FOOT_LOC(p);
		foot->upLink = p;
		foot->tag = 0;
		
		// 分配新的块
		p = foot + 1;
		p->size = size;
		foot = FOOT_LOC(p);
		p->tag = foot->tag = 1;
		foot->upLink = p;
	}
	else {
		// 分配后剩余空间小于 ALLOC_MIN_SIZE，整块分配
		if (p->nextLink == p) {
			// 只剩下一个空间了，清空指针
			*pav = NULL;
			nextFitStart = NULL;
			p->tag = 1;
		}
		else {
			// 直接分配 p->size个空间出去
			Space foot = FOOT_LOC(p);
			foot->tag = p->tag = 1;
			
			// 从链表中删除节点
			p->preLink->nextLink = p->nextLink;
			p->nextLink->preLink = p->preLink;
			
			// 更新nextFitStart，避免指向已分配的块
			if (nextFitStart == p) {
				nextFitStart = p->nextLink;
			}
		}
	}
	
	userSpace[usCount] = p;
	usCount++;
	
	SetColor(GREEN);
	printf("成功分配内存：地址=0x%p, 大小=%d\n", p, p->size);
	
	return p;
}
//回收空间，合并 邻接空闲空间.
void reclaimBoundTag(Space * pav,Space sp){
	Space pre = NULL;//前一个空间
	Space next = NULL;//后一个空间
	Space foot = NULL;
	int pTag = -1;
	int nTag = -1;
	int i = 0;

	// 获取相邻块信息
	if(*pav != NULL)
	{
		pre = (sp - 1)->upLink;//前一个空间（通过前一个尾部找到其头部）
		pTag = pre->tag;
		next = sp + sp->size;//后一个空间（当前块头部+大小）	
		nTag = next->tag;	
	}
	
	// 情况1：前后都被占用，或空闲链表为空
	if ((*pav != NULL && pTag == 1 && nTag == 1) || *pav == NULL){
		Space foot = FOOT_LOC(sp);
		foot->tag = sp->tag = 0;
		
		if (*pav == NULL){
			// 空闲链表为空，创建只有一个节点的循环链表
			*pav = sp->preLink = sp->nextLink = sp;
			nextFitStart = sp;
		}
		else{
			// 插入到表头
			sp->nextLink = *pav;
			sp->preLink = (*pav)->preLink;
			(*pav)->preLink->nextLink = sp;
			(*pav)->preLink = sp;
			*pav = sp;//将头指针指向刚释放的空间
			
			// 更新nextFitStart
			if (nextFitStart == NULL) {
				nextFitStart = sp;
			}
		}
		
		SetColor(GREEN);
		printf("已回收内存（独立块）：地址=0x%p, 大小=%d\n", sp, sp->size);
	}
	// 情况2：只有前面的可以合并
	else if(pTag == 0 && nTag == 1){
		int oldSize = pre->size;
		pre->size += sp->size;
		foot = FOOT_LOC(pre);
		foot->tag = 0;
		foot->upLink = pre;
		
		SetColor(GREEN);
		printf("已回收内存（与前块合并）：地址=0x%p, 原大小=%d, 合并后大小=%d\n", 
			   pre, oldSize, pre->size);
	}
	// 情况3：只有后面的可以合并
	else if(pTag == 1 && nTag == 0){
		// 更新表头指针（如果需要）
		if(*pav == next)
		{
			*pav = sp;
		}
		
		// 更新nextFitStart（如果需要）
		if(nextFitStart == next)
		{
			nextFitStart = sp;
		}
		
		// 从链表中删除next节点，用sp替换
		sp->preLink = next->preLink;
		sp->nextLink = next->nextLink;
		sp->preLink->nextLink = sp;
		sp->nextLink->preLink = sp;
		
		// 合并大小
		sp->size += next->size;
		foot = FOOT_LOC(sp);
		sp->tag = foot->tag = 0;
		foot->upLink = sp;
		
		SetColor(GREEN);
		printf("已回收内存（与后块合并）：地址=0x%p, 合并后大小=%d\n", sp, sp->size);
	}
	// 情况4：前后都可以合并
	else{
		// 更新表头指针（如果需要）
		if(*pav == next)
		{
			*pav = pre;
		}
		
		// 更新nextFitStart（如果需要）
		if(nextFitStart == next)
		{
			nextFitStart = pre;
		}
		
		int oldSize = pre->size;
		// 合并三个块：pre + sp + next
		pre->size += sp->size + next->size;
		
		// 从链表中删除next节点
		pre->nextLink = next->nextLink;
		next->nextLink->preLink = pre;
		
		// 更新尾部
		foot = FOOT_LOC(pre);
		foot->tag = 0;
		foot->upLink = pre;
		
		SetColor(GREEN);
		printf("已回收内存（与前后块合并）：地址=0x%p, 原大小=%d, 合并后大小=%d\n", 
			   pre, oldSize, pre->size);
	}
	
	//设置用户空间
	for (i = 0; i < usCount; i++){
		if (sp == userSpace[i]){
			userSpace[i] = NULL;
			break;
		}
	}
}

/* 设置字体颜色 */
void SetColor(int color)
{
	SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), 
		FOREGROUND_INTENSITY | color);
}

void print(Space s){
	printf("0x%0x    %6d\t%10d           0x%0x  0x%0x\n",s,s->size,s->tag, s->preLink,s->nextLink);
}

void printSpace(Space pav){
	SetColor(RED|GREEN|BLUE);
	printf("空间首地址  空间大小  块标志(0:空闲,1:占用)  前驱地址  后继地址\n");
	SetColor(GREEN);
	int i = 0;
	Space p = NULL, us = NULL;

	if (pav != NULL)
	{
		p = pav;
		print(p);
		for (p = p->nextLink; p != pav; p = p->nextLink){
			print(p);
			i++;
		}
	}
	for (i = 0; i < usCount; i++){
		us = userSpace[i];
		if (us){
			printf("0x%0x    %6d\t%10d\t\n",us, us->size, us->tag);  
		}
	}
}

