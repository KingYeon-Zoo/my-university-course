;Z=X+Y PROC
DATA SEGMENT
    X    DW 1234H
    Y    DW 2345H
    Z    DW ?
DATA ENDS

STACK SEGMENT
STACK ENDS

CODE SEGMENT
         ASSUME DS:DATA,SS:STACK,CS:CODE
    MAIN:
         MOV    AX,DATA
         MOV    DS,AX

         MOV    AX,X
         PUSH   AX
         MOV    AX,Y
         PUSH   AX

         CALL   SUM
         MOV    Z,AX

         MOV    AH,4CH
         INT    21H

SUM PROC ;取两个栈顶元素，返回和储存到AX中
         MOV    BP,SP
         MOV    AX,[BP+2]
         ADD    AX,[BP+4]
         RET
SUM ENDP

CODE ENDS
END MAIN