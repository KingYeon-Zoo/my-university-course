# Makefile for Key-LED System
# Compatible with C89 standard

CC      = arm-linux-gcc
LD      = arm-linux-ld
AR      = arm-linux-ar
OBJCOPY = arm-linux-objcopy
OBJDUMP = arm-linux-objdump

# 编译标志：使用C89标准，禁用内建函数
CFLAGS  = -Wall -Os -fno-builtin -std=c89 -pedantic
CPPFLAGS = -nostdinc

# 目标文件
TARGET = key_led_system
BINARY = $(TARGET).bin
ELF    = $(TARGET).elf
DIS    = $(TARGET).dis

# 源文件
SOURCES = key_led_system.c key_handler.c led_controller.c libfuncs.c
OBJECTS = $(SOURCES:.c=.o) start.o

# 链接脚本（用户可能需要根据实际情况调整）
LDSCRIPT = system.lds

# 默认目标
all: $(BINARY)

# 生成二进制文件
$(BINARY): $(ELF)
	$(OBJCOPY) -O binary -S $< $@
	$(OBJDUMP) -D $< > $(DIS)
	@echo "Build completed: $(BINARY)"

# 链接生成ELF文件
$(ELF): $(OBJECTS)
	$(LD) -T$(LDSCRIPT) -o $@ $^

# 编译C文件
%.o: %.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

# 编译汇编文件
%.o: %.S
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

# 清理
clean:
	rm -f *.o *.elf *.bin *.dis

# 重新编译
rebuild: clean all

# 显示帮助信息
help:
	@echo "Available targets:"
	@echo "  all      - Build the complete system (default)"
	@echo "  clean    - Remove all generated files"
	@echo "  rebuild  - Clean and build"
	@echo "  help     - Show this help message"
	@echo ""
	@echo "Generated files:"
	@echo "  $(BINARY) - Final binary file for flashing"
	@echo "  $(ELF)    - ELF file with debug information"
	@echo "  $(DIS)    - Disassembly listing"

# 代码检查（可选）
check:
	@echo "Checking C89 compliance..."
	$(CC) $(CFLAGS) -fsyntax-only $(SOURCES)
	@echo "Syntax check passed"

# 显示文件大小信息
size: $(ELF)
	@echo "File size information:"
	@ls -lh $(BINARY) $(ELF)
	@arm-linux-size $(ELF)

.PHONY: all clean rebuild help check size 