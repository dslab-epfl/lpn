from collections import deque
from lpnlang import Place, Token
from lpnlang import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from lpnlang import IntFunc, VoidFunc
from lpnlang import prop_value, lpn_int, get_token

from protoacc_with_dma.lpn_def.places import *
from protoacc_with_dma.lpn_def.funcs.lpn_enum import CstStr

import numpy as np

pass_bytes_token = OutWeightFunc("pass_bytes_token", from_place=Place)
@pass_bytes_token.install
def output_token(binding, output_place, from_place):
    bytes = prop_value(binding, from_place, 0, "bytes")
    num = lpn_int(bytes / 16)
    output_place.push_token(Token({"num": num}))

take_all_tokens = InWeightFunc("take_all_tokens", from_place=Place)
@take_all_tokens.install
def number_of_token(binding, from_place):
    return prop_value(binding, from_place, 0, "num")

anonymous_func_1_pass_token = OutWeightFunc("anonymous_func_1_pass_token", from_place=Place)
@anonymous_func_1_pass_token.install
def output_token(binding, output_place, from_place):
    control_range = prop_value(binding, from_place, 0, "control_range")
    output_place.push_token(Token({"num": control_range}))

pass_16_bytes_outputQ_token = OutWeightFunc("pass_16_bytes_outputQ_token", from_place=Place)
@pass_16_bytes_outputQ_token.install
def output_token(binding, output_place, from_place):
    bytes = prop_value(binding, from_place, 0, "bytes")
    num = lpn_int(bytes / 16)
    for i in range(num):
        output_place.push_token(Token({
            "bytes": 16, 
            "end_of_field": 0, 
            "end_of_top_level": 0}))

mem_request_cond_v1 = OutWeightFunc("mem_request_cond_v1", port=int, from_place=Place)
@mem_request_cond_v1.install
def output(binding, output_place, port, from_place):
    type = prop_value(binding, from_place, 0, "type")
    if type == CstStr.SUBMESSAGE:
        return
    num = prop_value(binding, from_place, 0, "control_range")
    for i in range(num):
        output_place.push_token(Token({"idx": port}))

push_request_order_cond_v1 = OutWeightFunc("push_request_order_cond_v1", port=int, from_place=Place)
@push_request_order_cond_v1.install
def output(binding, output_place, port, from_place):
    type = prop_value(binding, from_place, 0, "type")
    if type == CstStr.SUBMESSAGE:
        return
    num = prop_value(binding, from_place, 0, "control_range")
    for i in range(num):
        output_place.push_token(Token({"idx": port}))

push_request_order = OutWeightFunc("push_request_order", port=int, num=int)
@push_request_order.install
def output(binding, output_place, port, num):
    for i in range(num):
        output_place.push_token(Token({"idx": port}))

push_request_order_v3 = OutWeightFunc("push_request_order_v3", port=int, from_place=Place)
@push_request_order_v3.install
def output(binding, output_place, port, from_place):
    num = prop_value(binding, from_place, 0, "control_range")
    for i in range(num):
        output_place.push_token(Token({"idx": port}))

mem_request_v3 = OutWeightFunc("mem_request_v3", port=int, id=int, from_place=Place)
@mem_request_v3.install
def output(binding, output_place, port, id, from_place):
    num = prop_value(binding, from_place, 0, "control_range")
    print(f"control range: {num}")
    for i in range(num):
        tk = Token({"id": id, "addr": 0, "size": 0, "buffer": 0, "rw": 0, "ref": port})
        output_place.push_token(tk)

push_write_request_order_v4 = OutWeightFunc("push_write_request_order_v4", port=int, from_place=Place)
@push_write_request_order_v4.install
def output(binding, output_place, port, from_place):
    bytes = prop_value(binding, from_place, 0, "bytes")
    num = lpn_int(bytes / 16)
    if bytes % 16 > 0:
        num += 1
    for i in range(num):
        output_place.push_token(Token({"idx": port}))

mem_request_write_v4 = OutWeightFunc("mem_request_write_v4", port=int, id=int, from_place=Place)
@mem_request_write_v4.install
def output(binding, output_place, port, id, from_place):
    bytes = prop_value(binding, from_place, 0, "bytes")
    num = lpn_int(bytes / 16)
    if bytes % 16 > 0:
        num += 1
    for i in range(num):
        tk = Token({"id": id, "addr": 0, "size": 16, "buffer": 0, "rw": 1, "ref": port})
        output_place.push_token(tk)

push_request_order_v2 = OutWeightFunc("push_request_order_v2", port=int, from_place=Place)
@push_request_order_v2.install
def output(binding, output_place, port, from_place):
    bytes = prop_value(binding, from_place, 0, "bytes")
    num = lpn_int(bytes / 16)
    for i in range(num):
        output_place.push_token(Token({"idx": port}))

mem_request_v2 = OutWeightFunc("mem_request_v2", port=int, id=int, from_place=Place)
@mem_request_v2.install
def output(binding, output_place, port, id, from_place):
    bytes = prop_value(binding, from_place, 0, "bytes")
    num = lpn_int(bytes / 16)
    for i in range(num):
        tk = Token({"id": id, "addr": 0, "size": 0, "buffer": 0, "rw": 0, "ref": port})
        output_place.push_token(tk)

mem_request = OutWeightFunc("mem_request", port=int, id=int, num=int)
@mem_request.install
def output(binding, output_place, port, id, num):
    for i in range(num):
        tk = Token({"id": id, "addr": 0, "size": 0, "buffer": 0, "rw": 0, "ref": port})
        output_place.push_token(tk)

delay_0_if_resp_ready = DelayFunc("delay_0_if_resp_ready", type=int)
@delay_0_if_resp_ready.install
def delay(binding, type, port):
    # if type == 0:
    #     _list = read_list_of_mem_req
    # else:
    #     _list = write_list_of_mem_req
    # if len(_list) > 0:
    #     return 0
    # else:
    return np.Inf

mem_read_delay = DelayFunc("mem_read_delay")
@mem_read_delay.install
def delay(binding):
    return 10

con_delay = DelayFunc("con_delay", scale=int)
@con_delay.install
def delay(binding, scale):
    return scale

pass_empty_token = OutWeightFunc("pass_empty_token", num=int)
@pass_empty_token.install
def output_token(binding, output_place, num):
    for i in range(num):
        output_place.push_token(Token())


pass_field_token = OutWeightFunc("pass_field_token", num_place=Place, from_place=Place)
@pass_field_token.install
def output_token(binding, output_place, num_place, from_place):
    num = prop_value(binding, num_place, 0, "num")
    for i in range(num):
        tk = get_token(binding, from_place, i)
        output_place.push_token(tk)


pass_num_field_token = OutWeightFunc("pass_num_field_token", num_place=Place)
@pass_num_field_token.install
def output_token(binding, output_place, num_place):
    num = prop_value(binding, num_place, 0, "num")
    output_place.push_token(Token({"num": num}))

pass_fields_meta_token = OutWeightFunc("pass_fields_meta_token", num_place=Place, from_place=Place)
@pass_fields_meta_token.install
def output_token(binding, output_place, num_place, from_place):
    # binded variables:
    num = prop_value(binding, num_place, 0, "control_range")
    for i in range(num):
        tk = get_token(binding, from_place, i)
        output_place.push_token(tk)

take_num_field_tokens = InWeightFunc("take_num_field_tokens", num_place=Place)
@take_num_field_tokens.install
def number_of_token(binding, num_place):
    return prop_value(binding, num_place, 0, "num")


take_num_field_as_control = InWeightFunc("take_num_field_as_control", num_place=Place)
@take_num_field_as_control.install
def number_of_token(binding, num_place):
    return prop_value(binding, num_place, 0, "control_range")


take_resume_token = InWeightFunc("take_resume_token", num_place=Place)
@take_resume_token.install
def number_of_token(binding, num_place):
    return prop_value(binding, num_place, 0, "num")

pass_scalar_outputQ_token = OutWeightFunc("pass_scalar_outputQ_token", from_place=Place)
@pass_scalar_outputQ_token.install
def output_token(binding, output_place, from_place):
    token = Token({
        "bytes": prop_value(binding, from_place, 0, "bytes"), 
        "end_of_field": 0, 
        'end_of_top_level': 0})
    output_place.push_token(token)


pass_field_end_token = OutWeightFunc("pass_field_end_token")
@pass_field_end_token.install
def output_token(binding, output_place):
    output_place.push_token(Token({
        "bytes": 0, 
        "end_of_field": 1, 
        'end_of_top_level': 0}))

pass_key_outputQ_end_of_toplevel_token = OutWeightFunc("pass_key_outputQ_end_of_toplevel_token", from_place=Place)
@pass_key_outputQ_end_of_toplevel_token.install
def output_token(binding, output_place, from_place):
    # write key
    output_place.push_token(Token({
        "bytes": 1, 
        "end_of_field": 0,
        'end_of_top_level': 0}))

    if prop_value(binding, from_place, 0, "type") == CstStr.END_OF_MESSAGE_TOP_LEVEL:
        # pass end of toplevel info
        output_place.push_token(Token({
            "bytes": 1, 
            "end_of_field": 0, 
            "end_of_top_level": 1}))
    else:
        assert(prop_value(binding, from_place, 0, "type") == CstStr.END_OF_MESSAGE)

pass_key_outputQ_token = OutWeightFunc("pass_key_outputQ_token")
@pass_key_outputQ_token.install
def output_token(binding, output_place):
    output_place.push_token(Token({
        "bytes": 1, 
        "end_of_field": 0, 
        "end_of_top_level": 0}))


field_end_cond_delay = DelayFunc("field_end_cond_delay", from_place=Place)
@field_end_cond_delay.install
def delay(binding, from_place):
    end_of_field = prop_value(binding, from_place, 0, "end_of_field")
    end_of_top_level = prop_value(binding, from_place, 0, "end_of_top_level")
    if end_of_field == 0 and end_of_top_level == 0:
        return 1
    else:
        return 0


pass_non_field_end_token = OutWeightFunc("pass_non_field_end_token", from_place=Place, num=int)
@pass_non_field_end_token.install
def output_token(binding, output_place, from_place, num):
    end_of_field = prop_value(binding, from_place, 0, "end_of_field")
    if end_of_field == 0:
        for i in range(num):
            token = get_token(binding, from_place, i)
            output_place.push_token(token)

write_out_delay = DelayFunc("write_out_delay", from_place=Place)
@write_out_delay.install
def delay(binding, from_place):
    bytes = prop_value(binding, from_place, 0, "bytes")
    mem_delay = 1
    'this will cause smt to fail if not uisng lpn_int,  because its not int anymore'
    d = lpn_int(bytes / 16) + mem_delay
    return d

all_bytes_delay = DelayFunc("all_bytes_delay", from_place=Place)
@all_bytes_delay.install
def delay(binding, from_place):
    bytes = prop_value(binding, from_place, 0, "bytes")
    return 10
    # return lpn_int(bytes / 16) + 10



pass_all_bytes_outputQ_token = OutWeightFunc("pass_all_bytes_outputQ_token", from_place=Place)
@pass_all_bytes_outputQ_token.install
def output_token(binding, output_place, from_place):
    bytes = prop_value(binding, from_place, 0, "bytes")
    output_place.push_token(Token({
        "bytes": bytes, 
        "end_of_field": 0, 
        "end_of_top_level": 0}))

pass_bytes_in_token = OutWeightFunc("pass_bytes_in_token", from_place=Place)
@pass_bytes_in_token.install
def number_of_token(binding, output_place, from_place):
    end_of_field = prop_value(binding, from_place, 0, "end_of_field")
    if end_of_field == 1:
        return
    bytes = prop_value(binding, from_place, 0, "bytes")
    output_place.push_token(Token({"bytes":bytes}))


pass_token = OutWeightFunc("pass_token", from_place=Place, num=int)
@pass_token.install
def output(binding, output_place, from_place, num):
    for i in range(num):
        token = get_token(binding, from_place, i)
        output_place.push_token(token)

pass_not_submessage = OutWeightFunc("pass_not_submessage", from_place=Place)
@pass_not_submessage.install
def output_token(binding, output_place, from_place):
    if not (prop_value(binding, from_place, 0, "type") == CstStr.SUBMESSAGE):
        output_place.push_token(Token())

pass_empty_token = OutWeightFunc("pass_empty_token")
@pass_empty_token.install
def output_token(binding, output_place):
    output_place.push_token(Token())
        
take_1_token = InWeightFunc("take_1_token")
@take_1_token.install
def number_of_token(binding):
    return 1 

take_some_token = InWeightFunc("take_some_token", num=int)
@take_some_token.install
def number_of_token(binding, num):
    return num

pass_repeated_array_token = OutWeightFunc("pass_repeated_array_token", from_place=Place, branch=int)
@pass_repeated_array_token.install
def output_token(binding, output_place, from_place, branch):
    if prop_value(binding, from_place, 0, "type") == branch:
        num = prop_value(binding, from_place, 0, "num")
        for i in range(num):
            output_place.push_token(Token())

pass_message_token = OutWeightFunc("pass_message_token", from_place=Place)
@pass_message_token.install
def output_token(binding, output_place, from_place):
    is_msg = prop_value(binding, from_place, 0, "type") ==  CstStr.SUBMESSAGE 
    if is_msg:
        tk = get_token(binding, from_place, 0)
        output_place.push_token(tk)

pass_non_message_token = OutWeightFunc("pass_non_message_token", from_place=Place)
@pass_non_message_token.install
def output_token(binding, output_place, from_place):
    is_msg = prop_value(binding, from_place, 0, "type") ==  CstStr.SUBMESSAGE 
    if not is_msg:
        tk = get_token(binding, from_place, 0)
        output_place.push_token(tk)

pass_non_top_token = OutWeightFunc("pass_non_top_token", from_place=Place)
@pass_non_top_token.install
def output_token(binding, output_place, from_place):
    is_top = prop_value(binding, from_place, 0, "end_of_top_level") == 1
    if not is_top:
        tk = get_token(binding, from_place, 0)
        output_place.push_token(tk)

pass_top_token = OutWeightFunc("pass_top_token", from_place=Place)
@pass_top_token.install
def output_token(binding, output_place, from_place):
    is_top = prop_value(binding, from_place, 0, "end_of_top_level") == 1
    if is_top:
        tk = get_token(binding, from_place, 0)
        output_place.push_token(tk)


pass_eom = OutWeightFunc("pass_eom", from_place=Place)
@pass_eom.install
def output_token(binding, output_place, from_place):
    if (CstStr.END_OF_MESSAGE  == prop_value(binding, from_place, 0, "type") or CstStr.END_OF_MESSAGE_TOP_LEVEL  == prop_value(binding, from_place, 0, "type")) and prop_value(binding, from_place, 0, "repeated") == 0:
        tk = get_token(binding, from_place, 0)
        output_place.push_token(tk)

   
pass_scalar = OutWeightFunc( "pass_scalar", from_place=Place)
@pass_scalar.install 
def output_token(binding, output_place, from_place):
    if prop_value(binding, from_place, 0, "type") == CstStr.SCALAR and prop_value(binding, from_place, 0, "repeated") == 0:
        tk = get_token(binding, from_place, 0)
        output_place.push_token(tk)
    
pass_non_scalar = OutWeightFunc("pass_non_scalar", from_place=Place)
@pass_non_scalar.install
def output_token(binding, output_place, from_place):
    if CstStr.NONSCALAR == prop_value(binding, from_place, 0, "type") and prop_value(binding, from_place, 0, "repeated") == 0:
        tk = get_token(binding, from_place, 0)
        output_place.push_token(tk)
    
pass_repeated = OutWeightFunc("pass_repeated", from_place=Place)    
@pass_repeated.install
def output_token(binding, output_place, from_place):
    if prop_value(binding, from_place, 0, "repeated") == 1:
        tk = get_token(binding, from_place, 0)
        output_place.push_token(tk)
    
pass_field_index_token = OutWeightFunc("pass_field_index_token", from_place=Place, index=int)
@pass_field_index_token.install
def output_token(binding, output_place, from_place, index):
    if prop_value(binding, from_place, 0, "field_index") == index:
        tk = get_token(binding, from_place, 0)
        output_place.push_token(tk)

pass_field_index_add_one = OutWeightFunc("pass_field_index_add_one", from_place=Place, num_handlers=int)
@pass_field_index_add_one.install
def output_token(binding, output_place, from_place, num_handlers):
    cur_idx = prop_value(binding, from_place, 0, "field_index")
    print("=== current index and next", cur_idx, cur_idx%num_handlers+1)
    output_place.push_token(Token({"field_index": cur_idx%num_handlers+1}))
    # output_place.push_token(Token({"field_index": 1}))

pass_write_hold_cond = OutWeightFunc("pass_write_hold_cond", from_place=Place)
@pass_write_hold_cond.install
def output_token(binding, output_place, from_place):
    end_of_field = prop_value(binding, from_place, 0, "end_of_field")
    if not end_of_field == 0:
        output_place.push_token(Token())

pass_write_index_holder_cond = OutWeightFunc("pass_write_index_holder_cond", from_place=Place, pass_token_place=Place)
@pass_write_index_holder_cond.install
def output_token(binding, output_place, from_place, pass_token_place):
    end_of_field = prop_value(binding, from_place, 0, "end_of_field")
    if end_of_field == 0:
        tk = get_token(binding, pass_token_place, 0)
        output_place.push_token(tk)
