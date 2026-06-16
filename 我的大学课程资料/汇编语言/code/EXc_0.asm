;(Array initialization) Allocate 100 bytes of dseg, and assign value from 0-99 to those bytes.

dseg segment
      array db  100 dup(?)
dseg ends

sseg segment
sseg ends

cseg segment
            assume cs:cseg,ds:dseg,ss:sseg      ;装载
      start:
            mov    ax,dseg
            mov    ds,ax   ;用ax中转，将dseg的首地址赋给ds

            mov    si,OFFSET array  ;起始地址
            
            mov    cx,100   ;计数器
            mov    dl,0
      main: 
            mov    [si],dl
            inc    si
            inc    dl
            loop   main

            mov    ah,4ch
            int    21h
cseg ends
        end start
