import argparse
from mem.lpn_def.lpn import memory
from lpnlang import lpn_sim, Token
from lpnlang import dump_place_types, retrieve_place_types
from lpnlang.lpn2sim import pylpn2cpp
from mem.lpn_def.all_enum import CstStr
from collections import deque

def main(args):
    translate = True
    p_list, t_list, node_dict, comps = memory()
    if not translate:
        tokens = deque()
        for i in range(100):
            tokens.append(
                Token({"req_id": 0, "pid_fd":0, "addr": 0, "len": 512, "mem_buffer_ptr": 0, "type": 0, "ref_ptr": 0}))

        for i in range(10):
            tokens.append(
                Token({"req_id": 0, "pid_fd":0, "addr": 0, "len": 32, "mem_buffer_ptr": 0, "type": 0, "ref_ptr": 0}))
            
        node_dict["memory_req_front"].assign_marking(tokens)
        cycles = lpn_sim(t_list, node_dict, debug=True)
        dump_place_types(p_list, "place_types.txt")
        for p in p_list:
            print(p.id, len(p.tokens))
        print("latency = ", cycles) 
    else:
        retrieve_place_types(p_list, "place_types.txt")
        pylpn2cpp(p_list, t_list, CstStr)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog = 'vta sim',
                    description = 'simulates vta lpn',
                    epilog = '-b linked to benchmark file')
    parser.add_argument("-b", "--benchmark",  type=str, default="reference.insns")
    args = parser.parse_args()
    print(args)
    main(args)
