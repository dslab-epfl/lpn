
from lpnlang import Place, Transition, Token
from lpnlang import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from lpnlang import prop_value 
from lpn_def.funcs import *
from typing import List, Dict

"""
this is a fair arbiter, not considering arriving order
"""
take_0_or_1 = InWeightFunc(f"arbiterhelper_take_0_or_1", my_idx=int, list_of_buf=List[Place], pidx=Place)
@take_0_or_1.install    
def weight(binding, my_idx, list_of_buf, pidx):
    total = len(list_of_buf)
    tk_status = list()
    for p in list_of_buf:
        tk_status.append(prop_value(binding, p, None, "tk_len"))
    cur_turn = prop_value(binding, pidx, 0, "idx")
    _l = list()
    for i in range(cur_turn, total):
        _l.append(i)

    for i in range(0, cur_turn):
        _l.append(i)

    earliest_enabled_idx = -1
    for i in _l:
        if tk_status[i] > 0:
            earliest_enabled_idx = i
            break
    if earliest_enabled_idx == -1:
        if cur_turn == my_idx:
            # to prevent anything happening
            return 1
        else:
            return 0
    else:
        if earliest_enabled_idx == my_idx:
            return 1
        else:
            return 0

update_cur_turn = OutWeightFunc("arbiterhelper_update_cur_turn", pidx=Place, list_of_buf=List[Place])
@update_cur_turn.install
def output_tokens(binding, output_place, pidx, list_of_buf):
    total = len(list_of_buf)
    tk_status = list()
    for p in list_of_buf:
        tk_status.append(prop_value(binding, p, None, "tk_len"))
    cur_turn = prop_value(binding, pidx, 0, "idx")
    next_turn = cur_turn
    _l = list()
    for i in range(cur_turn, total):
        _l.append(i)

    for i in range(0, cur_turn):
        _l.append(i)

    for i in _l:
        if tk_status[i] > 0:
            next_turn = (i+1)%total
            break
    output_place.push_token(Token({"idx": next_turn}))

pass_turn_token = OutWeightFunc("arbiterhelper_pass_turn_token", pidx=Place, list_of_buf=List[Place])
@pass_turn_token.install
def output_tokens(binding, output_place, pidx, list_of_buf):
    total = len(list_of_buf)
    tk_status = list()
    for p in list_of_buf:
        tk_status.append(prop_value(binding, p, None, "tk_len"))
    cur_turn = prop_value(binding, pidx, 0, "idx")
    _l = list()
    for i in range(cur_turn, total):
        _l.append(i)
    for i in range(0, cur_turn):
        _l.append(i)

    cur_buf = list_of_buf[0]
    for i in _l:
        if tk_status[i] > 0:
            cur_buf = list_of_buf[i]
            break
    token = cur_buf.tokens[0]
    output_place.push_token(token)

def arbiterHelper(id, list_of_buf, list_of_buf_cap, out_buf, out_buf_cap):
    total = len(list_of_buf)
    pidx = Place(f"{id}_pidx")
    pidx.assign_marking(deque([Token({"idx":0})]))

    pass_turn_empty_token = OutWeightFunc("arbiterhelper_pass_turn_empty_token", pidx=Place, idx=int, list_of_buf=List[Place])
    @pass_turn_empty_token.install
    def output_tokens(binding, output_place, pidx, idx, list_of_buf):
        total = len(list_of_buf)
        tk_status = list()
        for p in list_of_buf:
            tk_status.append(prop_value(binding, p, None, "tk_len"))
        cur_turn = prop_value(binding, pidx, 0, "idx")
        _l = list()
        for i in range(cur_turn, total):
            _l.append(i)
        for i in range(0, cur_turn):
            _l.append(i)
        earliest_enabled_idx = -1
        for i in _l:
            if tk_status[i] > 0:
                earliest_enabled_idx = i
                break
        if earliest_enabled_idx == idx:
            output_place.push_token(Token())

    arbiter = Transition(
        id=f"{id}_arbiter",
        delay_func=con_delay(0),
        pi=[pidx, out_buf_cap, *list_of_buf],
        pi_w=[take_1_token(), take_1_token(), *[take_0_or_1(idx, list_of_buf, pidx) for idx in range(total)] ], 
        po=[pidx, out_buf, *list_of_buf_cap],
        po_w=[update_cur_turn(pidx, list_of_buf), pass_turn_token(pidx, list_of_buf), *[pass_turn_empty_token(pidx, idx, list_of_buf) for idx in range(total)] ],
    )
    
    return arbiter


"""
this is an arbiter based on ordering, the order is provided explictly
"""
def arbiterWTimeOrdHelper(id, list_of_buf, list_of_buf_cap, out_buf, out_buf_cap, porder_keeper):
    total = len(list_of_buf)
    take_0_or_1 = InWeightFunc(f"arbiterhelperord_take_0_or_1", my_idx=int, porder_keeper=Place)
    @take_0_or_1.install    
    def weight(binding, my_idx, porder_keeper):
        cur_turn = prop_value(binding, porder_keeper, 0, "idx")
        if cur_turn == my_idx:
            return 1
        else:
            return 0

    pass_turn_token = OutWeightFunc("arbiterhelperord_pass_turn_token", porder_keeper=Place, list_of_buf=List[Place])
    @pass_turn_token.install
    def output_tokens(binding, output_place, porder_keeper, list_of_buf):
        cur_turn = prop_value(binding, porder_keeper, 0, "idx")
        cur_buf = list_of_buf[cur_turn]
        token = cur_buf.tokens[0]
        output_place.push_token(token)

    pass_turn_empty_token = OutWeightFunc("arbiterhelperord_pass_turn_empty_token", porder_keeper=Place, idx=int)
    @pass_turn_empty_token.install
    def output_tokens(binding, output_place, porder_keeper, idx):
        cur_turn = prop_value(binding, porder_keeper, 0, "idx")
        if cur_turn == idx:
            output_place.push_token(Token())

    arbiter = Transition(
        id = f"{id}_arbiter",
        delay_func=con_delay(0),
        pi=[porder_keeper, out_buf_cap, *list_of_buf],
        pi_w=[take_1_token(), take_1_token(), *[take_0_or_1(idx, porder_keeper) for idx in range(total)] ], 
        po=[out_buf, *list_of_buf_cap],
        po_w=[pass_turn_token(porder_keeper, list_of_buf), *[pass_turn_empty_token(porder_keeper, idx) for idx in range(total)] ],
    )
    
    return arbiter


"""
this is a fair arbiter with no capacity consideration, not considering arriving order
"""
def arbiterHelperNoCap(id, list_of_buf, out_buf):
    total = len(list_of_buf)
    pidx = Place(f"{id}_pidx")
    pidx.assign_marking(deque([Token({"idx":0})]))
     
    arbiter = Transition(
        f"{id}_arbiter",
        delay_func=con_delay(0),
        pi=[pidx, *list_of_buf],
        pi_w=[take_1_token(), *[take_0_or_1(idx, list_of_buf, pidx) for idx in range(total)] ], 
        po=[pidx, out_buf],
        po_w=[update_cur_turn(pidx, list_of_buf), pass_turn_token(pidx, list_of_buf)],
    )
    
    return arbiter


"""
this is a fair arbiter with no capacity consideration, not considering arriving order
"""
def arbiterHelperNoCapWPort(id, list_of_buf, in_post_list, out_buf):
    total = len(list_of_buf)
    pidx = Place(f"{id}_pidx")
    pidx.assign_marking(deque([Token({"idx":0})]))
        
    pass_turn_token = OutWeightFunc("arbiterhelpernocapwport_pass_turn_token", pidx=Place, list_of_buf=List[Place], in_post_list=List[int])
    @pass_turn_token.install
    def output_tokens(binding, output_place, pidx, list_of_buf, in_post_list):
        total = len(list_of_buf)
        tk_status = list()
        for p in list_of_buf:
            tk_status.append(prop_value(binding, p, None, "tk_len"))
        cur_turn = prop_value(binding, pidx, 0, "idx")
        _l = list()
        for i in range(cur_turn, total):
            _l.append(i)

        for i in range(0, cur_turn):
            _l.append(i)

        cur_buf = list_of_buf[0]
        cur_port = 0
        for i in _l:
            if tk_status[i] > 0:
                cur_buf = list_of_buf[i]
                cur_port = in_post_list[i]
                break
        token = Token({
            "device": prop_value(binding, cur_buf, 0, "device"),
            "req": prop_value(binding, cur_buf, 0, "req"),
            "cmpl": prop_value(binding, cur_buf, 0, "cmpl"),
            "from": prop_value(binding, cur_buf, 0, "from"),
            "port": cur_port
        })
        output_place.push_token(token)


    arbiter = Transition(
        id=f"{id}_arbiter",
        delay_func=con_delay(0),
        pi=[pidx, *list_of_buf],
        pi_w=[take_1_token(), *[take_0_or_1(idx, list_of_buf, pidx) for idx in range(total)] ], 
        po=[pidx, out_buf],
        po_w=[update_cur_turn(pidx, list_of_buf), pass_turn_token(pidx, list_of_buf, in_post_list)],
    )
    
    return arbiter


pass_type_idx = OutWeightFunc("pass_type_idx", buf_map=Dict[int, int], type_enum=int)
@pass_type_idx.install
def output_tokens(binding, output_place, buf_map, type_enum):
    output_place.push_token(Token({"idx": buf_map[type_enum]}))