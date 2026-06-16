link.bin: start.o main.o clock.o uart.o
	arm-linux-ld -T  link.lds -o link.elf start.o main.o clock.o uart.o
	arm-linux-objcopy -O binary link.elf link.bin
	arm-linux-objdump -D link.elf > link.dis

%.o : %.S
	arm-linux-gcc -o $@ $< -c

%.o : %.c
	arm-linux-gcc -o $@ $< -c -fno-builtin 

clean:
	rm *.o *.elf *.bin *.dis -f
