# ==============================================================================
# Spacecraft Thermal OS (AST-OS) - Core Flight System (cFS) Application Build Rules
# File: Makefile
# Description: Standard standalone and dynamic compilation definitions.
# ==============================================================================

CC = gcc
CFLAGS = -Wall -Wextra -Werror -std=c99 -O3 -fPIC
INCLUDES = -I.

TARGET = astos_cfs_app
SRC = astos_app.c mpc_controller.c
OBJ = $(SRC:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) $(INCLUDES) -o $(TARGET) $(OBJ) -lm

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET)

.PHONY: all clean
