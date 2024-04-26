from lpn_def.def_topo import init_topology_1, init_topology_2, init_topology_3, init_topology_with_cpu
# from lpn_def.def_topo_with_jpeg import init_topology_with_jpeg, init_topology_with_mem,  init_topology_test

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

# def lpndef():
#     pcie_comp = init_topology_2()
#     t_list = init_t_list(pcie_comp)
#     p_list = init_p_list(t_list) 
#     node_dict = {}
#     for p in p_list:
#         node_dict[p.id] = p 
#     for t in t_list:
#         node_dict[t.id] = t 
    
#     return p_list, t_list, node_dict


def lpndef_with_cpu():
    pcie_comp = init_topology_with_cpu()
    t_list = init_t_list(pcie_comp)
    p_list = init_p_list(t_list) 
    node_dict = {}
    for p in p_list:
        node_dict[p.id] = p 
    for t in t_list:
        node_dict[t.id] = t 
    
    return p_list, t_list, node_dict


# def lpndef_with_jpeg():
#     pcie_comp = init_topology_with_jpeg()
#     t_list = init_t_list(pcie_comp)
#     p_list = init_p_list(t_list) 
#     node_dict = {}
#     for p in p_list:
#         node_dict[p.id] = p 
#     for t in t_list:
#         node_dict[t.id] = t 
    
#     return p_list, t_list, node_dict

# def lpndef_with_mem():
#     pcie_comp = init_topology_with_mem()
#     t_list = init_t_list(pcie_comp)
#     p_list = init_p_list(t_list) 
#     node_dict = {}
#     for p in p_list:
#         node_dict[p.id] = p 
#     for t in t_list:
#         node_dict[t.id] = t 
    
#     return p_list, t_list, node_dict


# def lpndef_test():
#     pcie_comp = init_topology_test()
#     t_list = init_t_list(pcie_comp)
#     p_list = init_p_list(t_list) 
#     node_dict = {}
#     for p in p_list:
#         node_dict[p.id] = p 
#     for t in t_list:
#         node_dict[t.id] = t 
    
#     return p_list, t_list, node_dict
