from collections import deque
from typing import List
from lpnlang import Token, OutWeightFunc, prop_value, get_token
from lpnlang import Place

pass_inc_cnt = OutWeightFunc("pass_inc_cnt", counter_place=Place, max_val=int)
@pass_inc_cnt.install
def output_token(binding, output_place, counter_place, max_val):
    # bounded variables:
    cnt = prop_value(binding, counter_place, 0, "cnt")
    cnt = (cnt + 1) % max_val
    output_place.push_token(Token({"cnt": cnt}))

pass_token_if_index = OutWeightFunc("pass_token_if_index", from_place=Place, counter_place=Place, index=int)
@pass_token_if_index.install
def output_token(binding, output_place, from_place, counter_place, index):
    # bounded variables:
    cnt = prop_value(binding, counter_place, 0, "cnt")
    if cnt == index:
        tk = get_token(binding, from_place, 0)
        output_place.push_token(tk) 


pass_token_from_multi_input = OutWeightFunc("pass_token_from_multi_input", from_place_array=List[Place], counter_place=Place)
@pass_token_from_multi_input.install
def output_token(binding, output_place, from_place_array, counter_place):
    # bounded variables:
    cnt = prop_value(binding, counter_place, 0, "cnt")
    queue = from_place_array[cnt]
    tk = get_token(binding, queue, 0)
    output_place.push_token(tk)

pass_drop_or_control_token = OutWeightFunc("pass_drop_or_control_token", from_place=Place)
@pass_drop_or_control_token.install
def output_token(binding, output_place, from_place):
    # bounded variables:
    drop = prop_value(binding, from_place, 0, "is_drop")
    control = prop_value(binding, from_place, 0, "is_control")
    if drop == 1 or control == 1:
        output_place.push_token(Token())

pass_data_token = OutWeightFunc("pass_data_token", from_place=Place)
@pass_data_token.install
def output_token(binding, output_place, from_place):
    # bounded variables:
    drop = prop_value(binding, from_place, 0, "is_drop")
    control = prop_value(binding, from_place, 0, "is_control")
    if not (drop == 1 or control == 1):
        tk = get_token(binding, from_place, 0)
        output_place.push_token(tk)

pass_token = OutWeightFunc("pass_token", from_place=Place, num=int)
@pass_token.install
def output_token(binding, output_place, from_place, num):
    # bounded variables:
    for i in range(num):
        tk = get_token(binding, from_place, i)
        output_place.push_token(tk)

pass_empty_token = OutWeightFunc("pass_empty_token")
@pass_empty_token.install
def output_token(binding, output_place):
    output_place.push_token(Token())
