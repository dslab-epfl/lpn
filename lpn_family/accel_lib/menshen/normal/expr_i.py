from lpnlang import InWeightFunc
from lpnlang import Place, prop_value

take_1_token = InWeightFunc("take_1_token")
@take_1_token.install
def number_of_token(binding):
    return 1

take_token_if_queue = InWeightFunc("take_token_if_queue", counter_place=Place, index=int)
@take_token_if_queue.install
def number_of_token(binding, counter_place, index):
    cnt = prop_value(binding, counter_place, 0, "cnt")
    if cnt == index:
        return 1
    else:
        return 0
