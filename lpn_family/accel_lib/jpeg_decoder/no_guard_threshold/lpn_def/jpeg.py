import uuid
from parameters import *
import lpn2smt.z3_util as z3_util
from collections import deque
from place_transition import Place, Transition, Token, IntSymbol
from lpn2smt.verify_place import VPlace
from lpn2smt.verify_transition import VTransition
import random
from parameters import *

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

    var_63_64 = 64
    cap = 4 
    # pt 
    def create_empty_tokens(num):
        tokens = deque()
        for i in range(num):
            token = Token()
            token.t = 0
            tokens.append(token)
        return tokens

    ptasks = VPlace("ptasks", create_empty_tokens(tasks_number*6//4))
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
    pstall = VPlace("pstall", create_empty_tokens(4))
    
    p7 = VPlace("p7")
    p8 = VPlace("p8", create_empty_tokens(1))
    p10 = VPlace("p10")
    # p11 = VPlace("p11", create_empty_tokens(4))
    p20 = VPlace("p20", create_empty_tokens(4))
    # p20.cap_node = True
    
    p21 = VPlace("p21")
    p22 = VPlace("p22")
    pdone = VPlace("pdone")

    pvarlatency = VPlace("pvarlatency")
    pvarlatency.type_annotations = ["delay"]
    delay_list = [8,8,125,67,8,49,8,8,67,8,8,198,66,49,8,8,8,8,197,68,8,8,49,67,197,67,67,67,8,8,51,198,8,125,8,8]
    delay_list = [200, 200, 66,8,50,8,200,194,66,66,66,8]
    delay_list = [143, 198,198, 197, 51, 8,8,8,8, 200,198,200,200,199,199,200, 8, 8, 8, 8, 8, 8, 8,8, 8, 8, 8, 8, 8, 8,8, 8, 8, 8]
    for i in range(tasks_number*6//4):
        global COUNTER
        # d = random.randint(8, 216)
        d = delay_list[COUNTER%len(delay_list)]
        d = 10
        value_list.append(d)
        # symbol = IntSymbol(d, symref=f"SYMREF{COUNTER}", z3range=(9, 195), z3varname=f"z3_delay{COUNTER}" )
        symbol = IntSymbol(d, symref=f"SYMREF{COUNTER}", z3range=(9, 195))
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
            return binding["pvarlatency.0.delay"].concrete()
        return delay

    
    # without threshold
    # PIP = 0
    # t2 = VTransition("t2", constant_func(66), pi=[p0, p20], po=[p1, p21, p4], pi_w=[c1,  c1], po_w=[ct1,  ct1, ct1], pip=PIP )
    # t3 = VTransition("t3", constant_func(66), pi=[p0, p21], po=[p2, p22, p4], pi_w=[c1,  c4], po_w=[ct4,  ct1, ct1], pip=PIP )
    # t4 = VTransition("t4", constant_func(66), pi=[p0, p22], po=[p3, p20, p4], pi_w=[c1,  c1], po_w=[ct4,  ct4, ct1], pip=PIP )
    # t5 = VTransition("t5", constant_func(65), pi=[p1, p2, p3], po=[pdone], pi_w=[c1, c1, c1], po_w=[ct1], pip=PIP )
    # t0 = VTransition("t0", mcu_delay(), pi=[p7, p4, pvarlatency], po=[p0, p8], pi_w=[c1, c1, c1], po_w=[ct1, ct1], pip=PIP )
    # t1 = VTransition("t1", constant_func(0), pi=[ptasks, p8], po=[p7, pstart], pi_w=[c1, c1], po_w=[ct1, ct1], pip=PIP )
    
    # with threshold

    t2 = VTransition("t2", constant_func(66), pi=[p0, p20, p6], po=[p1, p21, p4], pi_w=[c1,  c1,  c0], pi_w_threshold=[0, 0,  2], po_w=[ct1,  ct1, ct1])
    t3 = VTransition("t3", constant_func(66), pi=[p0, p21, p6], po=[p2, p22, p4], pi_w=[c1,  c4,  c0], pi_w_threshold=[0, 0,  2], po_w=[ct4,  ct1, ct1])
    t4 = VTransition("t4", constant_func(66), pi=[p0, p22, p6], po=[p3, p20, p4], pi_w=[c1,  c1,  c4], pi_w_threshold=[0, 0,  2], po_w=[ct4,  ct4, ct1])
    t5 = VTransition("t5", constant_func(65), pi=[p1, p2, p3], po=[pdone, p5, p6], pi_w=[c1, c1, c1], po_w=[ct1, ct1, ct1])
    t0 = VTransition("t0", mcu_delay(), pi=[p7, p4, pvarlatency], po=[p0, p8], pi_w=[c1, c1, c1], po_w=[ct1, ct1])
    t1 = VTransition("t1", constant_func(0), pi=[ptasks, p8], po=[p7, pstart], pi_w=[c1, c1], po_w=[ct1, ct1])

    # PIP = -1
    # t2 = VTransition("t2", constant_func(66), pi=[p0, p20, pstall], po=[p1, p21, p4], pi_w=[c1,  c1, c1], po_w=[ct1,  ct1, ct1], pip=PIP )
    # t3 = VTransition("t3", constant_func(66), pi=[p0, p21], po=[p2, p22, p4], pi_w=[c1,  c4], po_w=[ct4,  ct1, ct1], pip=PIP )
    # t4 = VTransition("t4", constant_func(66), pi=[p0, p22], po=[p3, p20, p4], pi_w=[c1,  c1], po_w=[ct4,  ct4, ct1], pip=PIP )
    
    # t5 = VTransition("t5", constant_func(130), pi=[p1, p2, p3], po=[pstall, pdone], pi_w=[c2, c2, c2], po_w=[ct2, ct2], pip=PIP)

    # t0 = VTransition("t0", mcu_delay(), pi=[p7, p4, pvarlatency], po=[p0, p8], pi_w=[c1, c1, c1], po_w=[ct1, ct1], pip=PIP )
    # t1 = VTransition("t1", constant_func(0), pi=[ptasks, p8], po=[p7, pstart], pi_w=[c1, c1], po_w=[ct1, ct1], pip=PIP )

    t_list = [t0, t1, t2, t3, t4, t5]
    # t_list = [t0, t2, t3, t4]
    # t_list = [t0, t1]
    # t_list = [t0, t1]
    p_list = [ptasks, pstart, pdone, p0, p1, p2, p3, p4, p5, p6, p7, p8, p20,p21,p22, pvarlatency, pstall]
    
    node_dict = {}
    for ele in t_list:
        node_dict[ele.id] = ele

    for ele in p_list:
        node_dict[ele.id] = ele

    return p_list, t_list, node_dict