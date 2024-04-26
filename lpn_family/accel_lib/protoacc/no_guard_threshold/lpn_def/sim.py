import numpy as np

from lpnlang import Place, Transition, Token
from lpn_def.places.install_tokens import install_tokens 
from lpn_def.transitions.f1 import f1_ts
from lpn_def.transitions.f2 import f2_ts
from lpn_def.transitions.f3 import f3_ts
from lpn_def.transitions.f4 import f4_ts
from lpn_def.transitions.f5 import f5_ts
from lpn_def.transitions.f6 import f6_ts
from lpn_def.transitions.common import common_ts
from lpn_def.testing.parse_message import *
from lpn_def.testing.gen_message import *

def init_t_list():
    fcommon = common_ts()
    f1 = f1_ts()
    f2 = f2_ts()
    f3 = f3_ts()
    f4 = f4_ts()
    f5 = f5_ts()
    f6 = f6_ts()
    t_list = []
    for _t_list in [fcommon, f1, f2,f3,f4,f5,f6]:
    # for _t_list in [fcommon, f1]:
        for _t in _t_list:
            t_list.append(_t)
    return t_list

def init_p_list(t_list):
    p_set = set()
    for t in t_list:
        for p in t.p_input:
            p_set.add(p)
        for p in t.p_output:
            p_set.add(p)
    return list(p_set) 

def reset(somelist):
    for e in somelist:
        e.reset()

def lpn_def():
    t_list = init_t_list()
    p_list = init_p_list(t_list)
    node_dict = {}
    for p in p_list:
        node_dict[p.id] = p 
    for t in t_list:
        node_dict[t.id] = t 
    
    return p_list, t_list, node_dict

def setup(p_list, t_list, node_dict, messages):

    # p_list, t_list, node_dict = lpn_def()
    for p in p_list:
        p.reset()
    for t in t_list:
        t.reset()
    
    #init non-input tokens
    install_tokens()
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

    p_list, t_list, node_dict = lpn_def()
    for p in p_list:
        p.reset()
    for t in t_list:
        t.reset()
    
    #init non-input tokens
    install_tokens()

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
