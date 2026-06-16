clock.bin: start.o clock.o main.o
	arm-linux-ld -Ttext 0x50000000 -o clock.elf start.o clock.o main.o
	arm-linux-objcopy -O binary clock.elf clock.bin
	arm-linux-objdump -D clock.elf > clock.dis

%.o : %.S
	arm-linux-gcc -o $@ $< -c

%.o : %.c
	arm-linux-gcc -o $@ $< -c
	
clean:
	rm *.o *.elf *.bin *.dis
