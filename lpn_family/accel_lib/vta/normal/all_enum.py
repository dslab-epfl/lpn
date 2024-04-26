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
