
import uuid
import math
from collections import deque
from lpnlang import Place, Transition, Token
from lpnlang import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from lpnlang import IntFunc, VoidFunc
from lpnlang import prop_value,get_token 
from typing import List, Dict
from pcie_topo.param_x8 import *
from pcie_topo.lpn_def.all_enum import CstStr

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

pass_empty_token = OutWeightFunc("pass_empty_token", num=int)
@pass_empty_token.install
def output_token(binding, output_place, num):
    for i in range(num):
        output_place.push_token(Token())

increase_credit_wc = OutWeightFunc("increase_credit_wc", send_buf=Place, unit=int)
@increase_credit_wc.install
def output(binding, output_place, send_buf, unit):
    num_credit = max(1, math.ceil(prop_value(binding, send_buf, 0, "pkt_size") / unit))
    for i in range(num_credit):
        output_place.push_token(Token())

increase_credit = OutWeightFunc("increase_credit", send_buf=Place, this_port=int, unit=int)
@increase_credit.install
def output(binding, output_place, send_buf, this_port, unit):
    if prop_value(binding, send_buf, 0, "port") == this_port:
        num_credit = max(1, math.ceil(prop_value(binding, send_buf, 0, "pkt_size") / unit))
        for i in range(num_credit):
            output_place.push_token(Token())


# pass_credit_token = OutWeightFunc("pass_credit_token", from_place=Place, unit=int)
# pass_credit_token.register_external_func([pass_empty_tokens])
# @pass_credit_token.install
# def output(binding, output_place, from_place, unit):
#     num_credit = max(1, math.ceil(prop_value(binding, from_place, 0, "pkt_size") / unit))
#     pass_empty_tokens(binding, output_place, num_credit)

pass_credit_with_header_token = OutWeightFunc("pass_credit_with_header_token", from_place=Place, header_bytes=int, unit=int)
@pass_credit_with_header_token.install
def output(binding, output_place, from_place, header_bytes, unit):
    num_credit = max(1, math.ceil((prop_value(binding, from_place, 0, "pkt_size")+header_bytes) / unit))
    # num_credit = min(num_credit, Credit)
    for i in range(num_credit):
        output_place.push_token(Token())
    

take_out_port = GuardFunc("take_out_port", from_place=Place, routinfo=Dict[int, int], this_port=int)
@take_out_port.install
def guard(binding, from_place, routinfo, this_port):
    dst = prop_value(binding, from_place, 0, "dst")
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


pass_atomic_smaller_token = OutWeightFunc("pass_atomic_smaller_token", tlp_size=int, from_place=Place)
@pass_atomic_smaller_token.install
def output_token(binding, output_place, tlp_size, from_place):

    num_atomic = math.ceil(prop_value(binding, from_place, 0, "pkt_size") / tlp_size)
    remain = prop_value(binding, from_place, 0, "pkt_size")
    offset = prop_value(binding, from_place, 0, "offset")
    dataref = prop_value(binding, from_place, 0, "dataref")
    src = prop_value(binding, from_place, 0, "src")
    dst = prop_value(binding, from_place, 0, "dst")
    type = prop_value(binding, from_place, 0, "type")
    for i in range(0, num_atomic):
        this_size = min(tlp_size, remain)    
        remain = remain - this_size
        token  = Token({ 
            "src": src,
            "dst": dst,
            "type": type,
            "pkt_size": this_size, 
            "offset": offset,
            "dataref": dataref
            })
        output_place.push_token(token)
        offset += this_size


take_1_token = InWeightFunc("take_1_token")
@take_1_token.install
def number_of_token(binding):
    return 1 

take_credit_token = InWeightFunc("take_credit_token", from_place=Place, unit=int)
@take_credit_token.install
def number_of_token(binding, from_place, unit):
    num_credit = max(1, math.ceil(prop_value(binding, from_place, 0, "pkt_size") / unit))
    return num_credit

take_some_token = InWeightFunc("take_some_token", num=int)
@take_some_token.install
def number_of_token(binding, num):
    return num

# store_readcomp_1byte = OutWeightFunc("store_readcomp_1byte", buf_place=Place)
# @store_readcomp_1byte.install
# def output(binding, output_place, buf_place):
#     is_req = prop_value(binding, buf_place, 0, "req")
#     num_cmpl = prop_value(binding, buf_place, 0, "pkt_size")
#     if is_req == 0:
#         for i in range(num_cmpl):
#             token  = Token({ 
#             "device": prop_value(binding, buf_place, 0, "device"),
#             "req" : prop_value(binding, buf_place, 0, "req"),
#             "pkt_size": 1, 
#             "from": prop_value(binding, buf_place, 0, "from")})
#             output_place.push_token(token)

store_cmpl = OutWeightFunc("store_cmpl", buf_place=Place)
@store_cmpl.install
def output(binding, output_place, buf_place):
    type = prop_value(binding, buf_place, 0, "type")
    if type == CstStr.CMPL:
        output_place.push_token(Token({
            "src": prop_value(binding, buf_place, 0, "src"),
            "dst": prop_value(binding, buf_place, 0, "dst"),
            "type": type,
            "pkt_size" : prop_value(binding, buf_place, 0, "pkt_size"),
            "offset": prop_value(binding, buf_place, 0, "offset"),
            "dataref": prop_value(binding, buf_place, 0, "dataref")})
        )

store_request = OutWeightFunc("store_request", buf_place=Place)
@store_request.install
def output(binding, output_place, buf_place):
    type = prop_value(binding, buf_place, 0, "type")
    if type == CstStr.READ or type == CstStr.WRITE:
        output_place.push_token(
            Token({
                "src": prop_value(binding, buf_place, 0, "src"),
                "dst": prop_value(binding, buf_place, 0, "dst"),
                "type": type,
                "pkt_size": prop_value(binding, buf_place, 0, "pkt_size"), 
                "offset": prop_value(binding, buf_place, 0, "offset"),
                "dataref": prop_value(binding, buf_place, 0, "dataref")
            }))

# store_request = OutWeightFunc("store_request", ori_device=int, buf_place=Place, mps=int)
# @store_request.install
# def output(binding, output_place, ori_device, buf_place, mps):
#     # already chunk up the requests such that each can be send back
#     type = prop_value(binding, buf_place, 0, "type")
#     if type == CstStr.READ or type == CstStr.WRITE:
#         req_from = prop_value(binding, buf_place, 0, "src")
#         offset = prop_value(binding, buf_place, 0, "offset")
#         dataref = prop_value(binding, buf_place, 0, "dataref")
#         if type == CstStr.READ:
#             req_size = prop_value(binding, buf_place, 0, "dataref")
#         else:
#             req_size = prop_value(binding, buf_place, 0, "pkt_size")
        
#         remain = req_size
#         transfer_count = math.ceil(req_size/mps)
#         for i in range(0, transfer_count):
#             this_size = min(mps, remain)    
#             remain = remain - this_size
#             output_place.push_token(
#                 Token({
#                     "dst": req_from,
#                     "src": 0, 
#                     "offset": offset,
#                     "dataref": dataref}))
#             offset = offset + this_size

empty_threshold = ThresholdFunc("empty_threshold")
@empty_threshold.install
def threshold(binding):
    return 0

# mem_delay = DelayFunc("mem_delay", from_place=Place, const_delay=int)
# @mem_delay.install
# def delay(binding, from_place, const_delay):
#     req_data = prop_value(binding, from_place, 0, "req")
#     if req_data > 0:
#         return 10
#     else:
#         cmpl_data = prop_value(binding, from_place, 0, "pkt_size")
#         return math.ceil(cmpl_data / 64) + const_delay

merge_delay = DelayFunc("merge_delay", from_place=Place)
@merge_delay.install
def delay(binding, from_place):
    pkt_size = prop_value(binding, from_place, 0, "pkt_size")
    return math.ceil(pkt_size/64)

var_tlp_process_delay = DelayFunc("var_tlp_process_delay", from_place=Place, base=int)
@var_tlp_process_delay.install
def delay(binding, from_place, base):
    pkt_size = prop_value(binding, from_place, 0, "pkt_size")
    # print("cmpl base ", cmpl, base) 
    # print(math.ceil(cmpl/16)*2+base)
    return math.ceil(pkt_size/16)*2+base

pass_rm_header_token = OutWeightFunc("pass_rm_header_token", from_place=Place, num=int, header_bytes=int)
@pass_rm_header_token.install
def output_token(binding, output_place, from_place, num, header_bytes):
    for i in range(num):
        token = Token({ 
            "src": prop_value(binding, from_place, i, "src"),
            "dst": prop_value(binding, from_place, i, "dst"),
            "type": prop_value(binding, from_place, i, "type"),
            "pkt_size": prop_value(binding, from_place, i, "pkt_size") - header_bytes,
            "offset": prop_value(binding, from_place, i, "offset"),
            "dataref": prop_value(binding, from_place, i, "dataref")
            })
        output_place.push_token(token)

pass_add_header_token = OutWeightFunc("pass_add_header_token", from_place=Place, num=int, header_bytes=int)
@pass_add_header_token.install
def output_token(binding, output_place, from_place, num, header_bytes):
    for i in range(num):
        token = Token({ 
            "src": prop_value(binding, from_place, i, "src"),
            "dst": prop_value(binding, from_place, i, "dst"),
            "type": prop_value(binding, from_place, i, "type"),
            "pkt_size": prop_value(binding, from_place, i, "pkt_size") + header_bytes,
            "offset": prop_value(binding, from_place, i, "offset"),
            "dataref": prop_value(binding, from_place, i, "dataref")
            })
        output_place.push_token(token)
    
mem_request_read = OutWeightFunc("mem_request_read", from_place=Place, mps=int, port=int)
@mem_request_read.install
def output(binding, output_place, from_place, mps, port):

    type = prop_value(binding, from_place, 0, "type")
    dataref = prop_value(binding, from_place, 0, "dataref")
    req_from = prop_value(binding, from_place, 0, "src")
    src = prop_value(binding, from_place, 0, "dst")
    dst = prop_value(binding, from_place, 0, "src")
    pkt_size = prop_value(binding, from_place, 0, "pkt_size")
    offset = prop_value(binding, from_place, 0, "offset")

    assert(type != CstStr.CMPL)
    if type == CstStr.READ:
        #     # already chunk up the requests such that each can be send back
        assert(offset == 0)
        req_size = dataref
        remain = req_size
        transfer_count = math.ceil(req_size/mps)
        for i in range(0, transfer_count):
            this_size = min(mps, remain)
            # assume dataref is the size
            id = Token({
                "src": src,
                "dst": dst,
                "type": CstStr.CMPL,
                "pkt_size": this_size,
                "offset": offset,
                "dataref": dataref
            })
            tk = Token({"id": id, "addr": offset, "size": this_size, "buffer": 0, "rw": 0, "ref": port})
            output_place.push_token(tk)
            offset = offset + this_size

mem_request_write = OutWeightFunc("mem_request_write", from_place=Place, mps=int, port=int)
@mem_request_write.install
def output(binding, output_place, from_place, mps, port):

    type = prop_value(binding, from_place, 0, "type")
    dataref = prop_value(binding, from_place, 0, "dataref")
    req_from = prop_value(binding, from_place, 0, "src")
    src = prop_value(binding, from_place, 0, "dst")
    dst = prop_value(binding, from_place, 0, "src")
    pkt_size = prop_value(binding, from_place, 0, "pkt_size")
    offset = prop_value(binding, from_place, 0, "offset")

    assert(type != CstStr.CMPL)
    if type == CstStr.WRITE:
        # because a write can be chunked, each write needs to response
        # the dataref contains the size of the write response
        # offset contains which parts are written
        dataref = pkt_size
        id = Token({
                "src": src,
                "dst": dst,
                "type": CstStr.CMPL,
                "pkt_size": 16,
                "offset": offset,
                "dataref": dataref
            })
        tk = Token({"id": id, "addr": 0, "size": 0, "buffer": 0, "rw": 1, "ref": port})
        output_place.push_token(tk)

send_cmpl = OutWeightFunc("send_cmpl", from_place=Place)
@send_cmpl.install
def output(binding, output_place, from_place):
    tk = prop_value(binding, from_place, 0, "id")
    output_place.push_token(tk)