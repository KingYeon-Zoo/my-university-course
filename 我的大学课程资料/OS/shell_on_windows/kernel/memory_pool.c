/*
 * memory_pool.c - 内存池实现模块
 * 
 * 本文件实现了一个简单但高效的内存池，用于批量管理内存分配。
 * 
 * 内存池的优势:
 * 1. 减少内存碎片 - 统一管理内存分配
 * 2. 提高性能 - 减少频繁的malloc/free调用
 * 3. 简化清理 - 销毁池时自动释放所有分配的内存
 * 4. 防止内存泄漏 - 即使忘记释放某块内存，池销毁时也会处理
 * 
 * 实现原理:
 * 使用链表记录所有通过池分配的内存块。
 * 每次分配都会创建一个节点加入链表，记录分配的指针和大小。
 * 销毁池时遍历链表，释放所有记录的内存块。
 * 
 * 适用场景:
 * - 需要在函数内分配多块内存，函数结束时统一释放
 * - 解析过程中需要分配大量临时内存
 * - 希望简化内存管理，避免逐个释放的麻烦
 */

#include "include/types.h"     /* 数据结构定义 */
#include "include/internal.h"  /* 内部接口定义 */
#include <stdlib.h>            /* malloc, free */
#include <string.h>            /* memset */

/*
 * pool_create - 创建一个新的内存池
 * 
 * @返回值: 成功返回内存池指针，失败返回NULL
 * 
 * 创建一个空的内存池，准备接受后续的内存分配请求。
 * 新池的统计信息都初始化为0。
 * 
 * 使用示例:
 *   struct mem_pool *pool = pool_create();
 *   if (pool) {
 *       char *str = pool_alloc(pool, 100);
 *       int *arr = pool_alloc(pool, sizeof(int) * 50);
 *       // 使用分配的内存...
 *       pool_destroy(pool);  // 一次性释放所有内存
 *   }
 */
struct mem_pool *pool_create(void)
{
	struct mem_pool *pool;
	
	/* 分配内存池结构体 */
	pool = (struct mem_pool *)malloc(sizeof(struct mem_pool));
	if (!pool)
		return NULL;  /* 内存分配失败 */
	
	/* 初始化内存池 */
	pool->head = NULL;            /* 分配链表为空 */
	pool->total_allocated = 0;    /* 已分配总量为0 */
	pool->block_count = 0;        /* 分配块数为0 */
	
	return pool;
}

/*
 * pool_alloc - 从内存池中分配内存
 * 
 * @pool: 内存池指针
 * @size: 要分配的字节数
 * @返回值: 成功返回分配的内存指针，失败返回NULL
 * 
 * 此函数从系统堆分配指定大小的内存，并将其注册到内存池中。
 * 分配的内存会被初始化为0（使用memset）。
 * 
 * 与直接使用malloc的区别:
 * - 分配的内存被池管理，无需单独释放
 * - 内存已初始化为0
 * - 池会跟踪分配统计信息
 * 
 * 注意: 不要对返回的指针调用free()，内存会在pool_destroy时释放。
 */
void *pool_alloc(struct mem_pool *pool, size_t size)
{
	struct mem_pool_node *node;
	void *ptr;
	
	/* 参数检查 */
	if (!pool || size == 0)
		return NULL;
	
	/* 分配实际的数据内存 */
	ptr = malloc(size);
	if (!ptr)
		return NULL;  /* 内存分配失败 */
	
	/* 创建池节点来跟踪这次分配 */
	node = (struct mem_pool_node *)malloc(sizeof(struct mem_pool_node));
	if (!node) {
		/* 节点分配失败，需要释放刚才分配的内存 */
		free(ptr);
		return NULL;
	}
	
	/* 设置节点信息 */
	node->ptr = ptr;           /* 记录分配的内存指针 */
	node->size = size;         /* 记录分配的大小 */
	
	/* 将节点插入链表头部（头插法，O(1)时间复杂度） */
	node->next = pool->head;
	pool->head = node;
	
	/* 更新统计信息 */
	pool->total_allocated += size;
	pool->block_count++;
	
	/* 将分配的内存初始化为0 */
	memset(ptr, 0, size);
	
	return ptr;
}

/*
 * pool_destroy - 销毁内存池并释放所有分配的内存
 * 
 * @pool: 要销毁的内存池指针
 * 
 * 此函数会:
 * 1. 遍历分配链表
 * 2. 释放每个节点记录的内存块
 * 3. 释放每个节点本身
 * 4. 释放内存池结构体
 * 
 * 调用此函数后:
 * - pool指针失效，不能再使用
 * - 所有从该池分配的内存都被释放，指针失效
 * 
 * 使用示例:
 *   pool_destroy(pool);
 *   pool = NULL;  // 建议将指针置空，防止误用
 */
void pool_destroy(struct mem_pool *pool)
{
	struct mem_pool_node *node, *next;
	
	/* NULL检查 */
	if (!pool)
		return;
	
	/* 遍历链表，释放所有分配的内存 */
	node = pool->head;
	while (node) {
		next = node->next;      /* 保存下一个节点的指针 */
		free(node->ptr);        /* 释放数据内存 */
		free(node);             /* 释放节点本身 */
		node = next;            /* 移动到下一个节点 */
	}
	
	/* 释放内存池结构体 */
	free(pool);
}
