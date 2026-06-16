LD = ld
LDFLAGS	= -nostdlib -Wl,-e,"startup_11" -Wl,--image-base,0x0000 -Wl,-Ttext,"0"

CC = gcc
CFLAGS = -g -pipe -Wall -nostdinc -fno-builtin -I./include
SFLAGS = -g -pipe

NASM = nasm
NFLAGS = -f bin

INCLUDES = $(wildcard ./include/*.h ./include/asm/*.h ./include/linux/*.h ./include/sys/*.h)

KERNEL_ARCHIVE = kernel/kernel.o
MM_ARCHIVE = mm/mm.o
FS_ARCHIVE = fs/fs.o
BLK_DRIVER = kernel/blk_drv/blk_drv.a
CHR_DRIVER = kernel/chr_drv/chr_drv.a
MATH = kernel/math/math.a
LIBS = lib/lib.a
MAIN = init/main.o
HEAD = boot\head.o
HEAD_LIST = boot\head.lst

BOOT = boot\bootsect.bin
BOOT_LIST = boot\bootsect.lst
LOADER = boot\setup.bin
LOADER_LIST = boot\setup.lst

TARGET = linux011.exe
KERNEL = linux011.bin
ARTIFACT = artifact.done

ifneq (,$(wildcard $(VSCODE_ARTIFACT_DIR)))
	VSCODE_ARTIFACT_INFO = Good Job ! You are using the customized version of VSCode for Linux 0.11 !
else
	VSCODE_ARTIFACT_INFO = Fatal Error ! Please use the customized version of VSCode for Linux 0.11 or reinstall it !
endif

all: $(TARGET) $(BOOT) $(LOADER) $(ARTIFACT)
	@echo -
	@echo -------- Build $(KERNEL) --------
	copy $(TARGET) $(TARGET).tmp
	strip $(TARGET).tmp
	pe2bin.exe $(TARGET).tmp $(KERNEL)
	del $(TARGET).tmp
	@echo -
	@echo -------- Build floppya.img --------
	mkfloppy.exe $(BOOT) $(LOADER) $(KERNEL) floppya.img
	@echo -
	@echo -------- Build Linux 0.11 success! --------

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
	copy "$(VSCODE_ARTIFACT_DIR)\bochs.exe" bochs.exe
	copy "$(VSCODE_ARTIFACT_DIR)\bochs-official.exe" bochs-official.exe
	copy "$(VSCODE_ARTIFACT_DIR)\BIOS-bochs-latest" BIOS-bochs-latest
	@echo done > $(ARTIFACT)


$(TARGET):	$(HEAD) $(MAIN) $(KERNEL_ARCHIVE) $(MM_ARCHIVE) $(FS_ARCHIVE) \
			$(BLK_DRIVER) $(CHR_DRIVER) $(MATH) $(LIBS)
	@echo -
	@echo -------- Link --------
	$(CC) $(LDFLAGS) \
	$(HEAD) \
	$(MAIN) \
	$(KERNEL_ARCHIVE) \
	$(MM_ARCHIVE) \
	$(FS_ARCHIVE) \
	$(BLK_DRIVER) \
	$(CHR_DRIVER) \
	$(MATH) \
	$(LIBS) \
	-o $(TARGET)

$(BOOT): boot/bootsect.asm
	@echo -
	@echo -------- Compile boot/bootsect.asm --------
	$(NASM) $(NFLAGS) -l boot/bootsect.lst -o $(BOOT) boot/bootsect.asm

$(LOADER): boot/setup.asm
	@echo -
	@echo -------- Compile boot/setup.asm --------
	$(NASM) $(NFLAGS) -l boot/setup.lst -o $(LOADER) boot/setup.asm

$(HEAD): boot/head.s
	@echo -
	@echo -------- Compile boot/head.s --------
	$(CC) $(SFLAGS) -c boot/head.s -o $(HEAD) -Wa,"-al=boot/head.lst"

$(MAIN): $(INCLUDES) $(wildcard ./init/*.c) $(wildcard ./init/*.h) $(wildcard ./init/*.s)
	(cd init && make)

$(MATH): $(INCLUDES) $(wildcard ./kernel/math/*.c) $(wildcard ./kernel/math/*.h) $(wildcard ./kernel/math/*.s)
	(cd kernel/math && make)

$(BLK_DRIVER): $(INCLUDES) $(wildcard ./kernel/blk_drv/*.c) $(wildcard ./kernel/blk_drv/*.h) $(wildcard ./kernel/blk_drv/*.s)
	(cd kernel/blk_drv && make)

$(CHR_DRIVER): $(INCLUDES) $(wildcard ./kernel/chr_drv/*.c) $(wildcard ./kernel/chr_drv/*.h) $(wildcard ./kernel/chr_drv/*.s)
	(cd kernel/chr_drv && make)

$(KERNEL_ARCHIVE): $(INCLUDES) $(wildcard ./kernel/*.c) $(wildcard ./kernel/*.h) $(wildcard ./kernel/*.s)
	(cd kernel && make)

$(MM_ARCHIVE): $(INCLUDES) $(wildcard ./mm/*.c) $(wildcard ./mm/*.h) $(wildcard ./mm/*.s)
	(cd mm && make)

$(FS_ARCHIVE): $(INCLUDES) $(wildcard ./fs/*.c) $(wildcard ./fs/*.h) $(wildcard ./fs/*.s)
	(cd fs && make)

$(LIBS): $(INCLUDES) $(wildcard ./lib/*.c) $(wildcard ./lib/*.h) $(wildcard ./lib/*.s)
	(cd lib && make)

clean:
	del /Q $(TARGET) $(KERNEL) $(HEAD) $(HEAD_LIST) $(BOOT) \
			$(BOOT_LIST) $(LOADER) $(LOADER_LIST)
	(cd fs && make clean)
	(cd init && make clean)
	(cd kernel && make clean)
	(cd lib && make clean)
	(cd mm && make clean)
	@echo -
	@echo -------- Clean Linux 0.11 success! --------
