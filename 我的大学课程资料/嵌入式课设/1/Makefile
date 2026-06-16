
CC      = arm-linux-gcc
LD      = arm-linux-ld
AR      = arm-linux-ar
OBJCOPY = arm-linux-objcopy
OBJDUMP = arm-linux-objdump

INCLUDEDIR 	:= $(shell pwd)/include
CFLAGS 		:= -Wall -Os -fno-builtin
CPPFLAGS   	:= -nostdinc -I$(INCLUDEDIR)

export 	CC AR LD OBJCOPY OBJDUMP INCLUDEDIR CFLAGS CPPFLAGS 

objs := start.o  clock.o uart.o timer.o sdram.o main.o lib/libc.a nand.o

keypad_led_controller.bin: $(objs)
	${LD} -Ttimer.lds -o keypad_led_controller.elf $^
	${OBJCOPY} -O binary -S keypad_led_controller.elf $@
	${OBJDUMP} -D keypad_led_controller.elf > keypad_led_controller.dis

.PHONY : lib/libc.a
lib/libc.a:
	cd lib; make; cd ..
	
%.o:%.c
	${CC} $(CPPFLAGS) $(CFLAGS) -std=c99 -c -o $@ $<

%.o:%.S
	${CC} $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

clean:
	make  clean -C lib
	rm -f *.bin *.elf *.dis *.o
	
