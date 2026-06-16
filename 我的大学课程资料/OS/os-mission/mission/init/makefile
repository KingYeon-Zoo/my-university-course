CC = gcc
LD = ld
CFLAGS = -g -pipe -O -Wall -nostdinc -fno-builtin -I../include

INCLUDES = $(wildcard ../include/*.h ../include/asm/*.h ../include/linux/*.h ../include/sys/*.h)
INC = $(wildcard ./*.h)

SRC = $(wildcard *.c)  
OBJS = $(patsubst %.c,%.o,$(notdir ${SRC})) 

TARGET = main.o

${TARGET}:
    
%.o: %.c $(INCLUDES) $(INC)
	@echo -
	@echo -------- Compile $< --------
	$(CC) $(CFLAGS) -c  "$(abspath $<)" -o $@

clean:
	del /Q *.o

