from lpnlang import lpn_all_nodes
from .places import *
from .transitions import *
from .setup import setup as setup_with_img

def JPEG():
    t_list = [t0, t1, t2, t3, t4, t5, t2p, t3p, t4p]
    return lpn_all_nodes(t_list)

def setup(p_list, t_list, node_dict, img):
    for p in p_list:
        p.reset()
    for t in t_list:
        t.reset()
    setup_with_img(img)