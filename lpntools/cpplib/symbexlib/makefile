# Compiler to use
CC=clang++
# llvm-link for linking .bc files
LLVM_LINK=llvm-link
# KLEE command if you want to run it as part of the make process
KLEE=klee

INCLUDE = -I$(KLEE_PATH)/libcxx/llvm-110/libcxx/include 
CFLAGS= -v -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone
LDFLAGS=

SRC_DIR=.
OBJ_DIR=./obj

# Adjusted to find .cc files
SOURCES=$(wildcard $(SRC_DIR)/*.cc)
# Adjusted to generate .bc files instead of .o files
OBJECTS=$(patsubst $(SRC_DIR)/%.cc, $(OBJ_DIR)/%.bc, $(SOURCES))

# The final bitcode file for KLEE
TARGET=$(OBJ_DIR)/sim.bc

all: $(TARGET)

# Link the .bc files into one .bc file with llvm-link
$(TARGET): $(OBJECTS)
	$(LLVM_LINK) -o $(TARGET) $(OBJECTS)

# Compile .cc to .bc
$(OBJ_DIR)/%.bc: $(SRC_DIR)/%.cc
	mkdir -p $(OBJ_DIR)
	$(CC) -stdlib=libc++ -nostdinc++  $(INCLUDE) $(CFLAGS) $< -o $@

clean:
	rm -f $(OBJ_DIR)/*.bc

# Optional: Add a rule to run KLEE on the final bitcode file
klee: $(TARGET)
	$(KLEE) -use-merge -libc=uclibc --libcxx --external-calls=all $(TARGET)
