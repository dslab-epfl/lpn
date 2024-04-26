from lpnlang import lpn_all_nodes
from .places import *
from .transitions import *
from .setup import symbolic_setup_with_blocks

def JPEG():
    t_list = [t0, t1, t2, t3, t4, t5, t2p, t3p, t4p]
    return lpn_all_nodes(t_list)

def symbolic_setup(p_list, t_list, node_dict, num_blocks):
    for p in p_list:
        p.reset()
    for t in t_list:
        t.reset()
    symbolic_setup_with_blocks(num_blocks)