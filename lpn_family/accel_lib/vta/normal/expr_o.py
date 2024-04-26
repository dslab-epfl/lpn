import lpnlang 
from lpnlang import Place, Transition, Token
from lpnlang import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from lpnlang import prop_value, get_token
from .places import *

output_insn_read_cmd = OutWeightFunc("output_insn_read_cmd", from_place=Place)
@output_insn_read_cmd.install
def output_token(binding, output_place, from_place):
    total_insn = prop_value(binding, from_place, 0, "total_insn")
    # edge expression: 
    max_insn = 8
    ites = total_insn // max_insn
    remain = total_insn % max_insn

    for i in range(ites):
        output_place.push_token(Token({"insn_count":max_insn}))

    if remain > 0:
        output_place.push_token(Token({"insn_count":remain}))  

pass_var_token_readLen = OutWeightFunc("pass_var_token_readLen", from_place=Place, dependent_place=Place)
@pass_var_token_readLen.install
def output_token(binding, output_place,from_place,dependent_place):
    num = prop_value(binding, dependent_place, 0, "insn_count")
    # print(from_place.id, keys)
    for i in range(0, num):
        token = get_token(binding, from_place, i)
        output_place.push_token(token)

pass_token = OutWeightFunc("pass_token", from_place=Place, num=int)
@pass_token.install
def output_token(binding, output_place, from_place, num):
    # binded variables:
    for i in range(0, num):
        token = get_token(binding, from_place, i)
        output_place.push_token(token)

pass_empty_token = OutWeightFunc("pass_empty_token")
@pass_empty_token.install
def output_token(binding, output_place):
    output_place.push_token(Token())

output_dep_push_prev = OutWeightFunc("output_dep_push_prev",dependent_place=Place)
@output_dep_push_prev.install
def output_token(binding, output_place, dependent_place):
    direc = prop_value(binding, dependent_place, 0, "push_prev")
    if direc == 1:
        output_place.push_token(Token())


output_dep_push_next = OutWeightFunc("output_dep_push_next", dependent_place=Place)
@output_dep_push_next.install
def output_token(binding, output_place, dependent_place):
    direc = prop_value(binding, dependent_place, 0, "push_next")
    if direc == 1:
        output_place.push_token(Token())

# p = Place("p1")
# op = output_dep_push_prev(dependent_place=p)
# p.tokens.append(Token({"push_prev":1}))
# p2 = Place("outputp")
# binding = dict()
# binding["p1.0.push_prev"] = 1
# op(binding, p2)
# print(p2.tokens)