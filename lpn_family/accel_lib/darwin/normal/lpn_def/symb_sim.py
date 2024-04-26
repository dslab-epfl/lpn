from lpnlang import lpn_all_nodes
from .places import *
from .transitions import *
from .setup import symbolic_setup_

def symbolic_setup(p_list, t_list, node_dict, params=None):
    for p in p_list:
        p.reset()
    for t in t_list:
        t.reset()
    symbolic_setup_()