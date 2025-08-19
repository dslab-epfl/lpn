from enum import IntEnum

class CstStr(IntEnum):
    INP = 0
    LOADUOP = 1
    GEMM = 2
    SYNC = 3
    WGT = 4
    LOADACC = 5
    ALU = 6
    COMPUTE = 7
    FINISH = 8
    EMPTY = 9
    STORE = 10
    LOAD = 11
    DMA_LOAD_INP = 12
    DMA_LOAD_WGT = 13
    DMA_STORE = 14
    DMA_LOAD_ACC = 15
    DMA_LOAD_UOP = 16
    DMA_LOAD_INSN = 17
