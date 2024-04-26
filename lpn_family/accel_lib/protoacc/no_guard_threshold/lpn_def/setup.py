import json
from lpn_def.sim import setup
from lpn_def.sim import lpn_def as ProtoaccDefOnly
from lpnlang.lpn2pi import detect_class

def tokens_from_input(msgs, input_class_dir):
    """
    Args:
    msgs (str) : path to msgs json
    
    Returns:
    node_dict (dir) : a dictionary of key as place id, value as token queues. 
    symb_list ([symbols]) : a list of symbols
    value_list ([int]) : a list of sample values, corresponding to the symbols
    """

    with open(f'{msgs}', 'r') as f:
        data = json.load(f)

    p_list, t_list, node_dict = ProtoaccDefOnly()
    setup(p_list, t_list, node_dict, data)

    # check which class it is
    ctype, symb_list, value_list = detect_class(p_list, input_class_dir)
    if value_list is None:
        print("This msg not covered")
        return None, None, None
    return ctype, symb_list, value_list