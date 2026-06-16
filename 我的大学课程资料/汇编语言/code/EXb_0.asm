DATA SEGMENT
      X    DW 1234H
      Y    DW 2345H
      Z    DW -1234H
      W    DW ?
DATA ENDS

STACK SEGMENT
STACK ENDS

CODE SEGMENT
            ASSUME DS:DATA,SS:STACK,CS:CODE
      MAIN: 
            MOV    AX,DATA
            MOV    DS,AX

            MOV    AX,X
            CMP    AX,Y                          ;试着保持AX中一直存储最大值
            JGE    DONE
      ;AX<Y
            MOV    AX,Y
      DONE: 
            CMP    AX,Z
            JGE    DONE2
            MOV    AX,Z
      DONE2:
            MOV    W,AX
      END:  
            MOV    AH,4CH
            INT    21H
CODE ENDS
END MAIN