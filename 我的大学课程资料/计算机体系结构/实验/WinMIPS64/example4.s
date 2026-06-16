;
; Array Sum Example - Loop Unrolling + Register Renaming + Instruction Scheduling
; 采用循环展开、寄存器换名和指令调度技术进一步提高性能
; 循环展开因子 = 4
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
; 1. 循环展开4次：每次迭代处理4个数组元素，减少循环开销
; 2. 寄存器换名：为4个元素使用不同的寄存器，消除伪相关
; 3. 指令调度：将地址计算、加载和累加操作重新排列，最大化隐藏load延迟
;
; 寄存器分配：
;   r16: 数组基地址
;   r17: 数组长度
;   r2:  循环计数器 i
;   r10: sum 累加器
;   r4, r11, r12, r13: 地址偏移 (i*8, (i+1)*8, (i+2)*8, (i+3)*8)
;   r5, r14, r15, r18: 计算的地址
;   r6, r7, r8, r9:    加载的数据 A[i], A[i+1], A[i+2], A[i+3]
;

array_sum:
        daddi r2,r0,0       ; r2 = i = 0
        daddi r10,r0,0      ; r10 = sum = 0
        beqz r17,end_sum    ; 边界检查：如果长度为0，直接退出
        
        ; 检查是否至少有4个元素
        slti r3,r17,4       ; r3 = (N < 4)
        bnez r3,remainder_loop  ; 如果 N < 4，直接处理剩余元素

unrolled_loop:
        ; === 第一阶段：计算4个元素的地址偏移 ===
        ; 通过寄存器换名，避免数据相关
        dsll r4,r2,3        ; r4 = i * 8
        daddi r19,r2,1      ; r19 = i + 1
        daddi r20,r2,2      ; r20 = i + 2
        daddi r25,r2,3      ; r25 = i + 3
        
        dsll r11,r19,3      ; r11 = (i+1) * 8
        dsll r12,r20,3      ; r12 = (i+2) * 8
        dsll r13,r25,3      ; r13 = (i+3) * 8
        
        ; === 第二阶段：计算4个元素的实际地址 ===
        dadd r5,r16,r4      ; r5 = &A[i]
        dadd r14,r16,r11    ; r14 = &A[i+1]
        dadd r15,r16,r12    ; r15 = &A[i+2]
        dadd r18,r16,r13    ; r18 = &A[i+3]
        
        ; === 第三阶段：加载4个元素 ===
        ; 连续发射load指令，利用流水线并行性
        ld r6,(r5)          ; load A[i]
        ld r7,(r14)         ; load A[i+1]
        ld r8,(r15)         ; load A[i+2]
        ld r9,(r18)         ; load A[i+3]
        
        ; === 第四阶段：在load延迟期间更新循环变量 ===
        daddi r2,r2,4       ; i = i + 4
        daddi r26,r2,4      ; r26 = i + 4 (预测下一次的i+4)
        slt r3,r26,r17      ; r3 = ((i+4) < N) ? 1 : 0
        
        ; === 第五阶段：累加操作 ===
        ; 此时load的数据已经可用，隐藏了延迟
        dadd r10,r10,r6     ; sum += A[i]
        dadd r10,r10,r7     ; sum += A[i+1]
        dadd r10,r10,r8     ; sum += A[i+2]
        dadd r10,r10,r9     ; sum += A[i+3]
        
        ; === 循环判断 ===
        bnez r3,unrolled_loop  ; 如果还有完整的4元素块，继续

remainder_loop:
        ; === 处理剩余元素 (0-3个) ===
        slt r3,r2,r17       ; r3 = (i < N)
        beqz r3,end_sum     ; 如果没有剩余元素，退出
        
        dsll r4,r2,3        ; r4 = i * 8
        dadd r5,r16,r4      ; r5 = &A[i]
        ld r6,(r5)          ; load A[i]
        
        daddi r2,r2,1       ; i++
        dadd r10,r10,r6     ; sum += A[i]
        
        j remainder_loop

end_sum:
        jr r31
	

; ========================================
; 优化效果分析：
; ========================================
;
; 优化前 (example3.s)：
;   每次迭代处理1个元素
;   循环体约10条指令
;   每次迭代约0-2个stall
;   处理12个元素：12次迭代 = 120-144个周期
;
; 优化后 (循环展开4次 + 寄存器换名 + 指令调度)：
;   每次迭代处理4个元素
;   循环体约25条指令
;   处理12个元素：3次迭代 = 75-90个周期
;
; 性能提升原因：
; 1. 循环开销减少75% (12次循环变为3次)
; 2. 寄存器换名消除了伪相关，允许更激进的指令调度
; 3. 4个load指令可以在流水线中并行执行
; 4. 地址计算、load和累加操作分阶段执行，最大化隐藏延迟
; 5. 在load延迟期间更新循环变量，充分利用执行单元
;
; 理论性能提升：约 40-50% (相比example3.s)
;
; 进一步优化可能性：
; - 展开因子增加到8或16（如果寄存器足够）
; - 使用软件流水线技术进一步优化
; - 采用多累加器技术减少累加链的依赖
;


