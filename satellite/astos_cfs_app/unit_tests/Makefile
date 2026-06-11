# ==============================================================================
# Spacecraft Thermal OS (AST-OS) - C Unit Tests Build Rules
# File: Makefile
# Description: Compiles C tests linking app logic with -DUNIT_TESTING.
# ==============================================================================

CC = gcc
CFLAGS = -Wall -Wextra -Werror -std=c99 -O2 -DUNIT_TESTING
INCLUDES = -I.. -I.

TARGET = test_astos_app
SRC = test_astos_app.c ../astos_app.c ../mpc_controller.c
OBJ = $(SRC:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) $(INCLUDES) -o $(TARGET) $(OBJ) -lm

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET)

.PHONY: all clean
