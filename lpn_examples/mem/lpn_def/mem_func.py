from lpnlang import Place, Transition, Token
from lpnlang import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from lpnlang import prop_value
from vta_with_dma.lpn_def.places import *
from vta_with_dma.lpn_def.all_enum import CstStr

pass_cl_token = OutWeightFunc("pass_cl_token", input_place=Place)
@pass_cl_token.install
def output(binding, output_place, input_place):
    addr = prop_value(binding, input_place, 0, "addr")
    size = prop_value(binding, input_place, 0, "len")
    rw = prop_value(binding, input_place, 0, "type")
    if(size == 0):
        num = 1
    else:
        num = size // 64
    for i in range(num):
        output_place.push_token(Token(
            {"addr": addr+i*64, "type": rw}))

pass_cl_cnt = OutWeightFunc("pass_cl_cnt", input_place=Place)
@pass_cl_cnt.install
def output(binding, output_place, input_place):
    size = prop_value(binding, input_place, 0, "len")
    if(size == 0):
        num = 1
    else:
        num = size // 64
    output_place.push_token(Token({"num":num}))
    
take_cl_cnt = InWeightFunc("take_cl_cnt", input_place=Place)
@take_cl_cnt.install
def input(binding, input_place):
    return prop_value(binding, input_place, 0, "num")

delay_num_cl = DelayFunc("delay_num_cl", input_place=Place)
@delay_num_cl.install
def delay(binding, input_place):
    return prop_value(binding, input_place, 0, "num")
