setup_perf_interface = """
def perf_interface_{ctype}(symb_list, value_list):
{code_in_bridge}
    input = AbstractInput({all_attributes})
{setup_input}
    return input
"""
