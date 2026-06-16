DATA SEGMENT
    MAXLENGTH    DB 100           ;一个字节，用它存最大的长度
    ACTUALLENGTH DB ?             ;一个字节，用它存实际的长度，在指令执行后会被填写
    SRTING       DB 100 DUP(?)    ;用来存字符串
DATA ENDS

STACK SEGMENT
STACK ENDS

CODE SEGMENT
         ASSUME DS:DATA,SS:STACK,CS:CODE
    MAIN:
         MOV    AX,DATA
         MOV    DS,AX

         MOV    DX,OFFSET MAXLENGTH         ;把需要用到的内存块（三个部分）的地址存入DX
         MOV    AH,10
         INT    21H

         MOV    AH,4CH
         INT    21H
CODE ENDS
END MAIN