from ..lpn_extension import IntSymbol
from ..lpn2sim.emitcpp import pylpn2cpp_no_sim, INDENT
from .symbex_sim_cst_str import SYMBEX_SIM_CC, SETUP_PLACE_HH_INCLUDE, NEW_SYMBOLIC_INT

def generate_simulator_based_on_t_list(t_list, PATH_NAME):
        t_list_str = ', '.join([ f"&{_t.id}" for _t in t_list ])
        t_size = len(t_list)
        t_list_def = """Transition* t_list[T_SIZE] = {{ {t_list_str} }};""".format(t_list_str=t_list_str)
        sim_code = SYMBEX_SIM_CC.format(t_list_def=t_list_def, T_SIZE=t_size)
        with open(f"{PATH_NAME}/path_sim.cc", "w") as f:
            f.write(sim_code)
            
def generate_lpn_init(p_list, set_of_token_types, PATH_NAME):
    place_declaration = SETUP_PLACE_HH_INCLUDE
    setup_place_code = """void lpn_init() {\n\n"""
    defined = set()
    symb_int_cnt = 0
    for place in p_list:
        if len(place.tokens_init) != 0:
            if len(place.type_annotations) == 0:
                setup_place_code += """{indent}for (int i = 0; i < {tk_len}; ++i){{\n{indent2}NEW_TOKEN(EmptyToken, new_token);\n{indent2}{pid}.pushToken(new_token);\n{indent}}}\n""".format(tk_len=len(place.tokens_init), pid=place.id, indent=INDENT, indent2=INDENT*2)
                setup_place_code += "\n"
                continue
            
            setup_place_code += """\n{indent}for (int i = 0; i < {tk_len}; ++i){{\n""".format(tk_len=1, indent=INDENT)
            for ith, tk in enumerate(place.tokens_init):
                tk_name = f"{place.id}_{ith}_tk"
                token_type_str = set_of_token_types[tuple(place.type_annotations)]
                setup_place_code += """{indent}NEW_TOKEN({token_type_str}, {token_name});\n""".format(indent=INDENT*2, token_type_str=token_type_str, token_name=tk_name)
                for key in place.type_annotations:
                    value = tk.prop(key)
                    if isinstance(value, IntSymbol):
                        setup_place_code += NEW_SYMBOLIC_INT.format(indent=INDENT*2, name=value.id, min=value.lower_bound, max=value.upper_bound)
                        setup_place_code += """{indent}{tk_name}->{key} = {value};\n""".format(indent=INDENT*2, tk_name=tk_name, key=key, value=value.id)
                    else:
                        setup_place_code += """{indent}{tk_name}->{key} = {value};\n""".format(indent=INDENT*2, tk_name=tk_name, key=key, value=value)
                setup_place_code += """{indent}{pid}.pushToken({tk_name});\n\n""".format(indent=INDENT*2, pid=place.id, tk_name=tk_name)
            setup_place_code += "\n"
            setup_place_code += """{indent}}}\n""".format(indent=INDENT)
    setup_place_code += "}\n"
    endif = """#endif"""
    
    with open(f"{PATH_NAME}/lpn_init.hh", 'w') as f:
        f.write(place_declaration + setup_place_code + endif)

def pylpn2symbexlpn(p_list, t_list, enums):
    PATH_NAME = "LPNCPP_KLEE"
    set_of_token_types = pylpn2cpp_no_sim(p_list, t_list, enums, PATH_NAME, int_only=True)
    generate_simulator_based_on_t_list(t_list, PATH_NAME)
    generate_lpn_init(p_list, set_of_token_types, PATH_NAME)      

def lpn2symlpn(p_list, t_list, enums):
    pylpn2symbexlpn(p_list, t_list, enums)
