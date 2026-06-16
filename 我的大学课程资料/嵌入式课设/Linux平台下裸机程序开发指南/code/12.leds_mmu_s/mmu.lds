SECTIONS {
    . = 0xc0000000;
    
	.text : {
			start.o
			sdram.o
			mmu.o
			mmu2.o
			clock.o
			* (.text)
	}

	.rodata : {
			* (.rodata)
	}

	.data : {
			* (.data)
	}

    bss_start = .;
    .bss ALIGN(4)  : { *(.bss)  *(COMMON) }
    bss_end = .;
}
