from lpnlang import Transition
from .funcs import *
from .places import *

t2p = Transition(
    id="t2p", 
    delay_func=constant_func(0), 
    pi=[p0, p20, p6, pt2p_hold], 
    po=[pt2p, p6], 
    pi_w=[c1,  c1,  c2, c1], 
    po_w=[ct1, ct2] 
)

t3p = Transition(
    id="t3p", 
    delay_func=constant_func(0), 
    pi=[p0, p21, p6, pt3p_hold], 
    po=[pt3p, p6], 
    pi_w=[c1,  c4,  c2, c1], 
    po_w=[ct1, ct2] 
)

t4p = Transition(
    id="t4p", 
    delay_func=constant_func(0), 
    pi=[p0, p22, p6, pt4p_hold], 
    po=[pt4p, p6], 
    pi_w=[c1,  c1,  c2, c1], 
    po_w=[ct1, ct2] 
)

t2 = Transition(
    id="t2", 
    delay_func=constant_func(66), 
    pi=[pt2p], 
    po=[p1, p21, p4, pt2p_hold], 
    pi_w=[c1], 
    po_w=[ct1, ct1, ct1, ct1] 
)

t3 = Transition(
    id="t3", 
    delay_func=constant_func(66), 
    pi=[pt3p], 
    po=[p2, p22, p4, pt3p_hold], 
    pi_w=[c1], 
    po_w=[ct4,  ct1, ct1, ct1]
)

t4 = Transition(
    id="t4", 
    delay_func=constant_func(66), 
    pi=[pt4p, p6], 
    po=[p3, p20, p4, pt4p_hold], 
    pi_w=[c1, c4], 
    po_w=[ct4,  ct4, ct1, ct1]
)

t5 = Transition(
    id="t5", 
    delay_func=constant_func(65), 
    pi=[p1, p2, p3], 
    po=[pdone, p5, p6], 
    pi_w=[c1, c1, c1], 
    po_w=[ct1, ct1, ct1]
)

t0 = Transition(
    id="t0", 
    delay_func=mcu_delay(pvarlatency), 
    pi=[p7, p4, pvarlatency], 
    po=[p0, p8], 
    pi_w=[c1, c1, c1], 
    po_w=[ct1, ct1]
)

t1 = Transition(
    id="t1", 
    delay_func=constant_func(0), 
    pi=[ptasks, p8], 
    po=[p7, pstart], 
    pi_w=[c1, c1], 
    po_w=[ct1, ct1]
)
 

