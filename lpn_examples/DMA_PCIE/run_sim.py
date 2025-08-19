import argparse
from collections import deque
import math
from lpnlang import Place, Transition, Token
from lpnlang import lpn_sim
from lpnlang.lpn2sim import pylpn2cpp
from lpnlang import dump_place_types, retrieve_place_types
from pcie_topo.lpn_def.pcie_components import PcieSwitch, PcieDevice, PcieUniDirLink, MemDevice
from pcie_topo.lpn_def.funcs import *
from pcie_topo.lpn_def.all_enum import CstStr
from pcie_topo.lpn_def.def_topo import *
from pcie_topo.lpn_def.funcs import *
from pcie_topo.lpn_def.helper import arbiterHelper, arbiterWTimeOrdHelper, arbiterHelperNoCap, arbiterHelperNoCapWPort, pass_type_idx

'''
the token traversing the pcie topology should have req_ref that contains the actual request
one request can be chunked in the LPN because of MPS, so the token should contain an offset from the initial request
'''

def define_topology_with_mem():

    dual_port_root = [0, 1]
    root = PcieSwitch("root", dual_port_root, is_rootcomplex=True)
    device0 = MemDevice("d0")
    device1 = PcieDevice("d1")
    
    links = []
    # start to connect the switches and root

    l1, l2 = connect_device(root, 0, device0)
    links.extend([l1, l2])
    l1, l2 = connect_device(root, 1, device1)
    links.extend([l1, l2])

    # populate rout infomation
    list_of_device_int_id = [CstStr.D0, CstStr.D1]
    install_rout(root, list_of_device_int_id, [0, 1])

    comp_list = [root, device1, device0]
    comp_list.extend(links)
    return comp_list


    dual_port_s1 = [0, 1]
    switch1 = PcieSwitch("s1", dual_port_s1)

    dual_port_root = [0, 1]
    root = PcieSwitch("root", dual_port_root, is_rootcomplex=True)

    'this is the mem device'
    device0 = MemDevice("d0")

    device1 = PcieDevice("d1")
    
    links = []

    # start to connect the switches and root
    l1, l2 = connect(root, 1, switch1, 0)
    links.extend([l1, l2])

    l1, l2 = connect_device(switch1, 1, device1)
    links.extend([l1, l2])
    l1, l2 = connect_device(root, 0, device0)
    links.extend([l1, l2])

    # populate rout infomation
    list_of_device = [device0, device1]
    list_of_device_int_id = [CstStr.D0, CstStr.D1]
    install_rout(switch1, list_of_device_int_id, [0, 1])
    install_rout(root, list_of_device_int_id, [0, 1])
    comp_list = [root, switch1, device0, device1]
    comp_list.extend(links)
    return comp_list

def init_p_list(t_list):
    p_set = set()
    for t in t_list:
        for p in t.p_input:
            p_set.add(p)
        for p in t.p_output:
            p_set.add(p)
    return list(p_set) 

def init_t_list(comps):
    t_list = []
    for comp in comps:
        t_list.extend(comp.transitions())
    return t_list

def lpndef():
    pcie_comp = define_topology_with_mem()
    t_list = init_t_list(pcie_comp)
    p_list = init_p_list(t_list) 
    node_dict = {}
    for p in p_list:
        node_dict[p.id] = p 
    for t in t_list:
        node_dict[t.id] = t 
    
    return p_list, t_list, node_dict

def generate_random_data(node_dict, args):
    device1_buf = node_dict["d1_reqbuf_nonpost"]
    device1_bufp = node_dict["d1_reqbuf_post"]

    tokens_queue_1 = deque()
    tokens_queue_2 = deque()
    tokens_queue_3 = deque()
    tokens_queue_1p = deque()
    tokens_queue_2p = deque()
    tokens_queue_3p = deque()
    def generate_chunk(chunk_size):
        # 'read'
        tokens_queue_1.append(Token({"dst": CstStr.D0,  "src": CstStr.D1, "type": CstStr.READ, "pkt_size": 16, "offset":0, "dataref": chunk_size}))
        # 'write'
        # tokens_queue_1p.append(Token({"dst": CstStr.D0,  "src": CstStr.D1, "type": CstStr.WRITE, "pkt_size": chunk_size, "offset":0, "dataref": chunk_size}))
        # 'need reply'
        # 'need no reply'
        # tokens_queue_1.append(Token({"dst": CstStr.D0, "type": 1, "pkt_size": chunk_size, "src": CstStr.D1}))
    
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
    device1_bufp.assign_marking(tokens_queue_1p)

    'record read streams'
    streams = []
    streams.append(("r", CstStr.D1, CstStr.D0, total_byte))
    return streams

def main(args):

    p_list, t_list, node_dict = lpndef()
    streams = generate_random_data(node_dict, args)    
    # print("==== start ====")
    latency = lpn_sim(t_list, node_dict, debug=False)
    # dump_place_types(p_list, "place_types.txt")
    # retrieve_place_types(p_list, "place_types.txt")
    # pylpn2cpp(p_list, t_list, CstStr)

    print("  latency = ", latency)
    for stream in streams:
        type, requster, dst, total = stream
        if type == "r":
            recvcmpl = node_dict[f"d{requster}_recvcmpl"]
            ori = dst
        else:
            recvcmpl = node_dict[f"d{dst}_recvcmpl"]
            ori = requster
        finish_idx = -1
        cnt = 0
        for ith, tk in enumerate(recvcmpl.tokens):
            print(tk.prop_dict())
            if tk.__dict__["src"] == ori and tk.type == CstStr.CMPL:
                cnt += tk.pkt_size
                if cnt == total:
                    finish_idx = ith
                    break
        if finish_idx != -1 and len(recvcmpl.tokens) > finish_idx:
            latency = recvcmpl.tokens[finish_idx].ts
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

