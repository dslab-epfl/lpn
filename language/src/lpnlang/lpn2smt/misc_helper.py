import z3
from .extension import IntSymbolSMT as IntSymbol
from .params import min_val, max_val
from . import z3_util
import sympy

def get_float_value(val):
    # Get the value of the variable from the model

    # If the value is a Z3 rational number (Real)
    if z3.is_rational_value(val):
        return float(val.numerator_as_long()) / float(val.denominator_as_long())

    # If the value is an integer
    elif z3.is_int_value(val):
        return float(val.as_long())

    # If the value is already a float (less common in Z3)
    elif z3.is_float_value(val):
        return float(val.as_string())

'de-IntSymbol-ize init tokens'
def set_up_smt_mode(p_list, t_list):
    for p in p_list:
        for tk in p.tokens_init:
            tk.ts = 0
            tk.consumed_t = z3_util.makeIntVar(IntSymbol.solver, f"consume{z3_util.getNewId()}", min_val, max_val)
            for key, value in tk.dict_items():
                if isinstance(value, IntSymbol):
                    tk.set_prop(key, value.symref())
     
def logout_invariants(p_list):
    for p in p_list:
        if len(p.invariant_values) != 0 :
            for key in p.invariant_values.keys():
                print(f"{p.id} {key} {p.invariant_values[key]}") 

def logout_history_pre(model, t_list):    
    for t in t_list:
        for idx, fire_time in enumerate(t.history_firing):
            print(f"t{t.id}", model[fire_time].as_long())
            for pdx, p in enumerate(t.p_input):  
                if t.pi_w_threshold != None and t.pi_w_threshold[pdx] != 0:
                    continue
                if isinstance(t.history_pre[p.id][idx][1], int):
                    token_time = t.history_pre[p.id][idx][1]
                else:
                    token_time = model[t.history_pre[p.id][idx][1]]

                print(f"history: {p.id} at {token_time}")

    # for _list in replicate_count:
    #     for c in _list:
    #         if isinstance(c, int):
    #             print("p4 replicate ", c)
    #         else:
    #             print("p4 replicate ", model.eval(c))

    # for _list in match_count:
    #     for c in _list:
    #         if isinstance(c, int ):
    #             print("p4 match ", c)
    #         else:
    #             print("p4 match ", model.eval(c))
            
    # p4 = node_dict["p4"]
    # for _list in p4.consumed:
    #     for tk in _list:
    #         # print("p4 tokens ", model[tk.ts].as_long(), model[tk.consumed_t].as_long()) 
    #         print("p4 tokens ", model[tk.ts], model[tk.consumed_t]) 
        

    # for tk in  p4.tokens_init:
    #     # print("p4 tokens ", model[tk.ts].as_long(), model[tk.consumed_t].as_long()) 
    #     print("p4 tokens init", tk.ts, model[tk.consumed_t]) 

    # for _list in p4.produced:
    #     for tk in _list:
    #         # print("p4 tokens ", model[tk.ts].as_long(), model[tk.consumed_t].as_long()) 
    #         print("p4 tokens produced", model[tk.ts], model[tk.consumed_t]) 
            
    # for p in p_list:
    #     post_list = []
    #     for token in p.tokens_produced:
    #         t_value = model[token.ts]
    #         if t_value is not None:
    #             post_list.append(t_value.as_long())
    #         else:
    #             print("none value legal")

    #     post_list = sorted(post_list)
    #     for ele in post_list:
    #         print(f"{p.id} post t_value", ele)

def sympy_to_z3(solver, sympy_expr):
    # Base case: if the expression is a number (int or float)
    if isinstance(sympy_expr, (int, float)):
        return sympy_expr

    if isinstance(sympy_expr, (sympy.Float, sympy.Integer)):
        return float(sympy_expr)
    
    if isinstance(sympy_expr, (sympy.Integer)):
        return int(sympy_expr)


    if isinstance(sympy_expr, (sympy.Rational)):
        return float(sympy_expr)

    # If the expression is a sympy symbol
    if isinstance(sympy_expr, sympy.Symbol):
        for idx, term in enumerate(symb_list):
            if sympy_expr == term:
                return z3_var_list[idx]
        # return Real(str(sympy_expr))

    # If the expression is a sympy Max function
    if isinstance(sympy_expr, sympy.Max):
        max_list = [sympy_to_z3(solver, arg) for arg in sympy_expr.args]
        return z3_util.maximum2_real(solver, max_list)

    # Handle arithmetic operations (+, -, *, /)
    if isinstance(sympy_expr, sympy.Add):
        return sum([sympy_to_z3(solver, arg) for arg in sympy_expr.args])
    if isinstance(sympy_expr, sympy.Mul):
        prod = 1
        for arg in sympy_expr.args:
            prod *= sympy_to_z3(solver, arg)
        return prod
    if isinstance(sympy_expr, sympy.Pow):
        base, exp = sympy_expr.args
        return sympy_to_z3(solver, base) ** sympy_to_z3(solver, exp)

    # Add more cases as needed for other operations or functions
    raise NotImplementedError(f"Conversion for {type(sympy_expr)} not implemented, {sympy_expr}")

# def fetch_formulae(expr_file):

#     with open(expr_file, 'r') as f:
#         data = json.load(f)
    
#     retrieved_expressions = {symbols(key): sympify(value) for key, value in data.items()}
#     maximum = sympify(data["formulae"])
#     return maximum*tasks_number
#     sub = {}
#     for var_name in retrieved_expressions.keys():
#         sub[var_name] = retrieved_expressions[var_name]

#     substituted_expression = maximum.subs(sub)
#     return substituted_expression    

def record_init_tokens(p_list):
    for p in p_list:
        p.tokens_init = p.tokens.copy()
      
def analyze_conflict(t_list, p_list, logout=False):
    conflict_list = []
    for p in p_list:
        conflict_t = []
        for t in t_list:
            if p in t.p_input:
                conflict_t.append(t)
        if len(conflict_t) > 1:
            # if p.id != "p6":
                # so the conflict doesn't handle when the edge is a threshold edge
                # automatically transform the net
            conflict_list.append((conflict_t, p))

    if logout:
        for ele1, ele2 in conflict_list:
            print(ele2.id, "conflict")
            [print(e.id) for e in ele1]

    return conflict_list