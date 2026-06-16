SECTIONS
{
    . = 0x50000000;
    
    .text : {
        start.o (.text)
        * (.text)
    }
    
    .data : {
        * (.data)
    }
    
    .bss : {
        * (.bss)
    }
} 