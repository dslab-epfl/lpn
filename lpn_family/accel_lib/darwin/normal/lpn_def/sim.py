from lpnlang import lpn_all_nodes
from .places import *
from .transitions import *
from .setup import setup as setup_with_dna_pairs

def Darwin():
    t_list = [t0]
    return lpn_all_nodes(t_list)

def setup(p_list, t_list, node_dict, dna_pairs):
    for p in p_list:
        p.reset()
    for t in t_list:
        t.reset()
    setup_with_dna_pairs(dna_pairs)