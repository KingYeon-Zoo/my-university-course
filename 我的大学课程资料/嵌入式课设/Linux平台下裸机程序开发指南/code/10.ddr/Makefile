ddr.bin : start.o clock.o sdram.o main.o uart.o
	arm-linux-ld  -T ddr.lds -o ddr.elf $^
	arm-linux-objcopy -O binary ddr.elf ddr.bin
	arm-linux-objdump -D ddr.elf > ddr.dis

%.o : %.S
	arm-linux-gcc -g -c -O2 -o $@ $^

%.o : %.c
	arm-linux-gcc -g -c -O2 -o $@ $^ -fno-builtin 

clean:
	rm -f *.o *.bin *.elf *.dis	
