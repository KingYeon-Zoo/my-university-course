mmu.bin: start.o clock.o sdram.o mmu.o main.o
	arm-linux-ld -T mmu.lds -o mmu.elf $^
	arm-linux-objcopy -O binary mmu.elf mmu.bin
	arm-linux-objdump -D mmu.elf > mmu.dis

%.o : %.S
	arm-linux-gcc -o $@ $< -c

%.o : %.c
	arm-linux-gcc -o $@ $< -c
	
clean:
	rm *.o *.elf *.bin *.dis -f
