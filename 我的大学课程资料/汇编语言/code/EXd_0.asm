;转换大小写
dseg segment
        MaxLength    DB 100
        ActualLength DB ?
        STRING       DB 100 DUP(?)
        ChangeRow    DB 0DH,0AH,'$'
dseg ends

sseg segment
sseg ends

cseg segment
                assume cs:cseg,ds:dseg,ss:sseg        ;装载
        MAIN:   
                mov    ax,dseg
                mov    ds,ax
        INPUT:  
                MOV    DX,OFFSET MaxLength
                MOV    AH,10
                INT    21H

        ;大小写转换
                MOV    BX,OFFSET STRING
                MOV    CH,0
                MOV    CL,ActualLength;CX=ACTUALLENGTH
        PROCESS:
                MOV    AL,[BX]
                CALL   TurnSmall
                MOV    [BX],AL
                INC    BX
                LOOP   PROCESS
        
        ADDtail:
                MOV    BX,OFFSET STRING
                MOV    DH,0
                MOV    DL,ActualLength
                ADD    BX,DX

                MOV    AL,24H;'$'
                MOV    [BX],AL

        OUTPUT: MOV    DX,OFFSET ChangeRow
                MOV    AH,9
                INT    21H
                
                MOV    DX,OFFSET STRING
                MOV    AH,9
                INT    21H

        END:    MOV    AH,4CH
                INT    21H

        
TurnSmall PROC
        ;AL中的字符作大小写转换
                CMP    AL,'a'
                JGE    DONE
        ;小写=大写+20H
                ADD    AL,20H
        DONE:   
                RET
TurnSmall ENDP

CSEG ENDS
        END MAIN
