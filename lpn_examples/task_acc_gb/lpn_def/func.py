from collections import deque
from lpnlang import Place, Transition, Token
from lpnlang import Place, Token, prop_value, get_token
from lpnlang import InWeightFunc, OutWeightFunc, DelayFunc, ThresholdFunc, OutWeightFuncA
from DMA.lpn_def.dma_ports import *
from jpeg_dma.lpn_def.func import *
from jpeg_dma.lpn_def.mem_func import *
from task_acc_gb.lpn_def.all_enum import CstStr
import typing

# We define a global ID generator for polynomials:
def unique_pair_id(a: int, b: int) -> int:
    """Generate a unique ID for an unordered pair (a, b) using Cantor's pairing function."""
    a, b = min(a, b), max(a, b)  # Ensure (a, b) is always ordered
    return (a + b) * (a + b + 1) // 2 + b + 10000

process_state_req = OutWeightFuncA("process_state_req", req_buf=Place, state_store=typing.Dict[int, int], inc_only_state=int)
@process_state_req.install
def output_tokens(binding, output_places, req_buf, state_store, inc_only_state):
    requester = prop_value(binding, req_buf, 0, "requester")
    resp_buf = output_places[requester]
    state_id = prop_value(binding, req_buf, 0, "state_id")
    rd_or_wr = prop_value(binding, req_buf, 0, "rd_or_wr")
    state_data = prop_value(binding, req_buf, 0, "state_data")
    found = False
    if state_id in state_store:
        found = True
        if rd_or_wr == CstStr.READ:
            state_data = state_store[state_id]
        if rd_or_wr == CstStr.WRITE:
            # updates can't be reversed
            if inc_only_state and state_store[state_id] > state_data:
                pass
            else:
                state_store[state_id] = state_data
    
    if not found:
        if rd_or_wr == CstStr.WRITE:
            if False: #state_store.capacity == state_store.size:
                # can't insert more
                # return None, indicate failure
                state_data = None
            else:
                state_store[state_id] = state_data 

        if rd_or_wr == CstStr.READ:
            state_data = None

    piggyback = len(state_store)
    resp_buf.push_token(
        Token({
        "requester": requester,
        "state_id": state_id,
        "rd_or_wr": rd_or_wr,
        "state_data": state_data,
        "piggyback": piggyback})
    )

process_state_req_multi = OutWeightFuncA("process_state_req_multi", from_place=Place, state_store_dict=typing.Dict[int, typing.Dict], inc_only_state=int)
@process_state_req_multi.install
def output_tokens(binding, output_places, req_buf, state_store_dict, inc_only_state):
    requester = prop_value(binding, req_buf, 0, "requester")
    resp_buf = output_places[requester]
    store_id = prop_value(binding, req_buf, 0, "store_id")
    state_id = prop_value(binding, req_buf, 0, "state_id")
    rd_or_wr = prop_value(binding, req_buf, 0, "rd_or_wr")
    state_data = prop_value(binding, req_buf, 0, "state_data")
    state_store = state_store_dict[store_id]
    found = False
    if state_id in state_store:
        found = True
        if rd_or_wr == CstStr.READ:
            state_data = state_store[state_id]
        if rd_or_wr == CstStr.WRITE:
            if inc_only_state and state_store[state_id] > state_data:
                pass
            else:
                state_store[state_id] = state_data
 
    if not found:
        if rd_or_wr == CstStr.WRITE:
            if False: #state_store.capacity == state_store.size:
                # can't insert more
                # return None, indicate failure
                state_data = None
            else:
                state_store[state_id] = state_data 

        if rd_or_wr == CstStr.READ:
            state_data = None

    piggyback = len(state_store)
    resp_buf.push_token(
        Token({
        "requester": requester,
        "store_id": store_id,
        "state_id": state_id,
        "rd_or_wr": rd_or_wr,
        "state_data": state_data,
        "piggyback": piggyback})
    )

exam_task_generator = OutWeightFuncA("exam_task_generator", best_performing=Place, generator=Place, path_stats_resp=Place, path_store=Place)
@exam_task_generator.install
def output_tokens(binding, output_places, best_performing, generator, path_stats_resp, path_store):
    bf_state_data = prop_value(binding, path_stats_resp, 0, "state_data")
    ge_state_data = prop_value(binding, path_stats_resp, 1, "state_data")

    # bf_stats1 = bf_state_data[0]
    # bf_stats2 = bf_state_data[1]
    # ge_stats1 = ge_state_data[0]
    # ge_stats2 = ge_state_data[1]

    # kill = True
    # if bf_stats1 == 0:
    #     kill = False

    # elif ge_stats1 > bf_stats1 and ge_stats2 > bf_stats2:
    #     kill = True 

    kill = False

    if not kill:        
        token = get_token(binding, generator, 0)
        output_places[0].push_token(token)
    else:
        if prop_value(binding, path_store, 0, "tk_len") > 0:
            'fetch a new path'
            output_places[3].push_token(Token())

    # replace = False
    # if ge_stats1 < bf_stats1 and ge_stats2 < bf_stats2:
    #     replace = True 
    replace = False
    if replace:        
        token = get_token(binding, generator, 0)
        output_places[1].push_token(token)
    else:
        'restore original token'
        token = get_token(binding, best_performing, 0)
        output_places[1].push_token(token)

    'ctrl token'
    output_places[2].push_token(Token())

read_poly_states = OutWeightFuncA("read_poly_states", buf=Place)
@read_poly_states.install
def output_tokens(binding, output_places, buf):
    path_id = prop_value(binding, buf, 0, "path_id")
    gen_type = prop_value(binding, buf, 0, 'gen_type')
    if gen_type == CstStr.SPOLY_GEN:
        poly_1_id = prop_value(binding, buf, 0, 'gen_arg1')
        poly_2_id = prop_value(binding, buf, 0, 'gen_arg2')
        stage = prop_value(binding, buf, 0, 'gen_arg3')
        if stage == 0 or stage == 1 or stage == 2:
            output_places[0].push_token(
                Token({
                    "store_id": path_id,
                    "state_id": poly_1_id,
                    "rd_or_wr": CstStr.READ,
                    "state_data": None,
                    "piggyback": None})
            )
            output_places[0].push_token(
                Token({
                    "store_id": path_id,
                    "state_id": poly_2_id,
                    "rd_or_wr": CstStr.READ,
                    "state_data": None,
                    "piggyback": None})
            )
            output_places[1].push_token(
                Token({
                    "num": 2})
            )
        else:
            'poly_1_id is the new_poly_id'
            output_places[0].push_token(
                Token({
                    "store_id": path_id,
                    "state_id": poly_1_id,
                    "rd_or_wr": CstStr.READ,
                    "state_data": None,
                    "piggyback": None})
            )
            output_places[1].push_token(
                Token({
                    "num": 1})
            )
    elif gen_type == CstStr.SPOLY_GEN_GEN:
        pair_poly_id = prop_value(binding, buf, 0, 'gen_arg2')
        output_places[0].push_token(
            Token({
                "store_id": path_id,
                "state_id": pair_poly_id,
                "rd_or_wr": CstStr.READ,
                "state_data": None,
                "piggyback": None})
        )
        output_places[1].push_token(
            Token({
                "num": 1})
        )
    else:
        output_places[1].push_token(
            Token({
                "num": 0})
        )

take_requested_token = InWeightFunc("take_requested_token", buf=Place)
@take_requested_token.install
def input_tokens(binding, buf):
    num = prop_value(binding, buf, 0, "num")
    return num
     
new_generators = OutWeightFuncA("new_generators", buf=Place, poly_store_resp=Place, func_sim_trace=typing.Dict[int, typing.Dict])
@new_generators.install
def output_tokens(binding, output_places, buf, poly_store_resp, func_sim_trace):
    
    task_generator_buffer, pe_task_buffer, poly_store, num_poly_store, ctrl = output_places

    path_id = prop_value(binding, buf, 0, "path_id")
    wait_for_ctrl = False
    num_poly_update = 0
    gen_type = prop_value(binding, buf, 0, 'gen_type')
    if gen_type == CstStr.SPOLY_GEN:
        poly_1_id = prop_value(binding, buf, 0, 'gen_arg1')
        poly_2_id = prop_value(binding, buf, 0, 'gen_arg2')
        stage = prop_value(binding, buf, 0, 'gen_arg3')
        poly_cnt = prop_value(binding, poly_store_resp, 0, "piggyback")
        # stage counter
        # 0: setup, 1: reorder, 2:sort, 3: spoly, 4:reduce
        if stage == 0:
            poly_1_state = prop_value(binding, poly_store_resp, 0, "state_data")
            poly_2_state = prop_value(binding, poly_store_resp, 1, "state_data")

            print(f"stage 0, poly1 id:{poly_1_id}, value:{poly_1_state}, poly2 id:{poly_2_id}, value:{poly_2_state}")
            assert(poly_1_state != None and poly_2_state != None)

            task_generator_buffer.push_token(
                Token({
                    "path_id": path_id, 
                    "gen_type": CstStr.SPOLY_GEN,
                    "gen_arg1": poly_1_id,
                    "gen_arg2": poly_2_id,
                    "gen_arg3": 1})
            )
            if poly_1_state == CstStr.INITIAL or poly_2_state == CstStr.INITIAL:
                # keep intermediate states
                if poly_1_state == CstStr.INITIAL:
                    reorder_task = Token(
                        {"path_id": path_id, 
                        "task_type": CstStr.REORDER, 
                        "cond": None, # already met
                        "task_arg1": poly_1_id, 
                        "task_arg2": None, 
                        "task_arg3": None}
                    )
                    pe_task_buffer.push_token(reorder_task)
                if poly_2_state == CstStr.INITIAL:
                    reorder_task = Token(
                        {"path_id": path_id, 
                        "task_type": CstStr.REORDER, 
                        "cond": None, # already met
                        "task_arg1": poly_2_id, 
                        "task_arg2": None, 
                        "task_arg3": None}
                    )
                    pe_task_buffer.push_token(reorder_task)
            
        if stage == 1:
            poly_1_state = prop_value(binding, poly_store_resp, 0, "state_data")
            poly_2_state = prop_value(binding, poly_store_resp, 1, "state_data")
            print(f"stage 1, poly1 id:{poly_1_id}, value:{poly_1_state}, poly2 id:{poly_2_id}, value:{poly_2_state}")
            if poly_1_state >= CstStr.REORDERED and poly_2_state >= CstStr.REORDERED:
                token = Token({
                    "path_id": path_id, 
                    "gen_type": CstStr.SPOLY_GEN,
                    # task reference
                    "gen_arg1": poly_1_id,
                    "gen_arg2": poly_2_id,
                    "gen_arg3": 2}
                )
                task_generator_buffer.push_token(token)

                if poly_1_state == CstStr.REORDERED:
                    #generate new pe tasks
                    sort_task1 = Token(
                        {"path_id": path_id, 
                        "task_type": CstStr.SORT, 
                        "cond": None, # already met
                        "task_arg1": poly_1_id, 
                        "task_arg2": None, 
                        "task_arg3": None}
                    )
                    pe_task_buffer.push_token(sort_task1)

                if poly_2_state == CstStr.REORDERED:
                    #generate new pe tasks
                    sort_task2 = Token(
                        {"path_id": path_id, 
                        "task_type": CstStr.SORT, 
                        "cond": None, # already met
                        "task_arg1": poly_2_id, 
                        "task_arg2": None, 
                        "task_arg3": None}
                    )
                    pe_task_buffer.push_token(sort_task2)
            else:
                # condition not met
                task_generator_buffer.push_token(get_token(binding, buf, 0))

        if stage == 2:
            poly_1_state = prop_value(binding, poly_store_resp, 0, "state_data")
            poly_2_state = prop_value(binding, poly_store_resp, 1, "state_data")
            print(f"stage 2, poly1 id:{poly_1_id}, value:{poly_1_state}, poly2 id:{poly_2_id}, value:{poly_2_state}")
            if poly_1_state >= CstStr.SORTED and poly_2_state >= CstStr.SORTED:
                'id starts from 0'
                new_poly_id = func_sim_trace[path_id]["get_id"][unique_pair_id(poly_1_id, poly_2_id)]
                print("new poly id", new_poly_id)
                token = Token({
                    "path_id": path_id, 
                    "gen_type": CstStr.SPOLY_GEN,
                    # task reference
                    "gen_arg1": new_poly_id,
                    # stage counter, 0: reorder, 1: sort, 2: spoly, 3: reduce
                    "gen_arg2": None,
                    "gen_arg3": 3}
                )
                task_generator_buffer.push_token(token)

                new_poly_token = Token({
                    "store_id": path_id,
                    "state_id": new_poly_id,
                    "rd_or_wr": CstStr.WRITE,
                    "state_data": CstStr.EMPTY,
                    "piggyback": None}
                )

                poly_store.push_token(new_poly_token)
                wait_for_ctrl = True
                num_poly_update += 1
                #generate new pe tasks
                spoly_task = Token(
                    {"path_id": path_id, 
                    "task_type": CstStr.SPOLY, 
                    "cond": None, # already met
                    "task_arg1": new_poly_id, 
                    "task_arg2": poly_1_id, 
                    "task_arg3": poly_2_id}
                )
                pe_task_buffer.push_token(spoly_task)

            else:
                # conditional not met
                task_generator_buffer.push_token(get_token(binding, buf, 0))

        if stage == 3:
            new_poly_id = prop_value(binding, buf, 0, 'gen_arg1')
            new_poly_state = prop_value(binding, poly_store_resp, 0, "state_data")
            print(f"stage 3, new poly id:{new_poly_id}, value:{new_poly_state}")
            if new_poly_state == CstStr.SPOLIED:
                token = Token({
                    "path_id": path_id, 
                    "gen_type": CstStr.SPOLY_GEN,
                    # task reference
                    "gen_arg1": new_poly_id,
                    # stage counter, 0: reorder, 1: sort, 2: spoly, 3: reduce
                    "gen_arg2": None,
                    "gen_arg3": 4}
                )
                task_generator_buffer.push_token(token)
                
                #generate new pe tasks
                print("Generate REDUCE task", new_poly_id)
                reduce_task = Token(
                    {"path_id": path_id, 
                    "task_type": CstStr.REDUCE, 
                    "cond": None, # already met
                    "task_arg1": new_poly_id, 
                    "task_arg2": None, 
                    "task_arg3": None}
                )
                pe_task_buffer.push_token(reduce_task)

            else:
                # conditional not met
                task_generator_buffer.push_token(get_token(binding, buf, 0))

        if stage == 4:
            new_poly_id = prop_value(binding, buf, 0, 'gen_arg1')
            new_poly_state = prop_value(binding, poly_store_resp, 0, "state_data")
            if new_poly_state == CstStr.ZERO:
                pass
                # remove this poly from the store
                # !!! problematic None state remove for now
                # new_poly_token = Token({
                #     "path_id": path_id,
                #     "id": new_poly_id,
                #     "state": None}
                # )
                # poly_store.push_token(new_poly_token)

            elif new_poly_state == CstStr.SORTED:
                'note, there is no reduced state for new spoly, it becomes SORTED after reduce'
                # add a new spoly-gen generator
                token = Token({
                    "path_id": path_id, 
                    "gen_type": CstStr.SPOLY_GEN_GEN,
                    "gen_arg1": new_poly_id,
                    "gen_arg2": 0,
                    "gen_arg3": None}
                )
                task_generator_buffer.push_token(token)
            
            else:
                # conditional not met
                task_generator_buffer.push_token(get_token(binding, buf, 0))

    if gen_type == CstStr.PATH_GEN:
        '''
        PATH_GEN generates SPOLY_GEN_GEN
        A path generator 
            Token(path_id: _, gen_type:PATH_GEN, gen_arg1: cur_poly_id, gen_arg2: total_poly_cnt, gen_arg3: None)

            This generator stops when cur_poly_id == total_poly_cnt
                    
        A spoly-gen generator 
            Token(path_id: _, gen_type:SPOLY_GEN_GEN, gen_arg1: poly_id, gen_arg2: pair_poly_id, gen_arg3: None)
        '''
        #update task pointer
        cur_poly_id = prop_value(binding, buf, 0, 'gen_arg1')
        total_poly_cnt = prop_value(binding, buf, 0, 'gen_arg2')
        token = Token({
            "path_id": path_id,
            "gen_type": CstStr.SPOLY_GEN_GEN, 
            "gen_arg1": cur_poly_id, 
            "gen_arg2": 0,
            "gen_arg3": None})
        task_generator_buffer.push_token(token)

        'update original path_gen generator'
        if (cur_poly_id+1) < total_poly_cnt:
            token = Token({
                "path_id": path_id,
                "gen_type": CstStr.PATH_GEN, 
                "gen_arg1": cur_poly_id+1, 
                "gen_arg2": total_poly_cnt,
                "gen_arg3": None})
            task_generator_buffer.push_token(token)

    if gen_type == CstStr.SPOLY_GEN_GEN:
        '''
        SPOLY_GEN_GEN generates SPOLY_GEN
        A spoly-gen generator 
            Token(path_id: _, gen_type: ,gen_arg1: poly_id, gen_arg2: pair_poly_id, gen_arg3: None)
        '''
        #update task pointer
        poly_id = prop_value(binding, buf, 0, 'gen_arg1')
        pair_poly_id = prop_value(binding, buf, 0, 'gen_arg2')
        pair_poly_state = prop_value(binding, poly_store_resp, 0, "state_data")
        if pair_poly_state == CstStr.ZERO:
            'skip this pair because its zero'
            pair_poly_id = pair_poly_id + 1
        else:
            token = Token({
                "path_id": path_id,
                "gen_type": CstStr.SPOLY_GEN, 
                "gen_arg1": poly_id, 
                "gen_arg2": pair_poly_id,
                "gen_arg3": 0})
            task_generator_buffer.push_token(token)

        if pair_poly_id + 1 < poly_id:
            token = Token({
                "path_id": path_id,
                "gen_type": CstStr.SPOLY_GEN_GEN, 
                "gen_arg1": poly_id, 
                "gen_arg2": pair_poly_id+1,
                "gen_arg3": None})
            task_generator_buffer.push_token(token)

    if wait_for_ctrl:
        num_poly_store.push_token(Token({"num": num_poly_update}))
    else:
        ctrl.push_token(Token())

dispatch_pe = OutWeightFuncA("dispatch_pe", buffer=Place)
@dispatch_pe.install
def output_tokens(binding, output_places, buffer):
    sort_buffer, reorder_buffer, spoly_buffer, reduce_buffer = output_places
    task_type = prop_value(binding, buffer, 0, "task_type")
    token = get_token(binding, buffer, 0)
    if task_type == CstStr.SORT:
        sort_buffer.push_token(token)
    elif task_type == CstStr.REORDER:
        reorder_buffer.push_token(token)
    elif task_type == CstStr.SPOLY:
        spoly_buffer.push_token(token)
    elif task_type == CstStr.REDUCE:
        reduce_buffer.push_token(token)

update_poly_state = OutWeightFuncA("update_poly_state", task=Place, poly_store_req_idx=int, path_store_req_idx=int, func_sim_trace=typing.Dict[int, typing.Dict])
@update_poly_state.install
def output_tokens(binding, output_places, task, poly_store_req_idx, path_store_req_idx, func_sim_trace):
    path_id = prop_value(binding, task, 0, "path_id")
    task_type = prop_value(binding, task, 0, "task_type")
    poly_id = prop_value(binding, task, 0, "task_arg1")
    print("finished a task", task_type, poly_id)
    new_state = None
    if task_type == CstStr.REORDER:
        new_state = CstStr.REORDERED
    elif task_type == CstStr.SORT:
        new_state = CstStr.SORTED
    elif task_type == CstStr.SPOLY:
        'change of poly_id to spoly_id'
        new_state = CstStr.SPOLIED
    elif task_type == CstStr.REDUCE:
        poly_stats = func_sim_trace[path_id]['poly_stats']
        print("polystats id", poly_stats[poly_id])
        if poly_stats[poly_id]["nonzero"] == False:
            '''
            essentially cheating here
            '''
            new_state = CstStr.ZERO
        else:
            print("nonzero-spoly poly_id", poly_id)
            new_state = CstStr.SORTED
    
    assert(new_state != None)

    output_places[0].push_token(
        Token({
            "requester": poly_store_req_idx,
            "store_id": path_id,
            "state_id": poly_id,
            "rd_or_wr": CstStr.WRITE,
            "state_data": new_state,
            "piggyback": None})
        )
    output_places[1].push_token(
        Token({
            "idx": poly_store_req_idx})
        )
    
read_path_stats = OutWeightFuncA("read_path_stats", best_performing=Place, generator=Place, req_idx=int)
@read_path_stats.install
def output_tokens(binding, output_places, best_performing, generator, req_idx):
    bf_path_id = prop_value(binding, best_performing, 0, "path_id")
    ge_path_id = prop_value(binding, generator, 0, "path_id")

    output_places[0].push_token(
        Token({
            "requester": req_idx,
            "state_id": bf_path_id,
            "rd_or_wr": CstStr.READ,
            "state_data": None,
            "piggyback": None})
    )
    output_places[0].push_token(
        Token({
            "requester": req_idx,
            "state_id": ge_path_id,
            "rd_or_wr": CstStr.READ,
            "state_data": None,
            "piggyback": None})
    )

    output_places[1].push_token(
        Token({
            "idx": req_idx})
    )

    output_places[1].push_token(
        Token({
            "idx": req_idx})
    )