from lpnlang import Place, Transition, Token
from lpnlang import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from lpnlang import prop_value
from vta_with_dma.lpn_def.places import *
from vta_with_dma.lpn_def.all_enum import CstStr


mem_request = OutWeightFunc("mem_request", port=int, id=int, num=int)
@mem_request.install
def output(binding, output_place, port, id, num):
    for i in range(num):
        tk = Token({"id": id, "addr": 0, "size": 0, "buffer": 0, "rw": 0, "ref": port})
        output_place.push_token(tk)

push_request_order = OutWeightFunc("push_request_order", port=int, num=int)
@push_request_order.install
def output(binding, output_place, port, num):
    for i in range(num):
        output_place.push_token(Token({"idx": port}))

take_resp_token_load_module = InWeightFunc("take_resp_token_load_module", insn_place=Place)
@take_resp_token_load_module.install
def input(binding, insn_place):
    tstype = prop_value(binding, insn_place, 0, "tstype")
    ysize = prop_value(binding, insn_place, 0, "ysize")
    if tstype == CstStr.INP or tstype == CstStr.WGT:
        return ysize
    return 0

mem_request_load_module = OutWeightFunc("mem_request_load_module", port=int, insn_place=Place)
@mem_request_load_module.install
def output(binding, output_place, port, insn_place):
    tstype = prop_value(binding, insn_place, 0, "tstype")
    ysize = prop_value(binding, insn_place, 0, "ysize")
    if tstype == CstStr.INP:
        for i in range(ysize):
            output_place.push_token(
                Token(
                {"id": CstStr.DMA_LOAD_INP, "addr": 0, "size": 0, "buffer": 0, "rw": 0, "ref": port})
            )
    elif tstype == CstStr.WGT:
        for i in range(ysize):
            output_place.push_token(
                Token(
                {"id": CstStr.DMA_LOAD_WGT, "addr": 0, "size": 0, "buffer": 0, "rw": 0, "ref": port})
            )

push_request_order_load_module = OutWeightFunc("push_request_order_load_module", port=int, insn_place=Place)
@push_request_order_load_module.install
def output(binding, output_place, port, insn_place):
    tstype = prop_value(binding, insn_place, 0, "tstype")
    ysize = prop_value(binding, insn_place, 0, "ysize")
    if tstype == CstStr.INP or tstype == CstStr.WGT:
        for i in range(ysize):
            output_place.push_token(Token({"idx": port}))


mem_request_store_module = OutWeightFunc("mem_request_store_module", port=int, insn_place=Place)
@mem_request_store_module.install
def output(binding, output_place, port, insn_place):
    subopcode = prop_value(binding, insn_place, 0, "subopcode")
    xsize = prop_value(binding, insn_place, 0, "xsize")
    ysize = prop_value(binding, insn_place, 0, "ysize")
    if subopcode != CstStr.SYNC:
        for i in range(xsize * ysize):
            output_place.push_token(
                Token(
                {"id": CstStr.DMA_STORE, "addr": 0, "size": 0, "buffer": 0, "rw": 1, "ref": port})
            )

push_request_order_store_module = OutWeightFunc("push_request_order_store_module", port=int, insn_place=Place)
@push_request_order_store_module.install
def output(binding, output_place, port, insn_place):
    subopcode = prop_value(binding, insn_place, 0, "subopcode")
    xsize = prop_value(binding, insn_place, 0, "xsize")
    ysize = prop_value(binding, insn_place, 0, "ysize")
    if subopcode != CstStr.SYNC:
        for i in range(xsize * ysize):
            output_place.push_token(Token({"idx": port}))

take_resp_token_store_module = InWeightFunc("take_resp_token_store_module", insn_place=Place)
@take_resp_token_store_module.install
def input(binding, insn_place):
    subopcode = prop_value(binding, insn_place, 0, "subopcode")
    xsize = prop_value(binding, insn_place, 0, "xsize")
    ysize = prop_value(binding, insn_place, 0, "ysize")
    if subopcode != CstStr.SYNC:
        return xsize * ysize
    return 0

take_resp_token_compute_module = InWeightFunc("take_resp_token_compute_module", insn_place=Place)
@take_resp_token_compute_module.install
def input(binding, insn_place):
    subopcode = prop_value(binding, insn_place, 0, "subopcode")
    ysize = prop_value(binding, insn_place, 0, "ysize")
    if subopcode == CstStr.LOADACC or subopcode == CstStr.LOADUOP:
        return ysize
    return 0

mem_request_compute_module = OutWeightFunc("mem_request_compute_module", port=int, insn_place=Place)
@mem_request_compute_module.install
def output(binding, output_place, port, insn_place):
    subopcode = prop_value(binding, insn_place, 0, "subopcode")
    ysize = prop_value(binding, insn_place, 0, "ysize")
    if subopcode == CstStr.LOADACC:
        for i in range(ysize):
            output_place.push_token(
                Token(
                {"id": CstStr.DMA_LOAD_ACC, "addr": 0, "size": 0, "buffer": 0, "rw": 0, "ref": port})
            )
    elif subopcode == CstStr.LOADUOP:
        for i in range(ysize):
            output_place.push_token(
                Token(
                {"id": CstStr.DMA_LOAD_UOP, "addr": 0, "size": 0, "buffer": 0, "rw": 0, "ref": port})
            )

push_request_order_compute_module = OutWeightFunc("push_request_order_compute_module", port=int, insn_place=Place)
@push_request_order_compute_module.install
def output(binding, output_place, port, insn_place):
    subopcode = prop_value(binding, insn_place, 0, "subopcode")
    ysize = prop_value(binding, insn_place, 0, "ysize")
    if subopcode == CstStr.LOADACC or subopcode == CstStr.LOADUOP:
        for i in range(ysize):
            output_place.push_token(Token({"idx": port}))
