import math
from collections import deque
from lpnlang import Place, Transition, Token
from lpnlang import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from lpnlang import IntFunc, VoidFunc
from lpnlang import prop_value,get_token 
from typing import List, Dict
import numpy as np

read_list_of_mem_req = []
write_list_of_mem_req = []

delay_0_if_resp_ready = DelayFunc("delay_0_if_resp_ready", type=int)
@delay_0_if_resp_ready.install
def delay(binding, type):
    if type == 0:
        _list = read_list_of_mem_req
    else:
        _list = write_list_of_mem_req
    if len(_list) > 0:
        return 0
    else:
        return np.Inf
    return np.Inf

call_get_mem = OutWeightFunc("call_get_mem", type=int)
@call_get_mem.install
def output(binding, output_place, type):
    if type == 0:
        _list = read_list_of_mem_req
    else:
        _list = write_list_of_mem_req
    ref, id, addr, size, buffer, rw = _list[0]
    _list.pop(0)
    # print(f"call_get_mem: port {ref}, tag {id}")
    output_place.push_token(Token({"id": id, "addr": addr, "size": size, "buffer":buffer, "rw": rw, "ref": ref}))
    # output_place.push_token(Token({"id": 0, "addr": 0, "size": 0, "buffer":0, "rw": 0, "ref": 0}))

call_put_mem = OutWeightFunc("call_put_mem", from_place=Place, type=int)
@call_put_mem.install
def output(binding, output_place, from_place, type):
    ref = prop_value(binding, from_place, 0, "ref")
    id = prop_value(binding, from_place, 0, "id")
    addr = prop_value(binding, from_place, 0, "addr")
    size = prop_value(binding, from_place, 0, "size")
    buffer = prop_value(binding, from_place, 0, "buffer")
    rw = prop_value(binding, from_place, 0, "rw")
    if type == 0:
        _list = read_list_of_mem_req
    else:
        _list = write_list_of_mem_req
    print(f"call_put_mem: tag {id} port {ref}")
    _list.append((ref, id, addr, size, buffer, rw))

pass_token_match_port = OutWeightFunc("pass_token_match_port", from_place=Place, match_port=int)
@pass_token_match_port.install
def output(binding, output_place, from_place, match_port):
    ref = prop_value(binding, from_place, 0, "ref")
    token = get_token(binding, from_place, 0)
    if ref == match_port:
        output_place.push_token(token)

def create_empty_tokens(num):
    tokens = deque()
    for i in range(num):
        token = Token()
        token.t = 0
        tokens.append(token)
    return tokens

empty_guard = GuardFunc("empty_guard")
@empty_guard.install
def guard(binding):
    return True

pass_empty_tokens = VoidFunc("pass_empty_tokens", output_place=Place, num=int)
@pass_empty_tokens.install
def body(binding, output_place, num):
    for i in range(num):
        output_place.push_token(Token())

con_edge = InWeightFunc("con_edge", number=int)
@con_edge.install
def weight(binding, number):
    return number

con_delay = DelayFunc("con_delay", scale=int)
@con_delay.install
def delay(binding, scale):
    return scale

con_delay_ns = DelayFunc("con_delay_ns", scale=int)
@con_delay_ns.install
def delay(binding, scale):
    return scale

pass_empty_token = OutWeightFunc("pass_empty_token")
@pass_empty_token.install
def output_token(binding, output_place):
    output_place.push_token(Token())

increase_credit_wc = OutWeightFunc("increase_credit_wc", send_buf=Place, unit=int)
@increase_credit_wc.install
def output(binding, output_place, send_buf, unit):
    num_credit = max(1, math.ceil(prop_value(binding, send_buf, 0, "cmpl") / unit))
    for i in range(num_credit):
        output_place.push_token(Token())

increase_credit = OutWeightFunc("increase_credit", send_buf=Place, this_port=int, unit=int)
@increase_credit.install
def output(binding, output_place, send_buf, this_port, unit):
    if prop_value(binding, send_buf, 0, "port") == this_port:
        num_credit = max(1, math.ceil(prop_value(binding, send_buf, 0, "cmpl") / unit))
        for i in range(num_credit):
            output_place.push_token(Token())


# pass_credit_token = OutWeightFunc("pass_credit_token", from_place=Place, unit=int)
# pass_credit_token.register_external_func([pass_empty_tokens])
# @pass_credit_token.install
# def output(binding, output_place, from_place, unit):
#     num_credit = max(1, math.ceil(prop_value(binding, from_place, 0, "cmpl") / unit))
#     pass_empty_tokens(binding, output_place, num_credit)

pass_credit_with_header_token = OutWeightFunc("pass_credit_with_header_token", from_place=Place, header_bytes=int, unit=int)
@pass_credit_with_header_token.install
def output(binding, output_place, from_place, header_bytes, unit):
    num_credit = max(1, math.ceil((prop_value(binding, from_place, 0, "cmpl")+header_bytes) / unit))
    # num_credit = min(num_credit, Credit)
    for i in range(num_credit):
        output_place.push_token(Token())
    

take_out_port = GuardFunc("take_out_port", from_place=Place, routinfo=Dict[int, int], this_port=int)
@take_out_port.install
def guard(binding, from_place, routinfo, this_port):
    dst = prop_value(binding, from_place, 0, "device")
    out_port = routinfo[dst]
    if out_port == this_port:
        return True
    else:
        return False


pass_token = OutWeightFunc("pass_token", from_place=Place, num=int)
@pass_token.install
def output(binding, output_place, from_place, num):
    # binded variables:
    # print(from_place.id, keys)
    for i in range(num):
        token = get_token(binding, from_place, i)
        output_place.push_token(token)


take_1_token = InWeightFunc("take_1_token")
@take_1_token.install
def number_of_token(binding):
    return 1 


take_some_token = InWeightFunc("take_some_token", num=int)
@take_some_token.install
def number_of_token(binding, num):
    return num
            
store_request = OutWeightFunc("store_request", ori_device=int, buf_place=Place, mps=int)
@store_request.install
def output(binding, output_place, ori_device, buf_place, mps):
    req_data = prop_value(binding, buf_place, 0, "req")
    if req_data != 0:
        remain = req_data
        req_from = prop_value(binding, buf_place, 0, "from")
        transfer_count = math.ceil(req_data/mps)
        for i in range(0, transfer_count):
            this_size = min(mps, remain)    
            remain = remain - this_size
            output_place.push_token(
                Token({
                    "device": req_from, 
                    "req":0, 
                    "cmpl": this_size, 
                    "from": ori_device}))

empty_threshold = ThresholdFunc("empty_threshold")
@empty_threshold.install
def threshold(binding):
    return 0

mem_delay = DelayFunc("mem_delay", from_place=Place, const_delay=int)
@mem_delay.install
def delay(binding, from_place, const_delay):
    req_data = prop_value(binding, from_place, 0, "req")
    if req_data > 0:
        return 10
    else:
        cmpl_data = prop_value(binding, from_place, 0, "cmpl")
        return math.ceil(cmpl_data / 64) + const_delay

