data segment  
    msg_bit0 db 'The 0 Bit is 1', 0dh,0ah,'$'
    msg_bit1 db 'The 1 Bit is 1', 0dh,0ah,'$'
    msg_bit2 db 'The 2 Bit is 1', 0dh,0ah,'$'
    msg_bit3 db 'The 3 Bit is 1', 0dh,0ah,'$'
    msg_bit4 db 'The 4 Bit is 1', 0dh,0ah,'$'
    msg_bit5 db 'The 5 Bit is 1', 0dh,0ah,'$'
    msg_bit6 db 'The 6 Bit is 1', 0dh,0ah,'$'
    msg_bit7 db 'The 7 Bit is 1', 0dh,0ah,'$'
msg_table:
    dw offset msg_bit0
    dw offset msg_bit1
    dw offset msg_bit2
    dw offset msg_bit3
    dw offset msg_bit4
    dw offset msg_bit5
    dw offset msg_bit6
    dw offset msg_bit7
data ends

stack segment
stack ends

code segment
assume cs:code, ds:data, ss:stack

start:
    mov ax, data         
    mov ds, ax

    mov bl, 00000001b    
    xor cx, cx           
    
check_bits:
    test bl, 1           
    jz next_bit          

    lea si, msg_table    
    mov di, cx           
    shl di, 1            
    add si, di           
    mov dx, [si]         

    mov ah, 09h          
    int 21h              

next_bit:
    shr bl, 1            
    inc cx               
    cmp cx, 8            
    jb check_bits        

exit_program:
    mov ah, 4Ch          
    int 21h

code ends
end start