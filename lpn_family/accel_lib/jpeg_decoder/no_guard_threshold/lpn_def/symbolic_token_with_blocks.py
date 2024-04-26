from collections import deque
from lpnlang import Place, Transition, Token
from lpnlang import createIntSymbol
from .funcs import *
from .transitions import *
from .places import *

COUNTER = 0
def symbolic_token_with_blocks(blocks):
    tokens_dict = {}
    tks = deque()
    for i in range(blocks):
        global COUNTER
        tks.append(Token({"nonzero": createIntSymbol(1, 0, 63, f"SYMREF{COUNTER}")}))
        COUNTER += 1
    tokens_dict[pvarlatency.id] = tks
    return tokens_dict