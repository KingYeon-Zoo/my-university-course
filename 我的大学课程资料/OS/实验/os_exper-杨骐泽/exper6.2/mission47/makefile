CC = gcc
CFLAGS = -g -w -fsigned-char -pipe -I "$(OLD_GCC_INCLUDE)"

INC = $(wildcard ./*.h)
SRC = $(wildcard *.c)  
OBJS = $(patsubst %.c,%.o,$(notdir ${SRC})) 
ARTIFACT = artifact.done
TARGET = linuxapp.exe

ifneq (,$(wildcard $(VSCODE_ARTIFACT_DIR)))
	VSCODE_ARTIFACT_INFO = Good Job ! You are using the customized version of VSCode for Linux 0.11 !
else
	VSCODE_ARTIFACT_INFO = Fatal Error ! Please use the customized version of VSCode for Linux 0.11 or reinstall it !
endif

all:  gcc_version $(TARGET) $(ARTIFACT)
	@echo -
	@echo -------- Write $(TARGET) into floppyb.img --------
	FloppyEditor Floppyb.img /copy $(TARGET) /y
	@echo -
	@echo -------- Build Linux 0.11 app success! --------

$(ARTIFACT):
	@echo -
	@echo -------- Build artifacts --------
	@echo -
	@echo $(VSCODE_ARTIFACT_INFO)
	@echo -
	copy "$(VSCODE_ARTIFACT_DIR)\floppya.img" floppya.img
	copy "$(VSCODE_ARTIFACT_DIR)\floppyb.img" floppyb.img
	copy "$(VSCODE_ARTIFACT_DIR)\harddisk.img" harddisk.img
	copy "$(VSCODE_ARTIFACT_DIR)\VGABIOS-lgpl-latest" VGABIOS-lgpl-latest
	copy "$(VSCODE_ARTIFACT_DIR)\bochsrcdbg.bxrc" bochsrcdbg.bxrc
	copy "$(VSCODE_ARTIFACT_DIR)\bochsrc.bxrc" bochsrc.bxrc
	copy "$(VSCODE_ARTIFACT_DIR)\bochsdbg.exe" bochsdbg.exe
	copy "$(VSCODE_ARTIFACT_DIR)\bochs-official.exe" bochs-official.exe
	copy "$(VSCODE_ARTIFACT_DIR)\BIOS-bochs-latest" BIOS-bochs-latest
	@echo done > $(ARTIFACT)

${TARGET}: ${OBJS}
	@echo -
	@echo -------- Build executable file $@ --------
	$(CC) -o ${TARGET} $(OBJS)
    
%.o: %.c $(INC)
	@echo -------- Compile $< --------
	$(CC) $(CFLAGS) -c  "$(abspath $<)" -o $@

gcc_version:
	$(CC) -version

clean:
	del /Q *.o $(TARGET)
	@echo -
	@echo -------- Clean Linux 0.11 app success! --------
