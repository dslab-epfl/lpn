from lpnlang import Place, Transition, Token, InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc, IntFunc
from lpnlang import prop_value
from .places import *
from .all_enum import CstStr

delay_t9 = DelayFunc("delay_t9", dependent_place=Place)
@delay_t9.install
def delay(binding, dependent_place):
    return 21+2*prop_value(binding, dependent_place, 0, "insn_count")

delay_store = DelayFunc("delay_store", dependent_place=Place)
@delay_store.install
def delay(binding, dependent_place):
    #simplified 
    xsize = prop_value(binding, dependent_place, 0, "xsize")
    ysize = prop_value(binding, dependent_place, 0, "ysize")
    return 27*(xsize/8)*ysize

con_delay = DelayFunc("con_delay", constant=int)
@con_delay.install
def delay(binding, constant):
    return constant

delay_load = DelayFunc("delay_load", dependent_place=Place)
@delay_load.install
def body(binding, dependent_place):
    #simplified 
    subopcode = prop_value(binding, dependent_place, 0, "subopcode")
    tstype = prop_value(binding, dependent_place, 0, "tstype")
    xsize = prop_value(binding, dependent_place, 0, "xsize")
    ysize = prop_value(binding, dependent_place, 0, "ysize")

    if subopcode == CstStr.SYNC:
        return 2;            
    if tstype == CstStr.INP:
        return 1+21+xsize*ysize*1*16*8/64
    if tstype == CstStr.WGT:
        return 1+21+xsize*ysize*16*16*8/64
    assert(0)

delay_gemm = IntFunc("delay_gemm", dependent_place=Place)
@delay_gemm.install
def body(binding, dependent_place):
    #simplified
    uop_begin = prop_value(binding, dependent_place, 0, "uop_begin")
    uop_end = prop_value(binding, dependent_place, 0, "uop_end")
    lp_0 = prop_value(binding, dependent_place, 0, "lp_0")
    lp_1 = prop_value(binding, dependent_place, 0, "lp_1")
    return 1+5+(uop_end-uop_begin)*lp_1*lp_0 

delay_loadUop = IntFunc("delay_loadUop", dependent_place=Place)
@delay_loadUop.install
def body(binding, dependent_place):
    xsize = prop_value(binding, dependent_place, 0, "xsize")
    ysize = prop_value(binding, dependent_place, 0, "ysize")
    #does this create trouble?
    return 1+21+xsize*(ysize+2-(ysize%2))/2    

delay_loadAcc = IntFunc("delay_loadAcc", dependent_place=Place)
@delay_loadAcc.install
def body(binding, dependent_place):
    xsize = prop_value(binding, dependent_place, 0, "xsize")
    ysize = prop_value(binding, dependent_place, 0, "ysize")
    return 1+21+xsize*8*ysize

delay_alu = IntFunc("delay_alu", dependent_place=Place)
@delay_alu.install
def body(binding, dependent_place):
    #simplified 
    uop_begin = prop_value(binding, dependent_place, 0, "uop_begin")
    uop_end = prop_value(binding, dependent_place, 0, "uop_end")
    lp_0 = prop_value(binding, dependent_place, 0, "lp_0")
    lp_1 = prop_value(binding, dependent_place, 0, "lp_1")
    use_alu_imm = prop_value(binding, dependent_place, 0, "use_alu_imm")
    return 1+5+(uop_end-uop_begin)*lp_1*lp_0*(2-use_alu_imm) 


delay_compute = DelayFunc("delay_compute", dependent_place=Place)
delay_compute.register_external_func([delay_alu, delay_gemm, delay_loadAcc, delay_loadUop])
@delay_compute.install
def delay(binding, dependent_place):
    subopcode = prop_value(binding, dependent_place, 0, "subopcode")
    if subopcode == CstStr.SYNC:
        return 1+1
    if subopcode == CstStr.ALU:
        return delay_alu(binding, dependent_place)
    if subopcode == CstStr.GEMM:
        return delay_gemm(binding, dependent_place)
    if subopcode == CstStr.LOADACC:
        return delay_loadAcc(binding, dependent_place)
    if subopcode == CstStr.LOADUOP:
        return delay_loadUop(binding, dependent_place)
    assert(0)

