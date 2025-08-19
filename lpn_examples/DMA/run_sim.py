import argparse
from collections import deque
import math
from lpnlang import Place, Transition, Token
from lpnlang import lpn_sim
from lpnlang import dump_place_types, retrieve_place_types
from lpnlang.lpn2sim import pylpn2cpp
from lpn_def.dma_ports import *

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

dma_comp = []
def lpndef_init():
    READ = 0
    WRITE = 1
    dma_comp.extend([DMAPortBase("dma_read_port", READ, 8), DMAPortBase("dma_write_port", WRITE, 1)])
    t_list = init_t_list(dma_comp)
    p_list = init_p_list(t_list) 
    node_dict = {}
    for p in p_list:
        node_dict[p.id] = p 
    for t in t_list:
        node_dict[t.id] = t 
    
    return p_list, t_list, node_dict

def generate_random_data(node_dict, args):
    for i in range(8):
        dma_comp[0].put(i, i, 0, 64, 0, 0)
    for i in range(1):
        dma_comp[1].put(i, i, 0, 64, 0, 0)

def main(args):

    p_list, t_list, node_dict = lpndef_init()
    # generate_random_data(node_dict, args)    
    # print("==== start ====")
    # latency = lpn_sim(t_list, node_dict, debug=False)
    # dump_place_types(p_list, "place_types.txt")
    # for t in t_list:
    #     print(t.id, t.count)
    # for i in range(8):
    #     print("read port resp", i, dma_comp[0].get(i)[0].prop_dict())
    # for i in range(1):
    #     print("write port resp", i, dma_comp[1].get(i)[0].prop_dict())
    # print("  latency = ", latency)

    retrieve_place_types(p_list, "place_types.txt")
    pylpn2cpp(p_list, t_list, None)

    

parser = argparse.ArgumentParser(
                    prog = 'run_example.py',
                    description = 'Simulates PCIe topology with constant latency memory')

parser.add_argument("-t", "--total",  type=int, default=64)
args = parser.parse_args()
main(args)

