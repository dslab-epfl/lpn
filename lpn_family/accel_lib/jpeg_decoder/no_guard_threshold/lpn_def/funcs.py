import uuid
from collections import deque
from lpnlang import Place, Token, prop_value, get_token
from lpnlang import InWeightFunc, OutWeightFunc, DelayFunc

'not lpn function, so dont care'
def create_empty_tokens(num):
    tokens = deque()
    for i in range(num):
        token = Token()
        tokens.append(token)
    return tokens

con_edge = InWeightFunc("con_edge", number=int)
@con_edge.install
def weight(binding, number):
    return number

constant_func = DelayFunc("constant_func", scale=int)
@constant_func.install
def delay(binding, scale):
    return scale

con_tokens = OutWeightFunc("con_tokens", number=int)
@con_tokens.install
def output_tokens(binding, output_place, number):
    for i in range(number):
        output_place.push_token(Token())

mcu_delay = DelayFunc("mcu_delay", from_place=Place)
@mcu_delay.install
def delay(binding, from_place):
    return prop_value(binding, from_place, 0, "nonzero")*3+6

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