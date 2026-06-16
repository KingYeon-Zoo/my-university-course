nand.bin : start.o clock.o sdram.o main.o uart.o nand.o
	arm-linux-ld  -T nand.lds -o nand.elf $^
	arm-linux-objcopy -O binary nand.elf nand.bin
	arm-linux-objdump -D nand.elf > nand.dis

%.o : %.S
	arm-linux-gcc -g -c -O2 -o $@ $^

%.o : %.c
	arm-linux-gcc -g -c -O2 -o $@ $^ -fno-builtin 

clean:
	rm -f *.o *.bin *.elf *.dis	
