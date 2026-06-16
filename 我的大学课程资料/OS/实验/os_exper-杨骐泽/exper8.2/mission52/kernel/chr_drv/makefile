AR = ar
CC = gcc
LD = ld
CFLAGS = -g -pipe -Wall -nostdinc -fno-builtin -I../../include
SFLAGS = -g -pipe

INCLUDES = $(wildcard ../../include/*.h ../../include/asm/*.h ../../include/linux/*.h ../../include/sys/*.h)
INC = $(wildcard ./*.h)

SRC = $(wildcard *.c)  
SRC_S = $(wildcard *.s)  
OBJS = $(patsubst %.c,%.o,$(notdir ${SRC})) 
OBJS_S = $(patsubst %.s,%.o,$(notdir ${SRC_S})) 

TARGET = chr_drv.a

${TARGET}: ${OBJS} ${OBJS_S}
	@echo -
	@echo -------- Build library file $@ --------
	$(AR) rcs $(TARGET) $(OBJS) $(OBJS_S)
    
%.o: %.c $(INCLUDES) $(INC)
	@echo -
	@echo -------- Compile $< --------
	$(CC) $(CFLAGS) -c  "$(abspath $<)" -o $@

%.o: %.s $(INCLUDES) $(INC)
	@echo -
	@echo -------- Compile $< --------
	$(CC) $(SFLAGS) -c  "$(abspath $<)" -o $@

clean:
	del /Q *.o *.a

