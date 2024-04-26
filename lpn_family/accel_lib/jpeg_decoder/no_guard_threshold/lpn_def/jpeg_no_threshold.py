import uuid
from parameters import *
import lpn2smt.z3_util as z3_util
from collections import deque
from place_transition import Place, Transition, Token, IntSymbol
from lpn2smt.verify_place import VPlace
from lpn2smt.verify_transition import VTransition
import random

COUNTER = 0

symb_list = []
z3_var_list = []
value_list = []

counter = 0
def global_count():
    counter += 1
    return counter

def JPEG(solver, args):
    Token.solver = solver
    IntSymbol.solver = solver
    var_63_64 = 64
    cap = 4 
    # pt 
    def create_empty_tokens(num):
        tokens = deque()
        for i in range(num):
            token = Token()
            token.t = IntSymbol(0)
            tokens.append(token)
        return tokens
        
    ptasks = VPlace("ptasks", create_empty_tokens(tasks_number*6//4))
    print("initial ptasks", len(ptasks.tokens))
    pstart = VPlace("pstart")
    p4 = VPlace("p4", create_empty_tokens(4))
    
    # for abstract
    # p4.cap_node = True

    # p4 = VPlace("p4")
    # p4.tokens_init_symbolic = False
    # p4.tokens_init_symbolic_range = [1, 4]
    
    p0 = VPlace("p0")
    p1 = VPlace("p1")
    p2 = VPlace("p2")
    p3 = VPlace("p3")
    p5 = VPlace("p5", create_empty_tokens(7))
    p6 = VPlace("p6", create_empty_tokens(4))
    p7 = VPlace("p7")
    p8 = VPlace("p8", create_empty_tokens(1))
    p10 = VPlace("p10")
    # p11 = VPlace("p11", create_empty_tokens(4))
    p20 = VPlace("p20", create_empty_tokens(4))
    # p20.cap_node = True
    
    p21 = VPlace("p21")
    p22 = VPlace("p22")
    pdone = VPlace("pdone")
    pt2p = VPlace("pt2p")
    pt3p = VPlace("pt3p")
    pt4p = VPlace("pt4p")
    pt2p_hold = VPlace("pt2p_hold", create_empty_tokens(1))
    pt3p_hold = VPlace("pt3p_hold", create_empty_tokens(1))
    pt4p_hold = VPlace("pt4p_hold", create_empty_tokens(1))

    pvarlatency = VPlace("pvarlatency")
    pvarlatency.type_annotations = ["delay"]
    delay_list = [8,8,125,67,8,49,8,8,67,8,8,198,66,49,8,8,8,8,197,68,8,8,49,67,197,67,67,67,8,8,51,198,8,125,8,8]
    delay_list = [200, 200, 66,8,50,8,200,194,66,66,66,8]
    delay_list = [138,139,191,193,194,195,11,9,9,9,9,10,9,12,9,10,190,192]
    delay_list = [100, 100, 100, 100,100, 100,10,10,10,10,10,10,9,12,9,10,190,192]
    # delay_list = [165, 40, 12, 13, 71, 195, 164, 162, 194, 163, 10, 161, 70, 193, 38, 39, 11, 9]
    delay_list = [16, 40, 12, 13, 71, 19, 16, 16, 19, 16, 10, 16, 70, 19, 38, 39, 11, 9]
    delay_list = [36]*12
    
    print("mean delay list", sum(delay_list)/len(delay_list))
    for i in range(tasks_number*6//4):
        global COUNTER
        # d = random.randint(8, 216)
        d = delay_list[COUNTER%len(delay_list)]
        value_list.append(d)
        # symbol = IntSymbol(d, symref=f"SYMREF{COUNTER}", z3range=(9, 195), z3varname=f"z3_delay{COUNTER}" )
        # symbol = IntSymbol(d, symref=f"SYMREF{COUNTER}", z3range=(9, 195))
        symbol = IntSymbol(d, symref=f"SYMREF{COUNTER}", z3range=(d, d))
        # symbol = IntSymbol(d, symref=f"SYMREF{COUNTER}", z3range=(10, 10))
        # symbol = IntSymbol(d, symref=f"SYMREF{COUNTER}")
        pvarlatency.tokens.append(Token({"delay": symbol}))
        symb_list.append(symbol.symref())
        z3_var_list.append(symbol.z3_value())

        COUNTER += 1

    def con_edge(number):
        def weight(binding=None):
            return number
        return weight

    def constant_func(scale):
        def constant(binding=None):
            return scale
        return constant

    def con_tokens(number):
        def output_tokens(binding=None):
            tokens = deque()
            for i in range(number):
                tokens.append(Token())
            return tokens
        return output_tokens

    constant_66 = constant_func(66)
    constant_0  = constant_func(0)
    constant_67 = constant_func(67)
    constant_65 = constant_func(65)
    constant_68 = constant_func(68)

    c0 = con_edge(0)
    c1 = con_edge(1)
    c2 = con_edge(2)
    c4 = con_edge(4)
    c64 = con_edge(64)
    c32 = con_edge(32)
    c16 = con_edge(16)
    c256 = con_edge(256)

    ct1 = con_tokens(1)
    ct2 = con_tokens(2)
    ct4 = con_tokens(4)

    def mcu_delay():
        def delay(binding=None):
            # return binding["pvarlatency.0.delay"].concrete()
            return binding["pvarlatency.0.delay"]
        return delay

    t2p = VTransition("t2p", constant_func(0), pi=[p0, p20, p6, pt2p_hold], po=[pt2p, p6], pi_w=[c1,  c1,  c2, c1], po_w=[ct1, ct2] )
    t3p = VTransition("t3p", constant_func(0), pi=[p0, p21, p6, pt3p_hold], po=[pt3p, p6], pi_w=[c1,  c4,  c2, c1], po_w=[ct1, ct2] )
    t4p = VTransition("t4p", constant_func(0), pi=[p0, p22, p6, pt4p_hold], po=[pt4p, p6], pi_w=[c1,  c1,  c2, c1], po_w=[ct1, ct2] )
   
    t2 = VTransition("t2", constant_func(66), pi=[pt2p], po=[p1, p21, p4, pt2p_hold], pi_w=[c1], po_w=[ct1,  ct1, ct1, ct1] )
    t3 = VTransition("t3", constant_func(66), pi=[pt3p], po=[p2, p22, p4, pt3p_hold], pi_w=[c1], po_w=[ct4,  ct1, ct1, ct1])
    t4 = VTransition("t4", constant_func(66), pi=[pt4p, p6], po=[p3, p20, p4, pt4p_hold], pi_w=[c1, c4], po_w=[ct4,  ct4, ct1, ct1])

    t5 = VTransition("t5", constant_func(65), pi=[p1, p2, p3], po=[pdone, p5, p6], pi_w=[c1, c1, c1], po_w=[ct1, ct1, ct1])
    t0 = VTransition("t0", mcu_delay(), pi=[p7, p4, pvarlatency], po=[p0, p8], pi_w=[c1, c1, c1], po_w=[ct1, ct1])
    t1 = VTransition("t1", constant_func(0), pi=[ptasks, p8], po=[p7, pstart], pi_w=[c1, c1], po_w=[ct1, ct1])
 

    t_list = [t0, t1, t2, t3, t4, t5, t2p, t3p, t4p]
    # t_list = [t0, t2, t3, t4]
    # t_list = [t0, t1]
    # t_list = [t0, t1]
    p_list = [ptasks, pstart, pdone, p0, p1, p2, p3, p4, p5, p6, p7, p8, p20,p21,p22, pvarlatency, pt2p, pt3p, pt4p, pt2p_hold, pt3p_hold, pt4p_hold]
    
    node_dict = {}
    for ele in t_list:
        node_dict[ele.id] = ele

    for ele in p_list:
        node_dict[ele.id] = ele

    return p_list, t_list, node_dict