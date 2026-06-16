;
; Array Sum Example
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

array_sum:
        daddi r2,r0,0       ; r2 = i = 0
        daddi r10,r0,0      ; r10 = sum = 0

sum_loop:
        slt r3,r2,r17       ; r3 = (i < N) ? 1 : 0
        beqz r3,end_sum     ; if i >= N, exit loop
        
        dsll r4,r2,3        ; r4 = i * 8
        dadd r5,r16,r4      ; r5 = A 基地址 + 偏移
        ld r6,(r5)          ; r6 = A[i]
        
        dadd r10,r10,r6     ; sum = sum + A[i]
        
        daddi r2,r2,1       ; i = i + 1
        j sum_loop

end_sum:
        jr r31
	

