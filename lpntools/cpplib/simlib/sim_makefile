# Compiler to use
CC=clang++
# Compiler flags, e.g., -g for debugging, -O2 for optimization
CFLAGS=-O3
# Linker flags, e.g., if you need to link libraries like -lm for math
LDFLAGS=
# Directory containing source files
SRC_DIR=.
# Directory to place object files
OBJ_DIR=./obj

# Automatically list all .cc files in SRC_DIR
SOURCES=$(wildcard $(SRC_DIR)/*.cc)
# Convert the .cc file list to a .o file list in OBJ_DIR
OBJECTS=$(patsubst $(SRC_DIR)/%.cc, $(OBJ_DIR)/%.o, $(SOURCES))

# The final executable
TARGET=lpnsim

# First target is the one executed when no targets are given.
all: $(TARGET)

# Link the target with all objects files
$(TARGET): $(OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $^

# Compile .cc to .o
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cc
	mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# 'make clean' command to remove all compiled files
clean:
	rm -f $(TARGET) $(OBJECTS)

