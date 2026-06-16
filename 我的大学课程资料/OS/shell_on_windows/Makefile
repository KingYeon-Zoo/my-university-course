# Makefile for Unix/Linux Shell Interpreter
# Compiles kernel code to static library (.lib) and demo code to executable (.exe)

# Compiler settings
CC = gcc
AR = ar
CFLAGS = -Wall -Wextra -std=c99 -g -O0 -Ikernel/include
LDFLAGS = -static -g

# Directories
KERNEL_DIR = kernel
DEMO_DIR = demo
BUILD_DIR = build
LIB_DIR = lib

# Kernel source files
KERNEL_SRCS = $(KERNEL_DIR)/memory_pool.c \
              $(KERNEL_DIR)/utils.c \
              $(KERNEL_DIR)/variable.c \
              $(KERNEL_DIR)/ast.c \
              $(KERNEL_DIR)/lexer.c \
              $(KERNEL_DIR)/parser.c \
              $(KERNEL_DIR)/builtin_cmd.c \
              $(KERNEL_DIR)/cmd_mapping.c \
              $(KERNEL_DIR)/io_redirect.c \
              $(KERNEL_DIR)/executor.c \
              $(KERNEL_DIR)/shell_core.c

# Demo source files
DEMO_SRCS = $(DEMO_DIR)/main.c \
            $(DEMO_DIR)/interactive.c \
            $(DEMO_DIR)/script_runner.c \
            $(DEMO_DIR)/debug_ui.c

# Object files
KERNEL_OBJS = $(KERNEL_SRCS:$(KERNEL_DIR)/%.c=$(BUILD_DIR)/kernel_%.o)
DEMO_OBJS = $(DEMO_SRCS:$(DEMO_DIR)/%.c=$(BUILD_DIR)/demo_%.o)

# Output files
KERNEL_LIB = $(LIB_DIR)/shell_kernel.lib
DEMO_EXE = shell_demo.exe

# Default target
all: directories $(KERNEL_LIB) $(DEMO_EXE)

# Create directories
directories:
	@if not exist $(BUILD_DIR) mkdir $(BUILD_DIR)
	@if not exist $(LIB_DIR) mkdir $(LIB_DIR)

# Compile kernel object files
$(BUILD_DIR)/kernel_%.o: $(KERNEL_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# Compile demo object files
$(BUILD_DIR)/demo_%.o: $(DEMO_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# Build kernel library
$(KERNEL_LIB): $(KERNEL_OBJS)
	$(AR) rcs $@ $(KERNEL_OBJS)

# Build demo executable
$(DEMO_EXE): $(DEMO_OBJS) $(KERNEL_LIB)
	$(CC) $(DEMO_OBJS) $(KERNEL_LIB) -o $@ $(LDFLAGS)

# Clean build artifacts
clean:
	@if exist $(BUILD_DIR) rmdir /s /q $(BUILD_DIR)
	@if exist $(LIB_DIR) rmdir /s /q $(LIB_DIR)
	@if exist $(DEMO_EXE) del $(DEMO_EXE)

.PHONY: all directories clean

