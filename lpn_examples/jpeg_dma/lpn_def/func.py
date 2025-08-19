from collections import deque
from lpnlang import Place, Transition, Token
from lpnlang import Place, Token, prop_value, get_token
from lpnlang import InWeightFunc, OutWeightFunc, DelayFunc, ThresholdFunc
from typing import List, Dict
from jpeg_dma.lpn_def.all_enum import CstStr

'not lpn function, so dont care'
def create_empty_tokens(num):
    tokens = deque()
    for i in range(num):
        token = Token()
        tokens.append(token)
    return tokens

take_max_16_tokens = InWeightFunc("take_max_16_tokens", from_place=Place)
@take_max_16_tokens.install
def weight(binding, from_place):
    num = prop_value(binding, from_place, None, "tk_len")
    if num == 0:
        return 1
    if num > 16:
        return 16
    else:
        return num
    
record_max_16 = OutWeightFunc("record_max_16", from_place=Place)
@record_max_16.install
def output_tokens(binding, output_place, from_place):
    num = prop_value(binding, from_place, None, "tk_len")
    if num > 16:
        num = 16
    output_place.push_token(Token({"num":num}))

put_recv_buf = OutWeightFunc("put_recv_buf", from_place=Place)
@put_recv_buf.install
def output_tokens(binding, output_place, from_place):
    num = prop_value(binding, from_place, 0, "num")
    # num of requests, each request is 32 bytes
    for i in range(num*32):
        output_place.push_token(Token())

con_edge = InWeightFunc("con_edge", number=int)
@con_edge.install
def weight(binding, number):
    return number

constant_func = DelayFunc("constant_func", scale=int)
@constant_func.install
def delay(binding, scale):
    return scale*CstStr.JPEG_SCALE_TO_NS

con_tokens = OutWeightFunc("con_tokens", number=int)
@con_tokens.install
def output_tokens(binding, output_place, number):
    for i in range(number):
        output_place.push_token(Token())

mcu_delay = DelayFunc("mcu_delay", from_place=Place)
@mcu_delay.install
def delay(binding, from_place):
    return (prop_value(binding, from_place, 0, "nonzero")*3+6)*CstStr.JPEG_SCALE_TO_NS

const_threshold = ThresholdFunc("const_threshold", number=int)
@const_threshold.install
def threshold(binding, number):
    return number

constant_66 = constant_func(66)
constant_0  = constant_func(0)
constant_67 = constant_func(67)
constant_65 = constant_func(65)
constant_68 = constant_func(68)

c0 = con_edge(0)
c1 = con_edge(1)
c2 = con_edge(2)
c4 = con_edge(4)
c64 = con_edge(64)
c32 = con_edge(32)
c16 = con_edge(16)
c256 = con_edge(256)

ct1 = con_tokens(1)
ct2 = con_tokens(2)
ct4 = con_tokens(4)

pass_type_idx_for_macroblock = OutWeightFunc("pass_type_idx_for_macroblock", map=Dict[int, int], type_enum=int)
@pass_type_idx_for_macroblock.install
def output_tokens(binding, output_place, map, type_enum):
    for i in range(128//4):
        output_place.push_token(Token({"idx": map[type_enum]}))

macroblock_write = OutWeightFunc("macroblock_write", id=int)
@macroblock_write.install
def output_tokens(binding, output_place, id):
    # RGB total 2x64bytes 
    # writing 4 bytes at a time
    for i in range(128//4):
        output_place.push_token(Token({"device": CstStr.CPU_DEVICE_ID, "req": 0, "cmpl": 4, "from": id}))


pass_token = OutWeightFunc("pass_token", from_place=Place, num=int)
@pass_token.install
def output(binding, output_place, from_place, num):
    # binded variables:
    # print(from_place.id, keys)
    for i in range(num):
        token = get_token(binding, from_place, i)
        output_place.push_token(token)


pass_all_tokens = OutWeightFunc("pass_all_tokens", from_place=Place)
@pass_all_tokens.install
def output_token(binding, output_place, from_place):
    num = prop_value(binding, from_place, None, "tk_len")
    for i in range(num):
        token = get_token(binding, from_place, i)
        output_place.push_token(token)

take_all = InWeightFunc("take_all", from_place=Place)
@take_all.install
def weight(binding, from_place):
    wgt = prop_value(binding, from_place, None, "tk_len")
    if wgt > 0:
        return wgt
    else:
        return 1
