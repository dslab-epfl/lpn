"""
All IntSymbol after this file should be set to int or z3value.
i.e. de_int_symbol-ize
"""
import uuid
from collections import deque
from .extension import TokenSMT
from .extension import IntSymbolSMT as IntSymbol
from .extension import FakePlace
from .helper import match_queues, match_queues_with_symbolic_length_of_zeros, existence_resolving, conflict_resolving
from .misc_helper import analyze_conflict
from .params import *
from . import z3_util

out_place = FakePlace()

single_place_special_counter = dict()
TOKEN_COUNTER = 0

def de_int_symbol(dir):
    new_dir = {}
    for key, value in dir.items():
        if isinstance(value, IntSymbol):
            new_dir[key] = value.symref()
        else:
            new_dir[key] = value
    return new_dir

def extend_binding(binding, p, tokens):
    if len(tokens) <= 0:
        return binding
    keys = tokens[0].props()
    for i in range(len(tokens)):
        for key in keys:
            binding[f"{p.id}.{i}.{key}"] = tokens[i].prop(key)
    return binding

def resolve_input_threshold(t, fire_time):
    'no support'
    assert(0)
    # for idx, p in enumerate(t.p_input):
    #     if t.pi_w_threshold != None and len(t.pi_w_threshold)>0 and t.pi_w_threshold[idx](binding=None) != 0:
    #         threshold_value = t.pi_w_threshold[idx]
    #         p.tokens_existence_dir[p.tokens_existence_time_holder] = (threshold_value, fire_time)

def resolve_input(solver, t, ith, binding, input_queues, consumed_t, concrete_mode):
    global single_place_special_counter
    global TOKEN_COUNTER 
    for idx, p in enumerate(t.p_input):
        'check invariant values for ith firing'
        'no support for guard and threshold'
        weight = t.pi_w[idx](binding)
        tokens = deque()
        for jth in range(weight):
            TOKEN_COUNTER += 1
            new_dir = dict()
            for key in p.type_annotations:
                # introduce invariant values
                if key in p.invariant_values:
                    new_dir[key] = p.invariant_values[key][t.id][ith][jth]
                else:
                    raise ValueError
            new_dir = de_int_symbol(new_dir)
            token = TokenSMT(new_dir, ts_symbolize=False)
            assert(isinstance(token.consumed_t, IntSymbol)==False)
            tokens.append(token)
        extend_binding(binding, p, tokens)
    
    'done collect binding'    
    input_t_list = []
    for idx, p in enumerate(t.p_input):
        if len(input_queues[idx]) == 0:
            last_token_time = None
        else:
            last_token_time = input_queues[idx][-1].ts

        first_token_time = None
        weight = t.pi_w[idx](binding)

        tokens = deque()
        for jth in range(weight):
            new_dir = dict()
            for key in p.type_annotations:
                new_dir[key] = binding[f"{p.id}.{jth}.{key}"]
            new_dir = de_int_symbol(new_dir)
            token = TokenSMT(new_dir, ts_symbolize=False)
            token.track_id = f"{t.id}.{ith}.consume"
            token_time = p.invariant_values["token_time"][t.id][ith][jth]
            if concrete_mode == 0:
                token.ts = z3_util.makeIntVar(solver, f"time_{uuid.uuid4().int}", min_val, max_val)
            else:
                token.ts = token_time.value
            token.consumed_t = consumed_t

            if jth == 0 :
                first_token_time = token.ts
            if last_token_time != None:
                if disable_assert_and_track:
                    solver.add( last_token_time <= token.ts )
                else:
                    solver.assert_and_track(last_token_time <= token.ts, f"strictly_increase_{uuid.uuid4().int}")
    
            tokens.append(token)
            input_queues[idx].append(token)
            last_token_time = token.ts

        if weight > 0:    
            if last_token_time == None:
                assert(0)
            t.history_pre[p.id].append((first_token_time, last_token_time))
        else:
            'cant handle inhibitor now'
            raise ValueError("inhibitor not supported") 
            # t.history_pre[p.id].append((-1, -1))
        if weight > 0:    
            input_t_list.append(last_token_time)
        
    return input_t_list
    
def resolve_output(solver, t, ith, binding, output_queues, output_time):
    for idx, p in enumerate(t.p_output):
        out_place.clear_tokens()
        t.po_w[idx](binding, out_place)
        if len(out_place.tokens) == 0:
            continue
        tokens = []
        for tk in out_place.tokens:
            new_dir = de_int_symbol(tk.prop_dict())
            new_tk = TokenSMT(new_dir, tk.ts, ts_symbolize=False)
            tokens.append(new_tk)

        for token in tokens:
            token.track_id = f"{t.id}.{ith}.produce"
            token.ts = output_time
            if t.pip is None: 
                output_queues[idx].append(token)
        'sorted not guaranteed'
        if t.pip is not None:
            print("WARNING: pip is not None")
            p.produced.append(tokens)
    
def create_consumed_produced_tokens(solver, t):
    """ 
    t is a transtion with non-zero count
    total number of tokens consumed/produced is known
    number of tokens consumed/produced each time is known (doesn't say constant)
    """
    input_queues = []
    output_queues = []

    for p in t.p_input:
        input_queues.append(deque())

    for p in t.p_output:
        output_queues.append(deque())

    t_next_avaliable_time = 0
    for ith in range(t.count):
        hist_ith_fire_t = t.history_t[ith]
        hist_ith_enabled_t= t.history_enabled_t[ith]
        if hist_ith_enabled_t.taint == 0 and hist_ith_fire_t.taint == 0:
            concrete_mode = 1
            print(t.id, ith, "enable concrete mode")
        else:
            concrete_mode = 0

        binding = dict()
        if concrete_mode:
            consumed_t = hist_ith_fire_t.value
        else:
            consumed_t = z3_util.makeIntVar(solver, f"{uuid.uuid4().int}", min_val, max_val)

        'binding is also updated after this function'
        input_t_list = resolve_input(solver, t, ith, binding, input_queues, consumed_t, concrete_mode)
        if concrete_mode:
            output_time = hist_ith_fire_t.value
            max_input_time = hist_ith_enabled_t.value
        else:
            delay = t.delay_f(binding)
            if isinstance(delay, IntSymbol):
                delay = delay.symref()
                assert(isinstance(delay, IntSymbol)==False )
            input_t_list.append(t_next_avaliable_time)
            max_input_time = z3_util.maximum2(solver, input_t_list)
            t.history_firing.append(max_input_time)
            output_time = z3_util.makeIntVar(solver, f"{uuid.uuid4().int}", min_val, max_val)
            solver.add(consumed_t == output_time)
            solver.add(output_time == max_input_time + delay)

        t.symbolic_history_t.append(output_time)
        t.symbolic_history_enabled_t.append(max_input_time)

        if t.pip != None:
            t_next_avaliable_time = max_input_time + t.pip(binding)
        else:
            t_next_avaliable_time = output_time

        # resolve_input_threshold(t, output_time)
        resolve_output(solver, t, ith, binding, output_queues, output_time)
        
    for idx, p in enumerate(t.p_input):
        if len(input_queues[idx]) > 0:
            p.consumed.append(input_queues[idx])

    for idx, p in enumerate(t.p_output):
        if len(output_queues[idx]) > 0:
            p.produced.append(output_queues[idx])

def resolve_consumed_produced_tokens(solver, p):
    
    def no_symbolic_init():
        consumed_queues = []
        produced_queues = []
        consumed_sizes = []
        produced_sizes = []

        if len(p.tokens_init) != 0:
            for tk in p.tokens_init:
                assert( isinstance(tk, TokenSMT) )
                assert( isinstance(tk.consumed_t, IntSymbol)==False )
            if len(p.produced) == 1:
                'single deque, has to be less than tokens_init'
                new_queue = p.tokens_init.copy() 
                new_queue.extend(p.produced[0])
                produced_queues.append(new_queue)
                produced_sizes.append(len(new_queue))
            else:
                produced_queues.append(p.tokens_init)
                produced_sizes.append(len(p.tokens_init))
                for q in p.produced:
                    produced_queues.append(q)
                    produced_sizes.append(len(q))
        else:
            for q in p.produced:
                produced_queues.append(q)
                produced_sizes.append(len(q))
            
        consumed_queues = p.consumed.copy()

        for q in p.consumed:
            consumed_sizes.append(len(q))

        replicate_count, match_count = match_queues(solver, p, consumed_queues, produced_queues, consumed_sizes, produced_sizes) 
        existence_resolving(solver, p, produced_queues)     
        return replicate_count, match_count

    def with_symbolic_init():

        consumed_queues = []
        produced_queues = []
        consumed_sizes = []
        produced_sizes = []

        'initial tokens represent configurable buffer with symbolic size'
        for q in p.produced:
            produced_queues.append(q)
            produced_sizes.append(len(q))
        
        consumed_queues = p.consumed.copy()

        for q in p.consumed:
            consumed_sizes.append(len(q))

        # print("symbolic match ", p.id, consumed_sizes, produced_sizes)
        replicate_count, match_count = match_queues_with_symbolic_length_of_zeros(solver, p, consumed_queues, produced_queues, consumed_sizes, produced_sizes) 
        #existence_resolving(solver, p, produced_queues)
        return replicate_count, match_count
  
    if p.tokens_init_symbolic == True:
        replicate_count, match_count = with_symbolic_init()
        return replicate_count, match_count
    else:
        replicate_count, match_count = no_symbolic_init()
        return replicate_count, match_count
    
def create_symbolic_tokens(solver, t_list):
    for t in t_list:
        if t.count == 0:
            continue
        create_consumed_produced_tokens(solver, t)

def resolve_symbolic_tokens(solver, p_list, t_list):
    for p in p_list:
        _replicate_count, _match_count = resolve_consumed_produced_tokens(solver, p)
    
    conflict_list = analyze_conflict(t_list, p_list)
    conflict_resolving(solver, conflict_list)

  