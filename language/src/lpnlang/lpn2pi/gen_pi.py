import json
import re
from sympy import symbols, sympify, pycode, simplify
from textwrap import dedent
from .cst_string import setup_perf_interface

INDENT = "    "
NEWLINE = '\n'

class AbstractInput:
    def __init__(self, list_of_attributes):
        for attr in list_of_attributes:
            setattr(self, attr, 0)

def fetch_formulae(symb_list, value_list):
    with open('expressions_jpeg_test.json', 'r') as f:
        data = json.load(f)

    retrieved_expressions = {symbols(key): sympify(value) for key, value in data.items()}
    maximum = sympify(data["formulae"])
    substitutions = {term: value_list[idx] for idx, term in enumerate(symb_list)}

    for var_name, expression in retrieved_expressions.items():
        substitutions[var_name] = expression.subs(substitutions).evalf()

    substituted_expression = maximum.subs(substitutions)
    return substituted_expression.evalf()

def find_max_sym_number(text):
    matches = re.findall(r'SYMREF([0-9]+)', text)
    return max(map(int, matches)) if matches else None

def perf_wrapper_for_one_class(ctype, input_name, name_map, json_data):
    
    retrieved_expressions = {symbols(key): sympify(value).evalf(2) for key, value in json_data.items()}
    maximum = sympify(json_data["formulae"])
    code_in_bridge = "\n"
    code_in_formulae = ""
    all_attributes = []
    for key, value in retrieved_expressions.items():
        if key.name == "formulae":
            rhs = pycode(simplify(value))
            for name, replace_with in name_map.items():
                rhs = rhs.replace(name, replace_with)
            code_in_formulae += f"{rhs}\n"
        else:
            variable_name = key.name
            for name, replace_with in name_map.items():
                variable_name = variable_name.replace(name, replace_with)
            code_in_bridge += f"{variable_name} = {pycode(value)}\n"
            all_attributes.append(variable_name)

    max_pop = find_max_sym_number(code_in_bridge)
    code_in_bridge = re.sub(r'SYMREF([0-9]+)', r'value_list[\1]', code_in_bridge)
    code_in_bridge = re.sub(r'\nvalue_list\[([0-9]+)\] = value_list\[([0-9]+)\]', r'\nSYMREF\2 = value_list[\2]', code_in_bridge)
    NEWLINE = "\n"
    setup_input = NEWLINE.join([f"input.{key} = {key}" for key in all_attributes])
    setup_input += NEWLINE+f"input.type = {ctype}"
    setup_input = NEWLINE.join(INDENT + (line if line.strip() else '') for line in setup_input.split(NEWLINE) )
    
    code_in_bridge = NEWLINE.join(INDENT + (line if line.strip() else '') for line in code_in_bridge.split(NEWLINE) )
    
    # print(setup_input)
    wrapper_function = setup_perf_interface.format(ctype=ctype, code_in_bridge=code_in_bridge, all_attributes=all_attributes, setup_input=setup_input)
    for key in all_attributes:
        code_in_formulae = re.sub(f"{key}", f'{input_name}.{key}', code_in_formulae)
    
    return wrapper_function, code_in_formulae

def generate_nonrepeatitive(lpn_name, classes_dir, classes_dir_abspath, input_name, name_map):
    """
    Non-repeattivie performance interface generation

    Args:
        classes_dir (map) : key is the class type, value is the corresponding extracted pi/formulae
        classes_dir_abspath (str) : absolute path to classes def
        input_name (str) : meaningful name of the input
        name_map (map) : key is original name appearing in the formulae, value is the new name
    
    """
    code_in_perf = {}
    code_in_wrapper = {}
    for ctype, formulae_file in classes_dir.items():
        with open(formulae_file, 'r') as f:
            data = json.load(f)
        wrapper, perf = perf_wrapper_for_one_class(ctype, input_name, name_map, data)
        code_in_wrapper[ctype] = wrapper
        code_in_perf[ctype] = perf
    
    wrapper_body = ""
    for key in code_in_wrapper.keys():
        wrapper_body += dedent(f"""
        if {key} == ctype:
            input = perf_interface_{key}(symb_list, value_list)"""
        )


    perf_func_class_def = ""
    for key in code_in_wrapper.keys():
        perf_func_class_def += code_in_wrapper[key]

    wrapper_body = NEWLINE.join(INDENT*3 + (line if line.strip() else '') for line in wrapper_body.split(NEWLINE) )
    perf_func_class_def = NEWLINE.join(INDENT*2 + (line if line.strip() else '') for line in perf_func_class_def.split(NEWLINE) )
    wrapper_function = dedent(f"""
    def perf_interface(func):{NEWLINE}{perf_func_class_def}
        def wrapper(input):
            ctype, symb_list, value_list = tokens_from_input(input, "{classes_dir_abspath}")
            input = None {NEWLINE}{wrapper_body}
            if input is None:
                exit("ERROR: {input_name} type not support")
            return func(input)
        return wrapper"""
    )

    perf_code_body = ""
    for key in code_in_perf.keys():
        perf_code_body += dedent(f"""
        if {input_name}.type == {key}:
            cycles = {code_in_perf[key]}"""
        )
    perf_code_body = NEWLINE.join(INDENT*2 + (line if line.strip() else '') for line in perf_code_body.split(NEWLINE) )
    interface_code = dedent(f"""
    @perf_interface
    def latency({input_name}):{NEWLINE}{perf_code_body}
        return cycles
    """)

    header = dedent(f"""
    from {lpn_name}.setup import tokens_from_input
    class AbstractInput:
        def __init__(self, list_of_attributes):
            for attr in list_of_attributes:
                setattr(self, attr, 0)
    """)
    final = header + "\n" +\
            wrapper_function + "\n" +\
            interface_code
    return final



def generate_repeatitive(lpn_name, classes_dir, classes_dir_abspath, input_name, name_map):
    """
    Non-repeattivie performance interface generation

    Args:
        classes_dir (map) : key is the class type, value is the corresponding extracted pi/formulae
        classes_dir_abspath (str) : absolute path to classes def
        input_name (str) : meaningful name of the input
        name_map (map) : key is original name appearing in the formulae, value is the new name
    
    """

    code_in_perf = {}
    code_in_wrapper = {}
    for ctype, formulae_file in classes_dir.items():
        with open(formulae_file, 'r') as f:
            data = json.load(f)
        wrapper, perf = perf_wrapper_for_one_class(ctype, input_name, name_map, data)
        code_in_wrapper[ctype] = wrapper
        code_in_perf[ctype] = perf
    
    wrapper_body = ""
    for key in code_in_wrapper.keys():
        wrapper_body += dedent(f"""
        if {key} == ctype:
            input = perf_interface_{key}(symb_list, value_list)"""
        )

    perf_func_class_def = ""
    for key in code_in_wrapper.keys():
        perf_func_class_def += code_in_wrapper[key]

    wrapper_body = NEWLINE.join(INDENT*4 + (line if line.strip() else '') for line in wrapper_body.split(NEWLINE) )
    perf_func_class_def = NEWLINE.join(INDENT*2 + (line if line.strip() else '') for line in perf_func_class_def.split(NEWLINE) )
    wrapper_function = dedent(f"""
    def perf_interface(func):{NEWLINE}{perf_func_class_def}
        def wrapper(input):
            ctype_list, symb_list_list, value_list_list = tokens_from_input_wchunk(input, "{classes_dir_abspath}")
            inputs = []
            for ctype, symb_list, value_list in zip(ctype_list, symb_list_list, value_list_list):
                input = None {NEWLINE}{wrapper_body}
                if input is None:
                    exit("ERROR: {input_name} has chunk not supported")
                inputs.append(input)
            return func(inputs)
        return wrapper
    """)

    perf_code_body = ""
    for key in code_in_perf.keys():
        perf_code_body += dedent(f"""
        if {input_name}.type == {key}:
            cycles += {code_in_perf[key]}"""
        )
    perf_code_body = NEWLINE.join(INDENT*3 + (line if line.strip() else '') for line in perf_code_body.split(NEWLINE) )
    perf_code_body = re.sub(input_name, f"{input_name}_chunk", perf_code_body)
    interface_code = dedent(f"""
    @perf_interface
    def latency({input_name}):
        cycles = 0
        for {input_name}_chunk in {input_name}:{perf_code_body}
        return cycles
    """)

    header = dedent(f"""
    from {lpn_name}.setup import tokens_from_input_wchunk
    class AbstractInput:
        def __init__(self, list_of_attributes):
            for attr in list_of_attributes:
                setattr(self, attr, 0)
    """)
    final = header + "\n" +\
            wrapper_function + "\n" +\
            interface_code
    return final