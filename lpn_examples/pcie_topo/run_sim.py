import argparse
from collections import deque
import math
from lpnlang import Place, Transition, Token
from lpnlang import lpn_sim
from lpn_def.sim import lpndef_with_cpu as PcieWCPU
from lpn_def.all_enum import CstStr
from param_x8 import *

def generate_random_data(node_dict, args):
    device1_buf = node_dict["d1_reqbuf_nonpost"]
    device2_buf = node_dict["d2_reqbuf_nonpost"]
    device3_buf = node_dict["d3_reqbuf_nonpost"]
    device1_bufp = node_dict["d1_reqbuf_post"]
    device2_bufp = node_dict["d2_reqbuf_post"]
    device3_bufp = node_dict["d3_reqbuf_post"]

    tokens_queue_1 = deque()
    tokens_queue_2 = deque()
    tokens_queue_3 = deque()
    tokens_queue_1p = deque()
    tokens_queue_2p = deque()
    tokens_queue_3p = deque()
    def generate_chunk(chunk_size):
        'read'
        tokens_queue_1.append(Token({"device": CstStr.D2, "req": chunk_size, "cmpl": 16, "from": CstStr.D1}))
        tokens_queue_1.append(Token({"device": CstStr.D3, "req": chunk_size, "cmpl": 16, "from": CstStr.D1}))
        tokens_queue_2.append(Token({"device": CstStr.D1, "req": chunk_size, "cmpl": 16, "from": CstStr.D2}))
        tokens_queue_2.append(Token({"device": CstStr.D3, "req": chunk_size, "cmpl": 16, "from": CstStr.D2}))
        tokens_queue_3.append(Token({"device": CstStr.D2, "req": chunk_size, "cmpl": 16, "from": CstStr.D3}))
        tokens_queue_3.append(Token({"device": CstStr.D1, "req": chunk_size, "cmpl": 16, "from": CstStr.D3}))
        'write'
        tokens_queue_1p.append(Token({"device": CstStr.D2, "req": 0, "cmpl": chunk_size, "from": CstStr.D1}))
        tokens_queue_1p.append(Token({"device": CstStr.D3, "req": 0, "cmpl": chunk_size, "from": CstStr.D1}))
        tokens_queue_2p.append(Token({"device": CstStr.D1, "req": 0, "cmpl": chunk_size, "from": CstStr.D2}))
        tokens_queue_2p.append(Token({"device": CstStr.D3, "req": 0, "cmpl": chunk_size, "from": CstStr.D2}))
        tokens_queue_3p.append(Token({"device": CstStr.D2, "req": 0, "cmpl": chunk_size, "from": CstStr.D3}))
        tokens_queue_3p.append(Token({"device": CstStr.D1, "req": 0, "cmpl": chunk_size, "from": CstStr.D3}))
    remain_byte = args.total
    total_byte = 0
    while remain_byte > 0:
        if remain_byte >= READMPS:
            generate_chunk(READMPS)
            remain_byte -= READMPS
            total_byte += READMPS
        else:
            chunk = math.ceil(remain_byte/64)*64
            generate_chunk(chunk)
            total_byte += chunk
            remain_byte = 0
 
    device1_buf.assign_marking(tokens_queue_1)
    device2_buf.assign_marking(tokens_queue_2)
    device3_buf.assign_marking(tokens_queue_3)
    device1_bufp.assign_marking(tokens_queue_1p)
    device2_bufp.assign_marking(tokens_queue_2p)
    device3_bufp.assign_marking(tokens_queue_3p)

    'record read streams'
    streams = []
    streams.append(("r", CstStr.D1, CstStr.D2, total_byte))
    streams.append(("r", CstStr.D1, CstStr.D3, total_byte))
    streams.append(("r", CstStr.D2, CstStr.D1, total_byte))
    streams.append(("r", CstStr.D2, CstStr.D3, total_byte))
    streams.append(("r", CstStr.D3, CstStr.D1, total_byte))
    streams.append(("r", CstStr.D3, CstStr.D2, total_byte))
    return streams

def main(args):

    p_list, t_list, node_dict = PcieWCPU()
    streams = generate_random_data(node_dict, args)    
    print("==== start ====")
    latency = lpn_sim(t_list, node_dict)
    print("  latency = ", latency)
    for stream in streams:
        type, requster, dst, total = stream
        if type == "r":
            recvcomp = node_dict[f"d{requster}_recvcomp"]
            ori = dst
        else:
            recvcomp = node_dict[f"d{dst}_recvcomp"]
            ori = requster
        finish_idx = -1
        cnt = 0
        for ith, tk in enumerate(recvcomp.tokens):
            if tk.__dict__["from"] == ori and tk.req == 0:
                cnt += tk.cmpl
                if cnt == total:
                    finish_idx = ith
                    break
        if finish_idx != -1 and len(recvcomp.tokens) > finish_idx:
            latency = recvcomp.tokens[finish_idx].ts
            print(f" ==== stream (rw:{type}, requested by: d{requster}, requeste to: d{dst}, with {total}B) ====")
            print(" total time in us:", latency/FMHz)
            print(" total time in ns:", latency/FMHz*1000)
            bw = total*FMHz/(latency*1000)*8
            print(" bandwith in Gb/s:", bw)
            print(" =====================================================================")
        else:
            print("(ERROR) Data is lost")
    print(" ============         END           ==================================")

parser = argparse.ArgumentParser(
                    prog = 'run_example.py',
                    description = 'Simulates PCIe topology with constant latency memory')

parser.add_argument("-t", "--total",  type=int, default=64)
args = parser.parse_args()
main(args)

