import sys
import json
import argparse
from collections import deque
import time as wallclock
import math
import uuid
from lpnlang import Place, Transition, Token
from lpnlang import lpn_sim
from lpnlang.lpn2sim import pylpn2cpp

from lpn_def.sim import lpndef_with_cpu as PcieWCPU
from lpn_def.funcs import create_empty_tokens
from lpn_def.all_enum import CstStr
from lpnlang import lpn_all_nodes
from param_x8 import *

def generate_random_data(node_dict, args):
    # unit is 128 bytes
    # lets assume transfer 1GB data
    # routing is handled internally
    # specify destination port
    device1_buf = node_dict["d1_reqbuf_nonpost"]
    device2_buf = node_dict["d2_reqbuf_nonpost"]
    device3_buf = node_dict["d3_reqbuf_nonpost"]

    device1_bufp = node_dict["d1_reqbuf_post"]
    device2_bufp = node_dict["d2_reqbuf_post"]
    device3_bufp = node_dict["d3_reqbuf_post"]
    # device4_buf = node_dict["d4_reqbuf"]
    # device5_buf = node_dict["d5_reqbuf"]
    # device6_buf = node_dict["d6_reqbuf"]
    # device7_buf = node_dict["d7_reqbuf"]
    # device8_buf = node_dict["d8_reqbuf"]

    tokens_queue_1 = deque()
    tokens_queue_2 = deque()
    tokens_queue_3 = deque()
    
    tokens_queue_1p = deque()
    tokens_queue_2p = deque()
    tokens_queue_3p = deque()
    # tokens_queue_4 = deque()
    # tokens_queue_5 = deque()
    # tokens_queue_6 = deque()
    # tokens_queue_7 = deque()
    # tokens_queue_8 = deque()
    def generate_chunk(chunk_size):
        # write 
        # the place can only have one set of keys, here there is a clear rewrite
        # tokens_queue_1.append(Token({"device": 2, "req": 0, "cmpl": chunk_size, "from": 1}))
        # read
        tokens_queue_1.append(Token({"device": CstStr.D2, "req": chunk_size, "cmpl": 16, "from": CstStr.D1}))
        tokens_queue_1.append(Token({"device": CstStr.D3, "req": chunk_size, "cmpl": 16, "from": CstStr.D1}))
        tokens_queue_2.append(Token({"device": CstStr.D1, "req": chunk_size, "cmpl": 16, "from": CstStr.D2}))
        tokens_queue_2.append(Token({"device": CstStr.D3, "req": chunk_size, "cmpl": 16, "from": CstStr.D2}))
        tokens_queue_3.append(Token({"device": CstStr.D2, "req": chunk_size, "cmpl": 16, "from": CstStr.D3}))
        tokens_queue_3.append(Token({"device": CstStr.D1, "req": chunk_size, "cmpl": 16, "from": CstStr.D3}))
        
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
            # chunk = math.ceil(remain_byte/64)*64
            chunk = math.ceil(remain_byte/16)*16
            generate_chunk(chunk)
            total_byte += chunk
            remain_byte = 0
 
    device1_buf.assign_marking(tokens_queue_1)
    device2_buf.assign_marking(tokens_queue_2)
    device3_buf.assign_marking(tokens_queue_3)

    device1_bufp.assign_marking(tokens_queue_1p)
    device2_bufp.assign_marking(tokens_queue_2p)
    device3_bufp.assign_marking(tokens_queue_3p)

    streams = []
    # streams.append(("w", 1, 2, total_byte))
    streams.append(("r", CstStr.D1, CstStr.D2, total_byte))
    streams.append(("r", CstStr.D1, CstStr.D3, total_byte))
    streams.append(("r", CstStr.D2, CstStr.D1, total_byte))
    streams.append(("r", CstStr.D2, CstStr.D3, total_byte))
    streams.append(("r", CstStr.D3, CstStr.D1, total_byte))
    streams.append(("r", CstStr.D3, CstStr.D2, total_byte))
    # streams.append(("r", 2, 1, total_byte))
    return streams

def main(args):

    # the cpu is device 2
    # the nic is device 1 
    p_list, t_list, node_dict = PcieWCPU()
   
    # generate_cytoscape_js(p_list, t_list)
    # exit()
    streams = generate_random_data(node_dict, args)    
    # node_dict["d3_recvcap"].assign_marking(create_empty_tokens(Credit//2))
    # for p in p_list:
    #     if len(p.tokens) != 0:
    #         print(p.id, len(p.tokens))
    # new_list = []
    # for t in t_list:
    #     if t.id != "root_send_18":
    #         new_list.append(t)
    # t_list = new_list

    print("==== start ====")
    latency = lpn_sim(t_list, node_dict)
    print("total cycles", latency)
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
        print(finish_idx, recvcomp, len(recvcomp.tokens))
        if finish_idx != -1 and len(recvcomp.tokens) > finish_idx:
            latency = recvcomp.tokens[finish_idx].ts
            print(f" ==== stream (rw:{type}, d{requster}, d{dst}, {len(recvcomp.tokens)} with {total}B) ============== ")
            print(" total time in us:", latency/FMHz)
            print(" total time in ns:", latency/FMHz*1000)
            bw = total*FMHz/(latency*1000)*8
            print(" bandwith in Gb/s:", bw)
            print(" ================================================== ")
        else:
            print("DATA LOST")
    print(" ============         END           =============== ")

    # for tk in node_dict[f"d2_recvreq"].tokens:
    #     print("recvreq", tk.dir)

    # for tk in node_dict[f"d2_recvcomp"].tokens:
    #     print("recvcomp", tk.dir)
    
    for p in p_list:
        if len(p.tokens) != 0:
            print(p.id, len(p.tokens))

    for t in t_list:
        print(t.id, t.count)

    p_list, t_list, _ = lpn_all_nodes(t_list)
    pylpn2cpp(p_list, t_list, CstStr)


parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')

parser.add_argument("-c", "--chunk",  type=int, default=64)
parser.add_argument("-t", "--total",  type=int, default=64)
args = parser.parse_args()
print(args)
main(args)

