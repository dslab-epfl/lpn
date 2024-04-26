import uuid
from collections import deque
from lpnlang import Place, Token, prop_value, get_token
from lpnlang import InWeightFunc, OutWeightFunc, DelayFunc

'not lpn function, so dont care'
def create_empty_tokens(num):
    tokens = deque()
    for i in range(num):
        token = Token()
        tokens.append(token)
    return tokens

con_edge = InWeightFunc("con_edge", number=int)
@con_edge.install
def weight(binding, number):
    return number

con_tokens = OutWeightFunc("con_tokens", number=int)
@con_tokens.install
def output_tokens(binding, output_place, number):
    for i in range(number):
        output_place.push_token(Token())

gact_delay = DelayFunc("gact_delay", from_place=Place)
@gact_delay.install
def delay(binding, from_place):
    NUM_PE = 4
    ref_len = prop_value(binding, from_place, 0, "ref_len")
    qry_len = prop_value(binding, from_place, 0, "query_len")
    steps = prop_value(binding, from_place, 0, "steps")
    return (ref_len+NUM_PE+2)*qry_len / NUM_PE + NUM_PE+2+3*steps