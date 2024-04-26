import os
import json
from sympy import symbols, srepr, sympify
from .input_classes import input_classes
from .input_classes import input_classes, places_marking_setup
from .helper import lpn_construct_formulae_wloops, lpn_get_loops, symb_sum_list, symb_sum_value_list, clear_symb_list
from .gen_pi import generate_nonrepeatitive, generate_repeatitive
from .pi_simulate import lpn_sim
from .pi_walk_seq import lpn_walk_seq
from .extension import TransitionShadow, PlaceShadow

ArgString = """
import argparse
parser = argparse.ArgumentParser(
                    prog = 'Performance Interface')
parser.add_argument("-i", "--input",  type=str, default=False)
args = parser.parse_args()
print("latency", latency(args.input))
"""

def store_eval_expr(symb_list, value_list, formulae, dumpfile, store):
    expr_dict = {}
    for name, expr in zip(symb_sum_list, symb_sum_value_list):
        expr_dict[str(name)] = srepr(expr)
        
    expr_dict["formulae"] = srepr(formulae)
    
    sub_exprs = list(formulae.args)
    expr = formulae
    variables = expr.free_symbols
    for expr in variables:
        if expr in symb_list:
            print("hit expr ", str(expr))
            expr_dict[str(expr)] = str(expr)

    # Dump to a JSON file
    with open(f'{dumpfile}', 'w') as f:
        json.dump(expr_dict, f)
    
    with open(f'{dumpfile}', 'r') as f:
        data = json.load(f)
    
    retrieved_expressions = {symbols(key): sympify(value) for key, value in data.items()}
    formulae = sympify(data["formulae"])

    # print(formulae.args)
    # sub_exprs = list(formulae.args)
    # expr = formulae
    # variables = expr.free_symbols

    # print(variables)
    sub = {}

    for idx, term in enumerate(symb_list):
        sub[term] = value_list[idx]

    for var_name in retrieved_expressions.keys():
        sub[var_name] = retrieved_expressions[var_name].subs(sub).evalf()
        
    substituted_expression = expr.subs(sub)
    result = substituted_expression.evalf()
    return result

def extract_for_one_class(class_name, p_list, t_list, node_dict, the_class_def, fire_seq=None, unique_cycles=None, has_cap_node=None, dumpfile=None, iterations=1):
    for p in p_list:
        p.reset()

    for t in t_list:
        t.reset()

    symb_list, value_list = places_marking_setup(node_dict, the_class_def)

    latency = lpn_sim(t_list, node_dict)
    for t in t_list:
        print(t.id, t.count)
    print(latency)

    clear_symb_list()
    if unique_cycles is None:
        unique_cycles, has_cap_node = lpn_get_loops(p_list, t_list, node_dict)
        print("DEBUG:", unique_cycles, has_cap_node)
    formulae = lpn_construct_formulae_wloops(p_list, t_list, node_dict, unique_cycles, has_cap_node, symb_list, value_list, iterations, dumpfile, store_eval_expr)
    return unique_cycles, has_cap_node


def method_2_extract_for_one_class(class_name, p_list, t_list, node_dict, the_class_def, fire_seq, unique_cycles=None, has_cap_node=None, dumpfile=None, iterations=1):
    for p in p_list:
        p.reset()

    for t in t_list:
        t.reset()

    symb_list, value_list = places_marking_setup(node_dict, the_class_def)

    latency = lpn_walk_seq(t_list, node_dict, fire_seq)
    print(latency)

    clear_symb_list()
    store_eval_expr(symb_list, value_list, latency, dumpfile,True)
    
    return None, None

def lpn_pi(p_list, t_list, node_dict, input_name='<place_holder>', PATH_TO_CLASSES="LPNCPP_KLEE/classes", name_map={}, setup_func_path='', iterations=1, repeatitive=False):
    
    for p in p_list:
        p.mode = 1
        p.shadow = PlaceShadow(p)
    for t in t_list:
        t.shadow = TransitionShadow(t)

    classes, seqs = input_classes(PATH_TO_CLASSES)
    classes_dir = {}
    unique_cycles = None
    has_cap_node = None
    os.makedirs("exprs", exist_ok=True)
    for i, (class_id, one_class) in enumerate(classes.items()):
        class_name = i
        # fire_seq = seqs[class_id]
        expr_path = f"exprs/expr{class_name}.json"
        unique_cycles, has_cap_node = extract_for_one_class(
            class_name, 
            p_list, t_list, node_dict, 
            one_class, 
            fire_seq=None,
            unique_cycles=unique_cycles,
            has_cap_node=has_cap_node, 
            dumpfile=expr_path, 
            iterations=iterations)
        
        classes_dir[str(i)] = expr_path
    class_name = "perf_interface"
    if repeatitive:
        final = generate_repeatitive(setup_func_path, classes_dir, PATH_TO_CLASSES, input_name, name_map)
    else:
        final = generate_nonrepeatitive(setup_func_path, classes_dir, PATH_TO_CLASSES, input_name, name_map)
    with open(f"{class_name}.py", "w") as f:
        f.write(final+ArgString)
