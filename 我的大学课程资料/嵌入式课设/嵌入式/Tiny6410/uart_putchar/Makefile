uart.bin: start.o main.o uart.o clock.o
	arm-linux-ld -Ttext 0x50000000 -o uart.elf $^
	arm-linux-objcopy -O binary uart.elf uart.bin
	arm-linux-objdump -D uart.elf > uart.dis

%.o : %.S
	arm-linux-gcc -o $@ $< -c

%.o : %.c
	arm-linux-gcc -o $@ $< -c -fno-builtin 

clean:
	rm *.o *.elf *.bin *.dis  -rf
