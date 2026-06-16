.data
A: .word 10
B: .word 8
C: .word 0
.text
main:
ld r4,A(r0)
ld r5,B(r0)
halt