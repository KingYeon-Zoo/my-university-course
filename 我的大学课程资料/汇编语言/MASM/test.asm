.model small
.stack 100h

.data
numbers db 23, 74, 18, 45, 63, 9, 81, 4, 59, 32
        db 79, 40, 69, 17, 53, 93, 86, 48, 20, 29
        db 11, 97, 33, 64, 38, 82, 43, 72, 57, 7
        db 3, 13, 88, 76, 52, 24, 36, 71, 26, 34
        db 21, 60, 83, 5, 41, 65, 19, 67, 56, 85
sum dw ?
count equ 50
average dw ?
max db ?
min db ?
prompt_sum db "sum: ", 0dh, 0ah, '$'
prompt_average db "average: ", 0dh, 0ah, '$'
prompt_max db "max: ", 0dh, 0ah, '$'
prompt_min db "min: ", 0dh, 0ah, '$'

.code
org 100h

main proc
    mov ax, @data
    mov ds, ax
    call compute_sum
    call compute_average
    call compute_max_min
    call display_results
    mov ah, 4Ch
    int 21h
main endp

compute_sum proc
    lea si, numbers
    mov cx, count
    xor ax, ax
sum_loop:
    add al, [si]
    adc ah, 0
    inc si
    loop sum_loop
    mov sum, ax
    ret
compute_sum endp

compute_average proc
    mov bx, count
    mov ax, sum
    xor dx, dx
    div bx
    mov average, ax
    ret
compute_average endp

compute_max_min proc
    lea si, numbers
    mov al, [si]
    mov max, al
    mov min, al
    inc si
    mov cx, count-1
find_min:
    mov al, [si]
    cmp al, min
    jnb not_below
    mov min, al
not_below:
    inc si
    loop find_min
    lea si, numbers
    mov cx, count
find_max:
    mov al, [si]
    cmp al, max
    jna not_above
    mov max, al
not_above:
    inc si
    loop find_max
    ret
compute_max_min endp

display_results proc
    lea dx, prompt_sum
    mov ah, 09h
    int 21h
    mov ax, sum
    call print_number
    lea dx, prompt_average
    mov ah, 09h
    int 21h
    mov ax, average
    call print_number
    lea dx, prompt_max
    mov ah, 09h
    int 21h
    xor ah, ah
    mov al, max
    call print_number
    lea dx, prompt_min
    mov ah, 09h
    int 21h
    xor ah, ah
    mov al, min
    call print_number
    ret
display_results endp

print_number proc
    push ax
    push bx
    push cx
    push dx
    xor cx, cx
print_digit_loop:
    xor dx, dx
    mov bx, 10
    div bx
    add dl, '0'
    push dx
    inc cx
    test ax, ax
    jnz print_digit_loop
print_digits:
    pop dx
    mov ah, 02h
    int 21h
    loop print_digits
print_newline:
    mov ah, 02h
    mov dl, 0dh
    int 21h
    mov dl, 0ah
    int 21h
    pop dx
    pop cx
    pop bx
    pop ax
    ret
print_number endp

end main
