from collections import deque
from sympy import nsimplify, Add, Max, Min, simplify, Symbol, Expr, Wild
from itertools import product
from .extension import IntSymbolPI as IntSymbol
from .extension import FakePlace
from ..lpn_token import Token

IF_WITH_PIP=True
out_place = FakePlace()

symb_sum_list = []
symb_sum_value_list = []

def clear_symb_list():
    symb_sum_list.clear()
    symb_sum_value_list.clear()

def symref(obj):
    if isinstance(obj, IntSymbol):
        return obj.symref()
    else:
        return obj
    
def simplify_sum_expr(expr, symb_list):
    # 'avg' represents the sum of all 'bytesN' variables
    global symb_sum_list
    global symb_sum_value_list

    symref_prefix = "SYMREF"
    symref_wild = Wild('SYMREF_wild', properties=[lambda k: k.is_Symbol and k.name.startswith(symref_prefix)])
    divisor_wild = Wild('divisor_wild', exclude=[symref_wild])

    byte_terms = []
    divisors = []

    # Make sure the expression is treated as an Add object
    for term in Add.make_args(expr):  
        match = term.match(symref_wild / divisor_wild)
        # print("match", match[symref_wild], symb_list)
        if match and match[symref_wild] in symb_list:
            # print(match[byte_wild], match[divisor_wild])
            byte_terms.append(match[symref_wild])
            divisors.append(match[divisor_wild])
    if len(byte_terms) != 0:
    # Sum the byte terms and divisors
        bytes_sum = sum(byte_terms)
        first_div = divisors[0]
        for div in divisors:
            if div != first_div:
                return None
        sum_var = None
        for idx, prev_bytes_sum in enumerate(symb_sum_value_list):
            if prev_bytes_sum == bytes_sum:
                sum_var = symb_sum_list[idx]
                break
        if sum_var == None:
            sum_var = Symbol(f"sum_symref{len(symb_sum_list)}")
            symb_sum_list.append(sum_var)
            symb_sum_value_list.append(bytes_sum)
        
        expr = nsimplify(expr)
        simplified_expr = expr.subs(sum(byte_term/first_div for byte_term in byte_terms), sum_var/first_div)
        # Simplify the expression to combine like terms if necessary
        simplified_expr = simplify(simplified_expr)
        return simplified_expr
    return None
    
def extend_binding(binding, p, tokens):

    if len(tokens) <= 0:
        return binding

    keys = tokens[0].props()
    for i in range(len(tokens)):
        for key in keys:
            binding[f"{p.id}.{i}.{key}"] = tokens[i].prop(key)
    # not used
    return binding

def restore_bindings(t, num_of_firing):
    list_of_binding = []
    
    for ith in range(num_of_firing):
        binding = {}
        for idx, p in enumerate(t.p_input):
            # check invariant values for ith firing
            #ignore mask and guard
            weight = int(t.pi_w[idx](binding))
            tokens = deque()
            for jth in range(weight):
                new_dir = dict()
                for key in p.type_annotations:
                    # introduce invariant values
                    if key in p.invariant_values:
                        new_dir[key] = p.invariant_values[key][t.id][ith][jth]
                    else:
                        raise ValueError

                token = Token(new_dir)
                tokens.append(token)
            extend_binding(binding, p, tokens)

        list_of_binding.append(binding)
    return list_of_binding

def normalize_cycle(cycle):
    return tuple(sorted(cycle))

def dfs(node, stack, graph, has_cap_node, unique_cycles, cycles):
    stack.append(node)

    for neighbor in graph.get(node, []):
        if neighbor in stack:
            # cycle = stack[stack.index(neighbor):] + [neighbor]
            cycle = stack[stack.index(neighbor):]
            if any(has_cap_node.get(n, False) for n in cycle):
                if normalize_cycle(cycle) not in unique_cycles:
                    unique_cycles.add(normalize_cycle(cycle))
                    cycles.add(tuple(cycle))
            continue

        dfs(neighbor, stack, graph, has_cap_node, unique_cycles, cycles)

    stack.pop()

def remove_subcycles(cycles, ordered_cycles):

    filtered_cycles = []
    for i, cycle in enumerate(cycles):
        contain_subcycle = False
        for j, other_cycle in enumerate(cycles):
            if i != j and set(other_cycle).issubset(set(cycle)):
                contain_subcycle = True
                break
        if not contain_subcycle:
            for ordered_cycle in ordered_cycles:
                if normalize_cycle(ordered_cycle) == cycle:
                    filtered_cycles.append(ordered_cycle)
                    break
    return filtered_cycles

def detect_cycle_in_petri_net(all_places, all_transitions):
    graph = {}
    has_cap_node = {}
    unique_cycles = set()
    cycles = set()


    # for place in all_places:
    #     if len(place.tokens_init) > 0:
    #         place.cap_node = True
    #     has_cap_node[place.id] = place.cap_node

    for trans in all_transitions:
        for place in trans.p_input:
            graph.setdefault(place.id, []).append(trans.id)
            if len(place.tokens_init) > 0:
                place.cap_node = True
            has_cap_node[place.id] = place.cap_node
        for place in trans.p_output:
            graph.setdefault(trans.id, []).append(place.id)
            if len(place.tokens_init) > 0:
                place.cap_node = True
            has_cap_node[place.id] = place.cap_node

    stack = []

    for node in graph.keys():
        dfs(node, stack, graph, has_cap_node, unique_cycles, cycles)
    
    cycles = remove_subcycles(unique_cycles, cycles)
    # for cycle in cycles:
    #     print(cycle)
    return cycles, has_cap_node


def cal_delay(unique_cycles, cap_node_set,  p_list, t_list, node_dict, symb_list, value_list, dumpfile):
    if unique_cycles:
        for i, cycle in enumerate(unique_cycles):
            # print(f"Cycle {i+1}: {cycle}")
            skip_cycle = False
            
            cap_node_id = None
            cap_node_start = None
            cap_node_count = 0
            '''
            Disallow loop with multiple capability nodes, 
            will skip the loop if that's true
            '''
            for i, node_id in enumerate(cycle):
                if node_id in cap_node_set:
                    cap_node_count += 1
                    cap_node_id = node_id
                    cap_node_start = i
            if cap_node_count > 1:
                print("skip cycle, too many cap nodes")
                continue

            if cap_node_id == None:
                assert(0)

            input_place_id = cap_node_id
            input_place = node_dict[cap_node_id]
            prev_tokens = len(node_dict[cap_node_id].tokens_init)
            cap_node_tokens = prev_tokens 
            cap_parallel = 1

            cycle_len = len(cycle)
            cycle_index = (cap_node_start+1)%cycle_len
            cur_trans_id = cycle[cycle_index] 
            t_start_index = cycle_index

            # collect all transitions
            t_index = t_start_index
            loop_transitions = []
            while 1:
                loop_transitions.append(cycle[t_index])
                t_index = (t_index+2)%cycle_len
                if t_index == t_start_index:
                    break

            all_weights = []
            all_avg_delay = {}
            transition_fire_count_in_the_cycle = {}
            while 1: 
                cycle_index += 1 # point to output node
                transition = node_dict[cur_trans_id]

                # transition has zero count 
                if transition.count == 0:
                    skip_cycle = True
                    break

                # restore bindings that the transitions have fired with in the concrete simulation
                bindings = restore_bindings(transition,  transition.count)
                
                # this is useless, transition count is not associated with the loop for now.
                # however, a very important factor to consider
                transition_fire_count_in_the_cycle[transition.id] = len(bindings)
                
                # distinct_weights collect all the input/output weights for each transition
                distinct_weights = set()
                # record the delay of the transition in each fired binding, key is the input/output pair
                delay_record = dict()
                for binding in bindings:
                    delay = symref(transition.delay_f(binding))
                    pip_delay = None if transition.pip == None else symref(transition.pip(binding))
                    input_index = transition.p_input.index(node_dict[input_place_id])
                    input_weight = int(transition.pi_w[input_index](binding))  
                    
                    if transition.pi_w_threshold != None and len(transition.pi_w_threshold) > 0 and int(transition.pi_w_threshold[input_index]) > 0:
                        if input_weight < int(transition.pi_w_threshold[input_index](binding)):
                            input_weight = int(transition.pi_w_threshold[input_index](binding))

                    output_index = transition.p_output.index(node_dict[cycle[(cycle_index)%cycle_len]])
                    out_place.clear_tokens()
                    transition.po_w[output_index](binding, out_place)
                    output_tokens = out_place.tokens 

                    # skip weights that doesn't make sense
                    if output_tokens == None or len(output_tokens) == 0:
                        # output_weight = 0
                        continue
                    else:
                        output_weight = len(output_tokens)
                        pair = (input_weight, output_weight)
                        distinct_weights.add( (input_weight, output_weight) )
                        if not pair in delay_record:
                            delay_record[pair] = []
                        if IF_WITH_PIP and pip_delay != None:
                            delay_record[pair].append(Max(delay, pip_delay))
                        else:
                            delay_record[pair].append(delay)

                if len(distinct_weights) == 0:
                    skip_cycle = True
                    break

                all_weights.append(list(distinct_weights))

                # the average delay for each transition
                avg_delay = dict()
                for _key in delay_record:
                    expr = sum(delay_record[_key])

                    if isinstance(expr, Expr):
                        simplified_expr = simplify_sum_expr(expr, symb_list)
                        # print("simplified expr : ", simplified_expr)

                        if simplified_expr == None:
                            avg_delay[_key] = expr/len(delay_record[_key])
                        else:
                            avg_delay[_key] = simplified_expr/len(delay_record[_key])

                    else:
                        avg_delay[_key] = expr/len(delay_record[_key])

                all_avg_delay[transition.id] = avg_delay

                # next transition
                input_place_id = cycle[(cycle_index)%cycle_len]
                cycle_index = (cycle_index+1)%cycle_len
                cur_trans_id = cycle[cycle_index]

                if input_place_id == cap_node_id:
                    break

            if skip_cycle == True:
                continue
            # have accounted all bindings

            for all_pairs in product(*all_weights):
                _product = len(node_dict[cap_node_id].tokens_init)
                # print("===== all pairs === ", _product, all_pairs)
                
                #check loop is well-formed:
                prev_tokens = len(node_dict[cap_node_id].tokens_init)
                _fire_count_list = []
                err = 0
                for _p, _t_id in zip( all_pairs, loop_transitions):
                    i, o = _p
                    if i == 0 or o == 0:
                        err = 1 
                        break
                    # print(node_dict[_t_id].count, prev_tokens, i)
                    _fire_count_list.append( node_dict[_t_id].count*i//prev_tokens )
                    prev_tokens = prev_tokens*o//i
                    _product = _product*o//i
                if err == 1:
                    continue

                if _product != cap_node_tokens:
                    continue
                    # need extra firing
                    # extra firing of last transition to make up the cap_node_tokens gap
                    extra = (cap_node_tokens-_product)//o 
                    print("buggy loop", all_pairs, _product, cap_node_tokens, "extra:", extra)
                    if extra <= 0:
                        continue
                else:
                    extra = 1

                    # cap_node_tokens = _product

                # print("survive one ", all_pairs)
                # this factor times prev_tokens/i will get the actual fire count of transitions in this loop
                # this is an approximation, since we don't record exactly which loops fired with which transitions
                loop_count_factor = min(_fire_count_list) 

                index_into_weights_pairs = 0        
            
                input_place_id = cap_node_id
                input_place = node_dict[cap_node_id]
                prev_tokens = cap_node_tokens
                cap_parallel = 1

                cycle_index = (cap_node_start+1)%cycle_len
                cur_trans_id = cycle[cycle_index] 
                cycle_delay_part_1 = 0
                cycle_delay_part_2 = 0
                fire_times_dict = {}
                while 1:
                    # print(cur_trans_id)
                    cycle_index += 1 # point to output node
                    transition = node_dict[cur_trans_id]
                    pair = all_pairs[index_into_weights_pairs]
                    input_weight, output_weight = pair
                    # print("======== find me ========", prev_tokens, input_weight, output_weight)
                    index_into_weights_pairs += 1
                    fire_times = prev_tokens//input_weight

                    if cycle[(cycle_index)%cycle_len] == cap_node_id and extra != 1:
                        fire_times_2 += extra
                        # print("adjust extra at", transition.id)
                    else:
                        fire_times_2 = fire_times

                    fire_times_dict[cur_trans_id] = fire_times
                    num_output_tokens = fire_times*output_weight

                    # print(all_avg_delay[transition.id])

                    t_delay = all_avg_delay[transition.id][pair]
                        
                    if IF_WITH_PIP or transition.pip is None: 
                        # modify the nonloop_stall, since it's tied to bindings, 
                        # there is no better place to do this
                        if t_delay not in transition.nonloop_stall_list:
                            transition.nonloop_stall_list.append(t_delay) # be careful, the rate is how long fire once 
                    
                        # print("======== t_delay ========== ", t_delay)
                    
                        cycle_delay_part_1 += t_delay - transition.loop_sym_stall( loop_count_factor*fire_times )
                        cycle_delay_part_2 += transition.loop_sym_stall( loop_count_factor*fire_times )*fire_times_2
                        
                        # cycle_delay_part_1 += 0
                        # cycle_delay_part_2 += t_delay*fire_times_2

                    else:
                        exit()
                        cycle_delay_part_1 += 0
                        cycle_delay_part_2 += t_delay + transition.pip*(fire_times_2-1)

                    # cycle_delay += transition.delay()
                   
                    # print("add amount", 
                    # f"{transition.id}", 
                    # "transition delay ", t_delay,
                    # "sym_rate & fire times ", transition.loop_sym_stall( loop_count_factor*fire_times ), fire_times, 
                    # "cycle_delay_added ", t_delay + transition.loop_sym_stall( loop_count_factor*fire_times )*(fire_times-1))
                    prev_tokens = num_output_tokens
                    input_place_id = cycle[(cycle_index)%cycle_len]
                    cycle_index = (cycle_index+1)%cycle_len
                    cur_trans_id = cycle[cycle_index]

                    if input_place_id == cap_node_id:
                        break

                # if 'pstall' in cycle:
                #     cycle_delay_part_2 -= 130
                
                cap_parallel = min(fire_times_dict.values())
                # print(cycle_delay, "cap parallel ", cap_parallel)
                for key, value in fire_times_dict.items():
                    transition = node_dict[key]
                    # transition_fire_count_in_the_cycle[transition.id] is all the firings of this loop
                    transition.loop_insert_stall( (cycle_delay_part_1/value + cycle_delay_part_2/(value*cap_parallel))*(transition_fire_count_in_the_cycle[transition.id]/transition.count), 
                                                         loop_count_factor*fire_times
                                                       )
                    # print(f"At end of the cycle, add amount to {transition.id} :", (cycle_delay_part_1/value + cycle_delay_part_2/(value*cap_parallel))*(transition_fire_count_in_the_cycle[transition.id]/transition.count))

    else:
        print("No unique_cycles found.")

    for t in t_list:
        if len(t.nonloop_stall_list) == 0 and t.count != 0:
            bindings = restore_bindings(t,  t.count)
            sum_of_delay = 0
            for binding in bindings:
                delay = symref(t.delay_f(binding))
                sum_of_delay += delay
            
            if not IF_WITH_PIP:
                if t.pip is not None:
                    sum_of_delay = symref(len(binding)*t.pip(binding))

            if isinstance(sum_of_delay, Expr):
                simplified_expr = simplify_sum_expr(sum_of_delay, symb_list)
                if simplified_expr == None:
                    t.nonloop_stall_list.append(sum_of_delay/len(bindings))
                else:                    
                    t.nonloop_stall_list.append(simplified_expr/len(bindings)) 
            else:
                t.nonloop_stall_list.append( sum_of_delay/len(bindings) ) 

    for t in t_list:
        print("stats ==", t.id, t.nonloop_stall_list, t.count, t.loop_stall)

    maximum = 0
    print("computing max")

    for t in t_list:
        local = t.count*t.sym_stall()
        maximum = Max(local, maximum)
        # if local > maximum:
        #     maximum = local
    print("======= done ====== ")
    # maximum = maximum / tasks_number
    print("maximum", maximum)

    maximum = simplify(maximum)
    return maximum

def lpn_construct_formulae_wloops(p_list, t_list, node_dict, unique_cycles, cap_node_set, symb_list, value_list, iterations, dumpfile, store_eval_expr):
    for i in range(iterations):
        formulae = cal_delay(unique_cycles, cap_node_set,  p_list, t_list, node_dict, symb_list, value_list, dumpfile)
        result = store_eval_expr(symb_list, value_list, formulae, dumpfile, store=False)
        print(result)
    return result

def lpn_get_loops(p_list, t_list, node_dict):
    
    count = 0
    for t in t_list:
        count += len(t.pi_w) + len(t.po_w)
    unique_cycles, has_cap_node = detect_cycle_in_petri_net(p_list, t_list)

    # can skip this part
    all_place = []
    for t in t_list:
        for p in t.p_input + t.p_output:
            if p not in all_place:
                all_place.append(p)        

    print("num t_list: ", len(t_list), "num p_list: ", len(all_place), " number of edges: ", count, ", num of cycles", len(unique_cycles) )

    # compute cap node set: the set of capability nodes
    cap_node_set = set()
    for key, value in has_cap_node.items():
        if value == True:
            cap_node_set.add(key)

    return unique_cycles, cap_node_set

def lpn_construct_formulae(p_list, t_list, node_dict, symb_list, value_list, iterations, dumpfile, store_eval_expr):
    count = 0
    for t in t_list:
        count += len(t.pi_w) + len(t.po_w)
    unique_cycles, has_cap_node = detect_cycle_in_petri_net(p_list, t_list)
    # unique_cycles, has_cap_node = [0], [0]

    # can skip this part
    all_place = []
    for t in t_list:
        for p in t.p_input + t.p_output:
            if p not in all_place:
                all_place.append(p)        

    print("num t_list: ", len(t_list), "num p_list: ", len(all_place), " number of edges: ", count, ", num of cycles", len(unique_cycles) )

    # compute cap node set: the set of capability nodes
    cap_node_set = set()
    for key, value in has_cap_node.items():
        if value == True:
            cap_node_set.add(key)

    for i in range(iterations):
        formulae = cal_delay(unique_cycles, cap_node_set,  p_list, t_list, node_dict, symb_list, value_list, dumpfile)
        result = store_eval_expr(symb_list, value_list, formulae, dumpfile, store=False)
        print(result)

    return formulae, result
