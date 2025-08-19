from enum import IntEnum

class CstStr(IntEnum):
    READ = 0
    WRITE = 1
    # states are sorted, updates can't be resevered
    # state changes for spoly: NONE -> EMPTY -> SPOLIED -> SORTED after reduce
    # state changes for initial poly: NONE -> INITIAL -> REORDERED -> SORTED
    # notice how the state changes for all polys end up in SORTED 
    # notice FINAL_REDUCED is the final state for all polys after reduction
    INITIAL = 0
    EMPTY = 1
    SPOLIED = 2
    REORDERED = 3
    ZERO = 4
    SORTED = 5
    FINAL_REDUCED = 6

    SORT = 100
    REORDER = 101
    SPOLY = 102
    REDUCE = 103
    PATH_GEN = 200
    SPOLY_GEN = 201
    SPOLY_GEN_GEN = 202
    