from lpnlang import lpn_all_nodes
from .places import *
from .transitions import *

def JPEG():
    t_list = [t0, t1, t2, t3, t4, t5, t2p, t3p, t4p]
    return lpn_all_nodes(t_list)