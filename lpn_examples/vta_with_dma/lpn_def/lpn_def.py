from .transitions import *
from lpnlang import lpn_all_nodes

def lpn_def():
    t_list = [t12, t9, t13, t14, t15, t16, tcompute_launch, tstore_launch, tload_launch, tcompute_done, tstore_done, tload_done ]
    p_list, _, node_dict = lpn_all_nodes(t_list)
    return p_list, t_list, node_dict