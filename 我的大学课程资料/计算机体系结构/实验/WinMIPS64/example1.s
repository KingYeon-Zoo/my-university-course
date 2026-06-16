;
; Vector-Scalar Addition Example
; Computes A[i] = B[i] + C for i=0 to N-1
; Results stored in array A
;

	.data
; 定义数组 B 的初始值
arrayB: .word 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
; 分配数组 A 的空间
arrayA: .word 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
; 标量 C
scalar: .word 5
; 数组长度 N
length: .word 10

title:  .asciiz "Vector-Scalar Addition Program\n"
result_msg: .asciiz "Results in array A:\n"

CONTROL: .word32 0x10000
DATA:    .word32 0x10008

        .text

main:   lwu r21,CONTROL(r0)
        lwu r22,DATA(r0)
        
        ; 输出标题
        daddi r24,r0,4      ; ascii output
        daddi r1,r0,title   
        sd r1,(r22)
        sd r24,(r21)

        ; 初始化寄存器
        daddi r16,r0,arrayA ; r16 = $s0 = 数组 A 的基地址
        daddi r17,r0,arrayB ; r17 = $s1 = 数组 B 的基地址
        ld r18,scalar(r0)   ; r18 = $s2 = 标量 C
        ld r19,length(r0)   ; r19 = $s3 = 长度 N
        
        ; 调用向量加法函数
        jal vector_add
        
        ; 输出结果提示
        daddi r24,r0,4      ; ascii output
        daddi r1,r0,result_msg
        sd r1,(r22)
        sd r24,(r21)
        
        ; 输出数组 A 的结果
        daddi r5,r0,0       ; i = 0
output_loop:
        slt r6,r5,r19       ; if i < N
        beqz r6,finish      ; if not, finish
        
        dsll r7,r5,3        ; r7 = i * 8 (每个字是8字节)
        dadd r8,r16,r7      ; r8 = A 的地址 + 偏移
        ld r9,(r8)          ; r9 = A[i]
        
        daddi r24,r0,1      ; integer output
        sd r9,(r22)
        sd r24,(r21)
        
        daddi r5,r5,1       ; i++
        j output_loop

finish: halt

;
; 向量加法函数
; 参数：
;   r16 ($s0) = 数组 A 的基地址
;   r17 ($s1) = 数组 B 的基地址
;   r18 ($s2) = 标量 C
;   r19 ($s3) = 长度 N
;

vector_add:
        daddi r2,r0,0       ; r2 = i = 0

loop:   slt r3,r2,r19       ; r3 = (i < N) ? 1 : 0
        beqz r3,end_loop    ; if i >= N, exit loop
        
        ; 计算 B[i] 的地址并加载
        dsll r4,r2,3        ; r4 = i * 8 (每个字是8字节)
        dadd r5,r17,r4      ; r5 = B 基地址 + 偏移
        ld r6,(r5)          ; r6 = B[i]
        
        ; 计算 B[i] + C
        dadd r7,r6,r18      ; r7 = B[i] + C
        
        ; 存储到 A[i]
        dadd r8,r16,r4      ; r8 = A 基地址 + 偏移
        sd r7,(r8)          ; A[i] = B[i] + C
        
        ; i++
        daddi r2,r2,1       ; i = i + 1
        j loop              ; 继续循环

end_loop:
        jr r31              ; 返回
	