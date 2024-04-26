from lpnlang import Transition
from .funcs import *
from .places import *

t0 = Transition(
    id = 't0',
    delay_func = gact_delay(ptasks),
    pi = [ptasks],
    po = [pdone],
    pi_w = [con_edge(1)],
    po_w = [con_tokens(1)],
)