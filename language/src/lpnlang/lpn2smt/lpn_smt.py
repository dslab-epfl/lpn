import time as wallclock
import z3
from . import z3_util
from . import helper as lpn2smt_helper
from . import conversion_func as conversion
from .conversion_func import create_symbolic_tokens, resolve_symbolic_tokens
from .misc_helper import get_float_value, set_up_smt_mode, logout_invariants, logout_history_pre, record_init_tokens
from .lpn_simulate import lpn_sim
from .input_classes import input_classes, places_marking_setup
from .extension import PlaceShadow, TransitionShadow, IntSymbolSMT, TokenSMT
from .smt_walk_seq import lpn_walk_seq
from .helper import symref

def method_2_verify_for_one_class(fire_seq, p_list, t_list, node_dict, the_class_def, smt_obj):
    p_dst_name = smt_obj['target_place']
    solver = IntSymbolSMT.solver
    for p in p_list:
        p.reset()
    for t in t_list:
        t.reset()
        t.time = IntSymbolSMT(0)
        if t.pip_place != None:
            for tk in t.pip_place.tokens:
                assert(isinstance(tk, TokenSMT))

    symb_list, value_list = places_marking_setup(node_dict, the_class_def)
    'remove all IntSymbol from tokens'
    for p in p_list:
        for tk in p.tokens:
            for p, v in tk.dict_items():
                tk.set_prop(p, symref(v))
            tk.ts = symref(tk.ts)
            assert(isinstance(tk, TokenSMT)) 
    
    for t in t_list:
        if t.pip_place != None:
            for tk in t.pip_place.tokens:
                for p, v in tk.dict_items():
                    tk.set_prop(p, symref(v))
                tk.ts = symref(tk.ts)
                assert(isinstance(tk, TokenSMT)) 
        
    latency = lpn_walk_seq(t_list, node_dict, fire_seq)
    lasttime = latency
    print(latency)
    if "constraints" in smt_obj:
        additional_constraints = smt_obj["constraints"]
        sum_of_symb_list = sum(symb_list)
        avg_of_symb_list = sum(symb_list)/len(symb_list)

        for c in additional_constraints:
            annotation, value = c
            print("Add additional constraints: ", annotation, value)
            if annotation == "sum_eq":
                solver.add(sum_of_symb_list == value)
            if annotation == "avg_eq":
                solver.add(avg_of_symb_list == value)
            if annotation == "sum_ge":
                solver.add(sum_of_symb_list >= value)
            if annotation == "avg_ge":
                solver.add(avg_of_symb_list >= value)
            if annotation == "sum_le":
                solver.add(sum_of_symb_list <= value)
            if annotation == "avg_le":
                solver.add(avg_of_symb_list <= value)
            if annotation == "sum_gt":
                solver.add(sum_of_symb_list > value)
            if annotation == "avg_gt":
                solver.add(avg_of_symb_list > value)
            if annotation == "sum_lt":
                solver.add(sum_of_symb_list < value)
            if annotation == "avg_lt":
                solver.add(avg_of_symb_list < value)
            if annotation == "sum_ne":
                solver.add(sum_of_symb_list != value)
            if annotation == "avg_ne":
                solver.add(avg_of_symb_list != value)
                
    print("z3.stats", len(solver.assertions()))
    done_tokens_time = []
    p_dst = node_dict[p_dst_name]
    for tk in p_dst.tokens:
        done_tokens_time.append(tk.ts)
    
    if len(done_tokens_time) != 0:
        lasttime = z3_util.maximum2(solver, done_tokens_time)
    if smt_obj['type'] == 'OPT':
        if smt_obj['maximize'] == True:
            solver.maximize(lasttime)
        if smt_obj['minimize'] == True:
            solver.minimize(lasttime)
    elif smt_obj['type'] == 'SAT':
        compare_to = smt_obj['bound']
        bound_type = smt_obj['bound_type']
        if bound_type == "lower": 
            solver.add(lasttime >= compare_to)
        elif bound_type == "upper":
            solver.add(lasttime <= compare_to)
        else:
            raise Exception("bound_type should be either lower or upper")
    else:
        raise Exception("type should be either SAT or OPT")
    
    start = wallclock.time()
    result = solver.check()
    end = wallclock.time()
    print(f"check done {result}. time cost:", end-start )
    if result == z3.unsat:
        print(solver.unsat_core())
        return None
    if result == z3.sat:
        print("====== SAT ====")
        model = solver.model()
        latency = model[lasttime].as_long()
        for p in p_list:
            for ith, tk in enumerate(p.tokens_init):
                for key, value in tk.dict_items():
                    if not isinstance(value, int): 
                        print("""p_id:{pid} nth_token:{tk} prop:{key} value:{v} """.format(pid=p.id, tk=ith, key=key, v=model[value].as_long()))
        return latency

def verify_for_one_class(p_list, t_list, node_dict, the_class_def, smt_obj):
   
    p_dst_name = smt_obj['target_place']
    solver = IntSymbolSMT.solver
    for p in p_list:
        p.reset()
    for t in t_list:
        t.reset()
        t.time = IntSymbolSMT(0)
        if t.pip_place != None:
            for tk in t.pip_place.tokens:
                assert(isinstance(tk, TokenSMT))

    symb_list, value_list = places_marking_setup(node_dict, the_class_def)
    # for p in p_list:
    #     print(p.id, len(p.tokens))
    #     for token in p.tokens:
    #         print("{")
    #         for key, isymbol in token.dict_items():
    #             print(key, isymbol.value)
    #         print("}")
    for p in p_list:
        for tk in p.tokens:
            assert(isinstance(tk, TokenSMT)) 

    record_init_tokens(p_list)
    latency = lpn_sim(t_list, node_dict)
    print("simulation latency", latency)
    sum_fires = 0
    taint_c = 0
    for t in t_list:
        # print(t.id, t.count)
        sum_fires += len(t.history_t)
        for _time in t.history_t:
            if _time.taint:
                # print(t.id, _time)
                taint_c += 1

    print("tainted ratio ", taint_c/sum_fires)
  
    set_up_smt_mode(p_list, t_list)

    create_symbolic_tokens(solver, t_list)
    print("num of tokens: ", conversion.TOKEN_COUNTER)
    resolve_symbolic_tokens(solver, p_list, t_list)
    if "constraints" in smt_obj:
        additional_constraints = smt_obj["constraints"]
        sum_of_symb_list = sum(symb_list)
        avg_of_symb_list = sum(symb_list)/len(symb_list)

        for c in additional_constraints:
            annotation, value = c
            print("Add additional constraints: ", annotation, value)
            if annotation == "sum_eq":
                solver.add(sum_of_symb_list == value)
            if annotation == "avg_eq":
                solver.add(avg_of_symb_list == value)
            if annotation == "sum_ge":
                solver.add(sum_of_symb_list >= value)
            if annotation == "avg_ge":
                solver.add(avg_of_symb_list >= value)
            if annotation == "sum_le":
                solver.add(sum_of_symb_list <= value)
            if annotation == "avg_le":
                solver.add(avg_of_symb_list <= value)
            if annotation == "sum_gt":
                solver.add(sum_of_symb_list > value)
            if annotation == "avg_gt":
                solver.add(avg_of_symb_list > value)
            if annotation == "sum_lt":
                solver.add(sum_of_symb_list < value)
            if annotation == "avg_lt":
                solver.add(avg_of_symb_list < value)
            if annotation == "sum_ne":
                solver.add(sum_of_symb_list != value)
            if annotation == "avg_ne":
                solver.add(avg_of_symb_list != value)
                
    print("z3.stats", len(solver.assertions()))
    done_tokens_time = []
    p_dst = node_dict[p_dst_name]
    for q in p_dst.produced:
        for token in q:
            done_tokens_time.append(token.ts)
    
    if len(done_tokens_time) != 0:
        lasttime = z3_util.maximum2(solver, done_tokens_time)
    if smt_obj['type'] == 'OPT':
        if smt_obj['maximize'] == True:
            solver.maximize(lasttime)
        if smt_obj['minimize'] == True:
            solver.minimize(lasttime)
    elif smt_obj['type'] == 'SAT':
        compare_to = smt_obj['bound']
        bound_type = smt_obj['bound_type']
        if bound_type == "lower": 
            solver.add(lasttime >= compare_to)
        elif bound_type == "upper":
            solver.add(lasttime <= compare_to)
        else:
            raise Exception("bound_type should be either lower or upper")
    else:
        raise Exception("type should be either SAT or OPT")
    
    start = wallclock.time()
    result = solver.check()
    end = wallclock.time()
    print(f"check done {result}. time cost:", end-start )
    if result == z3.unsat:
        print(solver.unsat_core())
        return None
    if result == z3.sat:
        print("====== SAT ====")
        model = solver.model()
        latency = model[lasttime].as_long()
        return latency
    
def lpn_smt_setup(smt_obj):
    'set up solver'
    type = smt_obj['type']
    if type=="SAT":
        solver = z3.Solver()
        threads = 12
        solver.set("threads", threads)
        solver.set("minimize_lemmas", True)
    elif type=="OPT":
        solver = z3.Optimize()
    
    IntSymbolSMT.solver = solver
    lpn2smt_helper.PROVE_INPUT = 1

def lpn_smt(p_list, t_list, node_dict, PATH_TO_CLASSES="LPNCPP_KLEE/classes", smt_obj={}):
    method2=True
    lpn_smt_setup(smt_obj)
    if not method2:
        for t in t_list:
            if t.pi_w_threshold != None and len(t.pi_w_threshold) > 0:
                raise Exception("pi_w_threshold is currently not supported in SMT mode")
            if t.pi_guard != None and len(t.pi_guard) > 0:
                raise Exception("pi_guard is currently not supported in SMT mode")
            
    for p in p_list:
        p.mode = 1
        p.shadow = PlaceShadow(p)
    for t in t_list:
        t.shadow = TransitionShadow(t)
    
    classes, seqs = input_classes(PATH_TO_CLASSES)
    for i, (class_id, one_class) in enumerate(classes.items()):
        fire_seq = seqs[class_id]
        ans = method_2_verify_for_one_class(fire_seq, p_list, t_list, node_dict, one_class, smt_obj)
        # ans = verify_for_one_class(p_list, t_list, node_dict, one_class, smt_obj)
        print("class_id", class_id, "latency", ans)
    