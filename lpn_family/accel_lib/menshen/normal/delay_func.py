from lpnlang import Place
from lpnlang import DelayFunc, prop_value
from typing import List
from .all_enums import CstStr


const_pip = DelayFunc("const_pip", constant=int)
@const_pip.install
def pip(binding, constant):
    return constant 

con_delay = DelayFunc("con_delay", constant=int)
@con_delay.install
def delay(binding, constant):
    return constant

fifo_delay_func = DelayFunc("fifo_delay_func")
@fifo_delay_func.install
def delay(binding):
    return CstStr.FIFO_Delay

pkt_filter_delay = DelayFunc("pkt_filter_delay", from_place=Place)
@pkt_filter_delay.install
def delay(binding, from_place):
    n_words = prop_value(binding, from_place, 0, "n_words")
    # The +1 is because the state machine must come back to its IDLE state.
    # return n_words + 1
    return n_words+2

parser_get_segs_delay = DelayFunc("parser_get_segs_delay", from_place=Place)
@parser_get_segs_delay.install
def delay(binding, from_place):
    n_words = prop_value(binding, from_place, 0, "n_words")
    # state_machine_delay = 0
    # if n_words == 1:
    #     state_machine_delay = 1
    # else:
    #     state_machine_delay = 2
    # The +1 is because the state machine must come back to its IDLE state.
    # return state_machine_delay + 1
    return 3

multi_queue_n_delay_func = DelayFunc("multi_queue_n_delay_func", counter_place=Place, array_of_queue=List[Place])
@multi_queue_n_delay_func.install
def delay(binding, counter_place, array_of_queue):
    queue_id = prop_value(binding, counter_place, 0, "cnt")
    'attention, translation might fail'
    place = array_of_queue[queue_id]
    n_words = prop_value(binding, place, 0, "n_words")
    # The +1 is because the state machine must come back to its IDLE state.
    return n_words + 1

multi_queue_n_plus_f_delay = DelayFunc("multi_queue_n_plus_f_delay", counter_place=Place, array_of_queue=List[Place])
@multi_queue_n_plus_f_delay.install
def delay(binding, counter_place, array_of_queue):
    queue_id = prop_value(binding, counter_place, 0, "cnt")
    'attention, translation might fail'
    place = array_of_queue[queue_id]
    n_words = prop_value(binding, place, 0, "n_words")
    # The +1 is because the state machine must come back to its IDLE state.
    return n_words + CstStr.FIFO_Delay + 1

n_words_delay = DelayFunc("n_words_delay", from_place=Place)
@n_words_delay.install
def delay(binding, from_place):
    n_words = prop_value(binding, from_place, 0, "n_words")
    return n_words-1

exact_n_words_delay = DelayFunc("exact_n_words_delay", from_place=Place)
@exact_n_words_delay.install
def delay(binding, from_place):
    n_words = prop_value(binding, from_place, 0, "n_words")
    return n_words