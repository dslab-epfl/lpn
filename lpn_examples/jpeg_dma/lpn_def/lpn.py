from jpeg_dma.lpn_def.components import *
from lpnlang import lpn_all_nodes

def init_p_list(t_list):
    p_set = set()
    for t in t_list:
        # print("=== ", t.id)
        for p in t.p_input:
            # print(p.id)
            p_set.add(p)
        for p in t.p_output:
            # print(p.id)
            p_set.add(p)
    return list(p_set) 

def init_t_list(comps):
    t_list = []
    for comp in comps:
        t_list.extend(comp.transitions())
    return t_list

def lpn_def():
    READ, WRITE = 0, 1
    dma_read = DMAPortBase("dma_read", READ, 1, 16, 400, 400)
    dma_write = DMAPortBase("dma_write", WRITE, 1, 16, 400, 400)
    jpeg = JPEG("jpeg", dma_read, dma_write)
    return [dma_read, dma_write, jpeg]

def jpeg():
    comps = lpn_def()
    t_list = init_t_list(comps)
    p_list = init_p_list(t_list)
    node_dict = {}
    for p in p_list:
        node_dict[p.id] = p 
    for t in t_list:
        node_dict[t.id] = t 
    
    for p in p_list:
        p.reset()
    for t in t_list:
        t.reset()

    for comp in comps:
        comp.init_places()
    
    return p_list, t_list, node_dict, comps
