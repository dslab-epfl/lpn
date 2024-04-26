#!/bin/bash

# Stop execution on any error
set -e
CUR_DIR=$(pwd)
# Environment setup
export LLVM_CONFIG="/usr/bin/llvm-config-11"
export CXX="/usr/bin/clang++-11"
export CC="/usr/bin/clang-11"

# Clone and build klee-uclibc
rm -drf KLEE
mkdir KLEE
git clone https://github.com/klee/klee-uclibc.git KLEE/klee-uclibc
cd KLEE/klee-uclibc
./configure --make-llvm-lib --with-cc=clang-11 --with-llvm-config=llvm-config-11
make -j$(nproc)
cd ..

# Clone the KLEE repository at the specific commit
git clone https://github.com/klee/klee.git klee
cd klee
git checkout 62680274c68ca6aa08c138d4c0fd12a09b73fe2a
pwd
git apply $CUR_DIR/patches/lpn_klee.patch
# Build libcxx
mkdir libcxx
LLVM_VERSION=11 BASE=$(pwd)/libcxx ENABLE_OPTIMIZED=1 DISABLE_ASSERTIONS=1 ENABLE_DEBUG=0 REQUIRES_RTTI=1 ./scripts/build/build.sh libcxx

# Create and move to the build directory
mkdir build
cd $CUR_DIR/KLEE/klee/build

# Configure KLEE
cmake \
    -DENABLE_SOLVER_Z3=ON \
    -DENABLE_POSIX_RUNTIME=ON \
    -DENABLE_KLEE_UCLIBC=ON \
    -DKLEE_UCLIBC_PATH=$CUR_DIR/KLEE/klee-uclibc \
    -DENABLE_UNIT_TESTS=OFF \
    -DENABLE_KLEE_LIBCXX=ON \
    -DKLEE_LIBCXX_DIR=$CUR_DIR/KLEE/klee/libcxx/libc++-install-110/ \
    -DKLEE_LIBCXX_INCLUDE_DIR=$CUR_DIR/KLEE/klee/libcxx/libc++-install-110/include/c++/v1/ \
    -DENABLE_KLEE_EH_CXX=ON  \
    -DKLEE_LIBCXXABI_SRC_DIR=$CUR_DIR/KLEE/klee/libcxx/llvm-110/libcxxabi/ \
    -DLLVM_CONFIG_BINARY=$LLVM_CONFIG \
    -DLLVMCC=$CC \
    -DLLVMCXX=$CXX \
    ..

# Build KLEE
make -j$(nproc)
make install
echo "KLEE setup completed."

