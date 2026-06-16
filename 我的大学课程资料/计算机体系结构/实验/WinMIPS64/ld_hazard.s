.data
A: .word 10
B: .word 8
C: .word 0
.text
main:
ld r3,B(r0)
ld r10,A(r0)
dsub r11,r10,r3
halt