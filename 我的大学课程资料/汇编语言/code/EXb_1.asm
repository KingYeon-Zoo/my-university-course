DATA SEGMENT
        X    DW 1234H
        Y    DW 2345H
        Z    DW -1234H
        W    DW ?
DATA ENDS

STACK SEGMENT
        NUMS  DW 100H DUP(?)
        TOP   DW LENGTH NUMS
STACK ENDS

CODE SEGMENT
                ASSUME DS:DATA,SS:STACK,CS:CODE
        MAIN:   
                MOV    AX,DATA
                MOV    DS,AX
                MOV    AX,STACK
                MOV    SS,AX
                MOV    AX,TOP
                MOV    SP,AX

                MOV    AX,X
                PUSH   AX
                MOV    AX,Y
                PUSH   AX
                MOV    AX,Z
                PUSH   AX

                CALL   MAXIMUM
                MOV    W,AX

                MOV    AH,4CH
                INT    21H

MAXIMUM PROC
                MOV    BP,SP
                MOV    AX,[BP+2]                       ;Z
                CMP    AX,[BP+4]                       ;Y,Z
                JGE    DONE
                MOV    AX,[BP+4]
        DONE:   
                CMP    AX,[BP+6]
                JGE    DONE2
                MOV    AX,[BP+6]
        DONE2:  
                RET
MAXIMUM ENDP

CODE ENDS
END MAIN