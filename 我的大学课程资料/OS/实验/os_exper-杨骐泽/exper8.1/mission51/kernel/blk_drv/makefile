AR = ar
CC = gcc
LD = ld
CFLAGS = -g -pipe -Wall -nostdinc -fno-builtin -I../../include
SFLAGS = -g -pipe

INCLUDES = $(wildcard ../../include/*.h ../../include/asm/*.h ../../include/linux/*.h ../../include/sys/*.h)
INC = $(wildcard ./*.h)

SRC = $(wildcard *.c)  
OBJS = $(patsubst %.c,%.o,$(notdir ${SRC})) 

TARGET = blk_drv.a

${TARGET}: ${OBJS}
	@echo -
	@echo -------- Build library file $@ --------
	$(AR) rcs $(TARGET) $(OBJS)
    
%.o: %.c $(INCLUDES) $(INC)
	@echo -
	@echo -------- Compile $< --------
	$(CC) $(CFLAGS) -c  "$(abspath $<)" -o $@

clean:
	del /Q *.o *.a

