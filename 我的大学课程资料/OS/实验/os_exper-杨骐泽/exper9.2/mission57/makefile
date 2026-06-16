DIR_INC = .
DIR_SRC = .
DIR_OBJ = .
DIR_BIN = .

SRC = $(wildcard ${DIR_SRC}/*.c)  
OBJ = $(patsubst %.c,${DIR_OBJ}/%.o,$(notdir ${SRC})) 

TARGET = boundaryidentification.exe

BIN_TARGET = ${DIR_BIN}/${TARGET}

CC = gcc
CFLAGS = -g -w -std=c99 -fsigned-char -I${DIR_INC}

${BIN_TARGET}:${OBJ}
	@echo --- build executable file: $@
	$(CC) $(OBJ) -o $@
    
${DIR_OBJ}/%.o:${DIR_SRC}/%.c
	@echo --- build object file: $@
	$(CC) $(CFLAGS) -c  $< -o $@

clean:
	del /Q *.exe *.o
