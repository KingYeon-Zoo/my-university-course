;
; Array Sum Example - Optimized with Instruction Scheduling
; 采用指令调度技术消除数据相关
; Computes sum = sum + A[i] for i=0 to N-1
; Returns sum in r10
;

	.data
arrayA: .word 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
length: .word 12
title:  .asciiz "array sum= "

CONTROL: .word32 0x10000
DATA:    .word32 0x10008

        .text

        lwu r21,CONTROL(r0)
        lwu r22,DATA(r0)
        daddi r24,r0,4      ; ascii output
        daddi r1,r0,title   
        sd r1,(r22)
        sd r24,(r21)

        daddi r16,r0,arrayA ; r16 = 数组 A 的基地址
        ld r17,length(r0)   ; r17 = 长度 N
        jal array_sum
        
        daddi r24,r0,1      ; integer output
        sd r10,(r22)
        sd r24,(r21)
        halt

;
; parameter: r16 = array base, r17 = length
; return value in r10
;
; 优化策略：
; 1. 软件流水线：将下一次迭代的地址计算与当前迭代的数据使用交错
; 2. 循环展开：提前加载第一个元素，避免循环内的初始化开销
; 3. 指令重排：在load和use之间插入独立指令，隐藏load延迟
;

array_sum:
        daddi r2,r0,0       ; r2 = i = 0
        daddi r10,r0,0      ; r10 = sum = 0
        beqz r17,end_sum    ; 边界检查：如果长度为0，直接退出
        
        ; === 循环预处理：预加载第一个元素 ===
        dsll r4,r2,3        ; r4 = 0 * 8
        daddi r2,r2,1       ; i = 1 (提前递增，与dsll无关)
        dadd r5,r16,r4      ; r5 = A[0] 地址
        slt r3,r2,r17       ; 预先检查 i=1 是否 < N (与load独立)
        ld r6,(r5)          ; 加载 A[0]

sum_loop:
        ; === 指令调度后的循环体 ===
        ; 此时 r6 中已经有了 A[i-1] 的值
        ; r3 中已经有了下一次循环的条件判断结果
        
        dsll r4,r2,3        ; r4 = i * 8 (计算下一个元素的偏移)
        dadd r10,r10,r6     ; sum = sum + A[i-1] (使用已加载的值)
        dadd r5,r16,r4      ; r5 = A + i*8 (计算下一个元素地址)
        
        beqz r3,end_sum     ; 如果 i >= N，退出循环
        
        daddi r2,r2,1       ; i = i + 1 (为下下次迭代准备)
        slt r3,r2,r17       ; 预先计算下次循环条件 (在load期间执行)
        ld r6,(r5)          ; 加载 A[i] (延迟在下次循环开始前有足够指令隐藏)
        
        j sum_loop

end_sum:
        jr r31
	

; ========================================
; 优化效果分析：
; ========================================
;
; 原始版本的关键路径 (每次迭代)：
;   slt -> beqz (1 stall)
;   dsll -> dadd (可能1 stall)  
;   dadd -> ld (可能1 stall)
;   ld -> dadd (2-3 stalls, load-use hazard)
;   总计：约 4-6 个 stall/iteration
;
; 优化版本的关键路径 (每次迭代)：
;   load 延迟被后续的 dsll, dadd, daddi, slt 等指令隐藏
;   分支延迟被提前计算的 slt 减少
;   总计：约 0-2 个 stall/iteration
;
; 性能提升：理论上可减少 50-75% 的 stall 周期
;

