from lpnlang import lpn_all_nodes
from .places import *
from .transitions import *

def Darwin():
    t_list = [t0]
    return lpn_all_nodes(t_list)