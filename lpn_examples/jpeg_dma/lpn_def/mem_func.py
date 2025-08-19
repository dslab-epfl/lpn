from lpnlang import Place, Transition, Token
from lpnlang import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from lpnlang import prop_value
from jpeg_dma.lpn_def.all_enum import CstStr


take_resp_token_write = InWeightFunc("take_resp_token_write", num=int)
@take_resp_token_write.install
def input(binding, num):
    return num

push_request_order_write = OutWeightFunc("push_request_order_write", port=int, num=int)
@push_request_order_write.install
def output(binding, output_place, port, num):
    for i in range(num):
        output_place.push_token(Token({"idx": port}))

mem_request_write = OutWeightFunc("mem_request_write", port=int, id=int, num=int)
@mem_request_write.install
def output(binding, output_place, port, id, num):
    for i in range(num):
        tk = Token({"id": id, "addr": 0, "size": 0, "buffer": 0, "rw": 1, "ref": port})
        output_place.push_token(tk)


mem_request = OutWeightFunc("mem_request", port=int, id=int, from_place=Place)
@mem_request.install
def output(binding, output_place, port, id, from_place=Place):
    num = prop_value(binding, from_place, None, "tk_len")
    if num > 16:
        num = 16
    for i in range(num):
        tk = Token({"id": id, "addr": 0, "size": 0, "buffer": 0, "rw": 0, "ref": port})
        output_place.push_token(tk)

push_request_order = OutWeightFunc("push_request_order", port=int, from_place=Place)
@push_request_order.install
def output(binding, output_place, port, from_place):
    num = prop_value(binding, from_place, None, "tk_len")
    if num > 16:
        num = 16
    for i in range(num):
        output_place.push_token(Token({"idx": port}))

take_resp_token = InWeightFunc("take_resp_token", from_place=Place)
@take_resp_token.install
def input(binding, from_place):
    num = prop_value(binding, from_place, 0, "num")
    return num
