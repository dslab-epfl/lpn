import z3
import uuid
from collections import deque
from .params import *
from . import z3_util
from .extension import IntSymbolSMT as IntSymbol
timeout = 100 #seconds

PROVE_INPUT = 0


def symref(obj):
    if isinstance(obj, IntSymbol):
        return obj.symref()
    else:
        return obj
    
def MUX(cond, f1, f2):
    if cond:
        return f1
    else: 
        return f2

def flatten(list_of_queue):
    new_list = deque()
    for queue in list_of_queue:
        for ele in queue:
            new_list.append(ele)
    return new_list

def two_level_deque_copy(list_of_queue):
    new_list = deque()
    for queue in list_of_queue:
        new_list.append(queue.copy())
    return new_list

def copy_solver(solver):
    # new_solver = z3.SolverFor("QF_LIA")
    # new_solver = solver.copy.copy()
    new_solver = solver.translate(z3.main_ctx())
    # new_solver.set('threads', 8)
    # new_solver.add(solver.assertions())
    # new_solver.set("timeout", timeout*1000)
    return new_solver

def init_check_sat(cur_place, budget):
    if cur_place.init_budget < budget:
        return 0
    else:
        return 1

def conflict_resolving(solver, conflict_list):
    for each_conflict in conflict_list:
        t_list, p = each_conflict
        consumed_queue = p.consumed
        # for qidx, _list1 in enumerate(consumed_queue):
        #     for qjdx, _list2 in enumerate(consumed_queue):
        #         for tk1 in _list1:
        #             for tk2 in _list2:
        #                 if tk1 == tk2 : 
        #                     continue
        #                 solver.add( z3.Implies(tk1.ts < tk2.ts, tk1.consumed_t <= tk2.consumed_t))
            
        # if p.id == "pwrites_inject_Q": 
        #     continue
        length = len(t_list)
        for i, each_t in enumerate(t_list):
            p_i_history = each_t.history_pre[p.id]
            for j in range(i+1, length):
                another_t = t_list[j]
                p_j_history = another_t.history_pre[p.id]
                for f_i, f_i_t in enumerate(each_t.history_firing):
                    for f_j, f_j_t in enumerate(another_t.history_firing):
                        # if p.id == "pwrites_inject_Q": 
                        if disable_assert_and_track:
                            solver.add( z3.Implies(f_i_t < f_j_t, p_i_history[f_i][1] <= p_j_history[f_j][0]))
                            solver.add( z3.Implies(f_j_t < f_i_t, p_j_history[f_j][1] <= p_i_history[f_i][0])) 
                        else:
                            solver.assert_and_track( z3.Implies(f_i_t < f_j_t, p_i_history[f_i][1] <= p_j_history[f_j][0]), f"{p.id}_conflict_resolving_{uuid.uuid4().int}")
                            solver.assert_and_track( z3.Implies(f_j_t < f_i_t, p_j_history[f_j][1] <= p_i_history[f_i][0]), f"{p.id}_conflict_resolving_{uuid.uuid4().int}") 
                            

def existence_resolving(solver, p, token_produced_queues):
    if len(p.tokens_existence_dir) == 0:
        return 0

    print(f"existence {p.id} len {len(p.tokens_existence_dir)}")
    all_produced_queue = []

    # [all_produced_queue.append(_token) for _token in p.tokens_post]
    [all_produced_queue.append(_token) for _list in token_produced_queues for _token in _list]
    
    print("all_produced_queue", len(all_produced_queue))
    
    for exist_time, (required_count, fire_time) in p.tokens_existence_dir.items():
        counter_less = 0
        counter_leq = 0
        for _token in all_produced_queue:
            counter_less += z3.If( z3.And(_token.ts < exist_time, _token.consumed_t >= fire_time), 1, 0)
            counter_leq += z3.If( z3.And(_token.ts <= exist_time, _token.consumed_t >= fire_time), 1, 0)
        
        solver.add( z3.And(counter_less < required_count, counter_leq >= required_count))

# def existence_resolving(solver, p_list):
#     for p in p_list:
#         if len(p.tokens_existence_dir) == 0:
#             continue
#         print(f"existence {p.id} len {len(p.tokens_existence_dir)}")
#         all_produced_queue = []

#         # [all_produced_queue.append(_token) for _token in p.tokens_post]
#         [all_produced_queue.append(_token) for _list in p.borrowed_BW for _token in _list]
#         [all_produced_queue.append(_token) for _token in p.tokens_init]
        
#         all_produced_queue = set(all_produced_queue)
        
#         print("all_produced_queue", len(all_produced_queue))
        
#         for key in p.tokens_existence_dir.keys():
            
#             for once_queue, trans_firing_idx, trans in p.tokens_existence_dir[key]:
#                 fire_time = trans.history_firing[trans_firing_idx]
#                 time_list = []
#                 for exist_token in once_queue:
#                     time_list.append(exist_token.ts)
                
#                 maxp = z3_util.maximum2(solver, time_list)
#                 counter_less = 0
#                 counter_leq = 0
#                 for _token in all_produced_queue:
#                     counter_less += z3.If( z3.And(_token.ts < maxp, _token.consumed_t >= fire_time), 1, 0)
#                     counter_leq += z3.If( z3.And(_token.ts <= maxp, _token.consumed_t >= fire_time), 1, 0)

#                 solver.add( z3.And(counter_less < len(once_queue), counter_leq >= len(once_queue)))
#                 # solver.add(counter_leq >= len(once_queue))

def parse_track_id(track_id):
    component = track_id.split('.')
    t_id, nth_fire, cp = component[0], component[1], component[2]
    return t_id, nth_fire, cp

def equal_cond(token1, token2, print_yes=False):
    global PROVE_INPUT
    'to handle self loop with delay 0'
    if token1.track_id != None and token2.track_id != None:
        t_id1, nth_fire1, cp1 = parse_track_id(token1.track_id)
        t_id2, nth_fire2, cp2 = parse_track_id(token2.track_id)
        if t_id1 == t_id2 and cp1 != cp2 and nth_fire1 == nth_fire2:
            return False

    # print("PROVE_INPUT ", PROVE_INPUT)
    # return equal_cond_t_only(token1, token2)
    equal_cond_list = []
    equal_cond_list.append(token1.ts == token2.ts)
    equal_cond_list.append(token1.consumed_t == token2.consumed_t)
    for key in token1.props():
        if True or PROVE_INPUT:
            equal_cond_list.append(token1.prop(key) == token2.prop(key))
        
        if print_yes:
            print("======= find me ==========")
            print(key, token1.prop(key), token2.prop(key))
    
    return z3.And(equal_cond_list)

def equal_cond_t_only(token1, token2):
    equal_cond_list = []
    equal_cond_list.append(token1.ts == token2.ts)
    equal_cond_list.append(token1.consumed_t == token2.consumed_t)
    return z3.And(equal_cond_list)

def match_queues(solver, p, ori_queues_left, ori_queues_right, sizes_left, sizes_right):
    
    queues_left = ori_queues_left
    queues_right = ori_queues_right
    match_count = [[0]*len(queue) for queue in queues_right ]
    replicate_count = [[1]*len(queue) for queue in queues_right ]

    ' O(n) instead of O(n^2) previously in computing duplicates '
    ' if there is only one list in queues_right -> big savings ' 
    p_id = p.id
    token_keys = p.type_annotations
    if len(token_keys) == 0:
        for i, _list in enumerate(queues_right):
            for j, ele in enumerate(_list):
                if j == 0 :
                    replicate_count[i][0] = 1
                else: 
                    replicate_count[i][j] = z3.If( equal_cond(_list[j], _list[j-1]), replicate_count[i][j-1] + 1, 1)
                    solver.add(_list[j].consumed_t >= _list[j-1].consumed_t)
    else: 
        for i, _list in enumerate(queues_right):
            for j, ele1 in enumerate(_list):
                for k, ele2 in enumerate(_list):
                    if k == j:
                        continue
                    replicate_count[i][j] += z3.If( equal_cond(ele1, ele2), 1, 0)

    for i, _list in enumerate(queues_right):
        for j, _list2 in enumerate(queues_right):
            if i == j:
                continue
            for idx, aux_i in enumerate(_list):
                for jdx, aux_j in enumerate(_list2):
                    replicate_count[i][idx] += z3.If( equal_cond(queues_right[i][idx], queues_right[j][jdx]), 1, 0)

    for idx, queue in enumerate(queues_left):
        sizes_other = sum([e for i, e in enumerate(sizes_left) if i!=idx])

        for i, token in enumerate(queue):
            # [)
            rge = (i, sizes_other+i+1)
            ranges = []
            'calculate start and end for each queue right'
            for jdx, _ in enumerate(queues_right):
                limit = sizes_right[jdx]
                sizes_otr = sum([e for _i, e in enumerate(sizes_right) if _i != jdx])
                ranges.append( (min(limit, max(0, rge[0] - sizes_otr)), min(limit, rge[1] )) )
            
            print("tick as [) ", i, ranges)
            orlist = []
            for ith, ( (s, e), right_queue ) in enumerate( zip(ranges, queues_right) ):
                for mx in range(s, e):
                    """
                    if decided to match this token, assign consumed_t as well
                    maybe we don't want consumed_t
                    """
                    orlist.append( equal_cond(right_queue[mx],  token, False))
                for mx in range(0, len(right_queue)):
                   match_count[ith][mx] += z3.If( equal_cond(right_queue[mx], token), 1, 0)

            if disable_assert_and_track:
                solver.add(z3.Or(orlist))
            else:
                solver.assert_and_track(z3.Or(orlist), f"orlist_{p_id}_{i}_{idx}_{uuid.uuid4().int}")
           
    for idx, _list in enumerate(match_count):
        len_list = len(_list)
        for i in range(len_list):
            if i < len_list-1:
                'FIFO'
                if disable_assert_and_track:
                    solver.add( z3.Implies(match_count[idx][i] == 0, match_count[idx][i+1] == 0) ) 
                else:
                    solver.assert_and_track( z3.Implies(match_count[idx][i] == 0, match_count[idx][i+1] == 0), f"imply1_{uuid.uuid4().int}" )

    for i, _list in enumerate(queues_right):
        for j, _list2 in enumerate(queues_right):
            if i == j:
                continue
            for idx, aux_i in enumerate(_list):
                for jdx, aux_j in enumerate(_list2):
                    # solver.add(z3.Implies( z3.And(match_count[j][jdx] > 0, match_count[i][idx] == 0), aux_i.ts >= aux_j.ts))
                    if disable_assert_and_track:
                        solver.add( z3.Implies( z3.And(match_count[j][jdx] > 0, match_count[i][idx] == 0), aux_i.ts >= aux_j.ts) )
                        solver.add( z3.Implies( z3.And(match_count[i][idx]>0, match_count[j][jdx]>0, match_count[i][idx] < replicate_count[i][idx]), queues_right[i][idx].ts >= queues_right[j][jdx].ts))
                    else:
                        solver.assert_and_track( z3.Implies( z3.And(match_count[j][jdx] > 0, match_count[i][idx] == 0), aux_i.ts >= aux_j.ts), f"imply2_{uuid.uuid4().int}" )
                        solver.assert_and_track( z3.Implies( z3.And(match_count[i][idx]>0, match_count[j][jdx]>0, match_count[i][idx] < replicate_count[i][idx]), queues_right[i][idx].ts >= queues_right[j][jdx].ts), f"imply3_{uuid.uuid4().int}" )

    for i, _list in enumerate(queues_right):
        for idx, aux_i in enumerate(_list):
            if idx == len(_list)-1:
                if disable_assert_and_track:
                    solver.add(match_count[i][idx] <= replicate_count[i][idx])
                else:
                    solver.assert_and_track(z3.And(match_count[i][idx] <= replicate_count[i][idx]), f"matchlessrep1_{uuid.uuid4().int}" )

            else:
                if disable_assert_and_track:
                    solver.add(z3.Implies( z3.And(match_count[i][idx]>0, z3.Not(equal_cond(queues_right[i][idx], queues_right[i][idx+1]))), match_count[i][idx] <= replicate_count[i][idx]))    
                else:
                    solver.assert_and_track(z3.Implies( z3.And(match_count[i][idx]>0, z3.Not(equal_cond(queues_right[i][idx], queues_right[i][idx+1]))), match_count[i][idx] <= replicate_count[i][idx]),
                     f"matchlessrep2_{uuid.uuid4().int}" )

    return replicate_count, match_count

def match_queues_with_symbolic_length_of_zeros(solver, p, ori_queues_left, ori_queues_right, sizes_left, sizes_right):
    
    symbolic_num_of_zeros = z3_util.makeIntVar(solver, f"{uuid.uuid4().int}", p.tokens_init_symbolic_range[0], p.tokens_init_symbolic_range[1])
    p.symbolic_num_of_zeros = symbolic_num_of_zeros
    max_zeros = p.tokens_init_symbolic_range[1]
    min_zeros = p.tokens_init_symbolic_range[0]
    
    queues_left = ori_queues_left
    queues_right = ori_queues_right
    match_count = [[0]*len(queue) for queue in queues_right ]
    replicate_count = [[1]*len(queue) for queue in queues_right ]

    indicator = []
    for q in queues_left:
        indicator.append([])
        for _ in q:
            indicator[-1].append(z3.Bool(f"{uuid.uuid4().int}"))

    p_id = p.id
    token_keys = p.type_annotations
    if len(token_keys) == 0:
        for i, _list in enumerate(queues_right):
            for j, ele in enumerate(_list):
                if j == 0 :
                    replicate_count[i][0] = 1
                else: 
                    replicate_count[i][j] = z3.If( equal_cond(_list[j], _list[j-1]), replicate_count[i][j-1] + 1, 1)
    else: 
        for i, _list in enumerate(queues_right):
            for j, ele1 in enumerate(_list):
                for k, ele2 in enumerate(_list):
                    if k == j:
                        continue
                    replicate_count[i][j] += z3.If( equal_cond(ele1, ele2), 1, 0)

    for i, _list in enumerate(queues_right):
        for j, _list2 in enumerate(queues_right):
            if i == j:
                continue
            for idx, aux_i in enumerate(_list):
                for jdx, aux_j in enumerate(_list2):
                    replicate_count[i][idx] += z3.If( equal_cond(queues_right[i][idx], queues_right[j][jdx]), 1, 0)

    for idx, queue in enumerate(queues_left):
        sizes_other = sum([e for i, e in enumerate(sizes_left) if i!=idx])
        for i, token in enumerate(queue):
            # [)
            rge = (i, sizes_other+i+1)
            ranges = []
            for jdx, _ in enumerate(queues_right):
                limit = sizes_right[jdx]
                sizes_otr = sum([e for _i, e in enumerate(sizes_right) if _i != jdx])
                sizes_otr += max_zeros
                ranges.append((    min(limit, max(0, rge[0] - sizes_otr)), 
                                    min(limit, rge[1] )
                                ))
            print("tick as [) ", i, ranges)
            
            orlist = []
            for ith, ( (s, e), right_queue ) in enumerate( zip(ranges, queues_right) ):
                # note changed
                for mx in range(s, e):
                    orlist.append( z3.And( equal_cond(right_queue[mx], token), indicator[idx][i]==False))

                for mx in range(0, len(right_queue)):
                   match_count[ith][mx] += z3.If( z3.And( equal_cond(right_queue[mx], token), indicator[idx][i]==False), 1, 0)
            orlist.append( z3.And(token.ts == 0, indicator[idx][i]==True))
            if disable_assert_and_track:
                solver.add(z3.Or(orlist))
            else:
                solver.assert_and_track(z3.Or(orlist), f"orlist_{p_id}_{i}_{idx}_{uuid.uuid4().int}")

    for idx, _list in enumerate(match_count):
        len_list = len(_list)
        for i in range(len_list):
            if i < len_list-1:
                # FIFO
                if disable_assert_and_track:
                    solver.add( z3.Implies(match_count[idx][i] == 0, match_count[idx][i+1] == 0) ) 
                else:
                    solver.assert_and_track( z3.Implies(match_count[idx][i] == 0, match_count[idx][i+1] == 0), f"imply1_{uuid.uuid4().int}" )

    for i, _list in enumerate(queues_right):
        for j, _list2 in enumerate(queues_right):
            if i == j:
                continue
            for idx, aux_i in enumerate(_list):
                for jdx, aux_j in enumerate(_list2):
                   
                    if disable_assert_and_track:
                        solver.assert_and_track( z3.Implies( z3.And(match_count[j][jdx] > 0, match_count[i][idx] == 0), aux_i.ts >= aux_j.ts))
                        solver.add( z3.Implies( z3.And(match_count[i][idx]>0, match_count[j][jdx]>0, match_count[i][idx] < replicate_count[i][idx]), queues_right[i][idx].ts >= queues_right[j][jdx].ts))
                    else:
                        solver.assert_and_track( z3.Implies( z3.And(match_count[j][jdx] > 0, match_count[i][idx] == 0), aux_i.ts >= aux_j.ts), f"imply2_{uuid.uuid4().int}" )
                        solver.assert_and_track( z3.Implies( z3.And(match_count[i][idx]>0, match_count[j][jdx]>0, match_count[i][idx] < replicate_count[i][idx]), queues_right[i][idx].ts >= queues_right[j][jdx].ts), f"imply3_{uuid.uuid4().int}" )

    for i, _list in enumerate(queues_right):
        for idx, aux_i in enumerate(_list):
            if idx == len(_list)-1:
                if disable_assert_and_track:
                    solver.add(match_count[i][idx] <= replicate_count[i][idx])
                else:
                    solver.assert_and_track(match_count[i][idx] <= replicate_count[i][idx], f"matchlessrep1_{uuid.uuid4().int}" )

            else:
                if disable_assert_and_track:
                    solver.add(z3.Implies( z3.And(match_count[i][idx]>0, z3.Not(equal_cond(queues_right[i][idx], queues_right[i][idx+1]))), match_count[i][idx] <= replicate_count[i][idx]))    
                else:
                    solver.assert_and_track(z3.Implies( z3.And(match_count[i][idx]>0, z3.Not(equal_cond(queues_right[i][idx], queues_right[i][idx+1]))), match_count[i][idx] <= replicate_count[i][idx]),
                     f"matchlessrep2_{uuid.uuid4().int}" )
    
    from_init = 0
    for idx, q in enumerate(queues_left):
        for jdx, _ in enumerate(q):
            from_init += z3.If(indicator[idx][jdx] == True, 1, 0)

    all_match = 0    
    for i, _list in enumerate(queues_right):
        for idx, aux_i in enumerate(_list):
            all_match += z3.If(match_count[i][idx] > 0, 1, 0)

    if disable_assert_and_track:
        solver.add( from_init <= symbolic_num_of_zeros )
        solver.add( z3.Implies(all_match>0, from_init == symbolic_num_of_zeros ))
    else:
        solver.assert_and_track( from_init <= symbolic_num_of_zeros, f"form_init_sym_num{uuid.uuid4().int}")
        solver.assert_and_track( z3.Implies(all_match>0, from_init == symbolic_num_of_zeros ), f"initial_zeros_{uuid.uuid4().int}")
    return replicate_count, match_count

    
    
