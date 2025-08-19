import numpy as np

from lpnlang import Place, Transition, Token
from protoacc_with_dma.lpn_def.transitions.components import *
from protoacc_with_dma.lpn_def.testing.parse_message import *

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


# def init_t_list():
#     common = FrontEnd("frontend", 6)
#     f1 = FieldHandler("f1", 1)
#     f2 = FieldHandler("f2", 2)
#     f3 = FieldHandler("f3", 3)
#     f4 = FieldHandler("f4", 4)
#     f5 = FieldHandler("f5", 5)
#     f6 = FieldHandler("f6", 6)

#     t_list = []
#     for _t_list in [
#                     common.transitions(), 
#                     f1.transitions(), 
#                     f2.transitions(),
#                     f3.transitions(),
#                     f4.transitions(),
#                     f5.transitions(),
#                     f6.transitions()]:
#         for _t in _t_list:
#             t_list.append(_t)
#     return t_list

# def init_p_list(t_list):
#     p_set = set()
#     for t in t_list:
#         for p in t.p_input:
#             p_set.add(p)
#         for p in t.p_output:
#             p_set.add(p)
#     return list(p_set) 

def reset(somelist):
    for e in somelist:
        e.reset()

def lpn_def():

    dmaread = DMAPortBase("dma_read_port", CstStr.READ, 8, 16, 20, 20)
    dmawrite = DMAPortBase("dma_write_port", CstStr.WRITE, 1, 16, 20, 20)
    frontend = FrontEnd("frontend", 6)
    f1 = FieldHandler("f1", 1)
    f2 = FieldHandler("f2", 2)
    f3 = FieldHandler("f3", 3)
    f4 = FieldHandler("f4", 4)
    f5 = FieldHandler("f5", 5)
    f6 = FieldHandler("f6", 6)
    comps = [frontend, f1, f2, f3, f4, f5, f6, dmaread, dmawrite]

    print(dmaread.port(1))
    f1.connect_memread_port(*(dmaread.port(2)))
    f2.connect_memread_port(*dmaread.port(3))
    f3.connect_memread_port(*dmaread.port(4))
    f4.connect_memread_port(*dmaread.port(5))
    f5.connect_memread_port(*dmaread.port(6))
    f6.connect_memread_port(*dmaread.port(7))
    
    frontend.connect_field_handler(f1, 1)
    frontend.connect_field_handler(f2, 2)
    frontend.connect_field_handler(f3, 3)
    frontend.connect_field_handler(f4, 4)
    frontend.connect_field_handler(f5, 5)
    frontend.connect_field_handler(f6, 6)

    memread_port_put_p_7, memread_port_get_p_7, memread_fifo_order_p, port_num_7 = dmaread.port(0)
    memread_port_put_p_8, memread_port_get_p_8, _, port_num_8 = dmaread.port(1)

    frontend.connect_memread_port([memread_port_put_p_7, memread_port_put_p_8],
                                  [memread_port_get_p_7, memread_port_get_p_8],
                                  memread_fifo_order_p, 
                                  [port_num_7, port_num_8])
    
    memwrite_port_put_p, memwrite_port_get_p, memwrite_fifo_order_p, port_num = dmawrite.port(0)
    frontend.connect_memwrite_port(memwrite_port_put_p, memwrite_port_get_p, memwrite_fifo_order_p, port_num)

    return comps

def setup(p_list, t_list, node_dict, messages):

    # p_list, t_list, node_dict = lpn_def()
    for p in p_list:
        p.reset()
    for t in t_list:
        t.reset()
    
    #init non-input tokens
    # install_tokens()
    #init input tokens
    parse_control_tokens(messages)
    parse_fields_and_units(messages)
    
    pmessage_tasks = node_dict["pmessage_tasks"]
    pfields_meta = node_dict["pfields_meta"]
    pfields = node_dict["pfields"]
    print(len(control_tokens))
    print(len(fields_meta_tokens))
    print(len(unit_tokens))
    pmessage_tasks.assign_marking(control_tokens)
    pfields_meta.assign_marking(fields_meta_tokens)
    pfields.assign_marking(unit_tokens)

def Protoacc(solver, messages):
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
    
    #init non-input tokens
    # install_tokens()

    #init input tokens
    parse_control_tokens(messages)
    parse_fields_and_units(messages)
    
    pmessage_tasks = node_dict["pmessage_tasks"]
    pfields_meta = node_dict["pfields_meta"]
    pfields = node_dict["pfields"]
    print(len(control_tokens))
    print(len(fields_meta_tokens))
    print(len(unit_tokens))
    pmessage_tasks.assign_marking(control_tokens)
    pfields_meta.assign_marking(fields_meta_tokens)
    pfields.assign_marking(unit_tokens)

    return p_list, t_list, node_dict


def ProtoaccWithMsg(messages):
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
    
    #init non-input tokens
    # install_tokens()

    #init input tokens
    parse_control_tokens(messages)
    parse_fields_and_units(messages)
    
    print("len control tokens", len(control_tokens))
    print("len fields meta tokens", len(fields_meta_tokens))
    print("len unit tokens", len(unit_tokens))
    comps[0].install_input_tokens(control_tokens, fields_meta_tokens, unit_tokens)

    return p_list, t_list, node_dict

def SetupWithMsg(comps, messages):

    #init input tokens
    parse_control_tokens(messages)
    parse_fields_and_units(messages)
    
    print("len control tokens", len(control_tokens))
    print("len fields meta tokens", len(fields_meta_tokens))
    print("len unit tokens", len(unit_tokens))
    comps[0].install_input_tokens(control_tokens, fields_meta_tokens, unit_tokens)

def ProtoaccWithMsgNoSetup():
    comps = lpn_def()
    t_list = init_t_list(comps)
    p_list = init_p_list(t_list)
    node_dict = {}
    print("len p_list", len(p_list), p_list)
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
    
    #init non-input tokens
    # install_tokens()

    return p_list, t_list, node_dict, comps
