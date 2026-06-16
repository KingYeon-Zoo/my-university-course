SECTIONS
{
	. = 0x1000;
	.text : {
		start.o
		* (.text)
	}
    		
	.data : {
		* (.data)
	}
	
	bss_start = .; 
	.bss : {
		* (.bss)
	}
	bss_end  = .;	
}
