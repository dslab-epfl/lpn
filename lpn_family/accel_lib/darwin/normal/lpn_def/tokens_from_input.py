from collections import deque
from lpnlang import Place, Transition, Token
from lpnlang import createIntSymbol
from lpnlang.lpn2pi import detect_class
from .funcs import *
from .transitions import *
from .places import *
from .lpn_def import Darwin
import ctypes

def tokens_from_input(dna_pairs, input_class_dir):
    """
    Args:
    img (str) : path to dna sequence
    
    Returns:
    ctypes ([class_types]) :  
    symb_list_list ([[symbols]]) : a list of list of symbols
    value_list ([[int]]) : a list of list of sample values, corresponding to the symbols
    """
    path1, path2 = dna_pairs.split(' ')
    dna_pairs = [path1, path2]
    p_list, t_list, node_dict = Darwin()
    lib = ctypes.CDLL('lpn_def/cpp/driver.so')

    lib.bt_steps.restype = ctypes.POINTER(ctypes.c_int)
    # Define the argument types (pointer to int, pointer to char)
    lib.bt_steps.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    # Prepare the arguments
    filepath = ctypes.c_char_p(dna_pairs[0].encode('utf-8'))
    filepath2 = ctypes.c_char_p(dna_pairs[1].encode('utf-8'))
    # Call the function
    array_pointer = lib.bt_steps(filepath, filepath2)

    # Convert to a Python list
    array = [array_pointer[i] for i in range(3)]
    print(array)

    tokens_dict = {}
    tks = deque()
    tks.append(Token({"ref_len":array[0], "query_len": array[1], "steps": array[2]}))
    ptasks.assign_marking(tks)

    # check which class it is
    ctype, symb_list, value_list = detect_class(p_list, input_class_dir)
    if value_list is None:
        print("This pair are not covered")
        return None, None, None
    return ctype, symb_list, value_list

    tokens_dict[ptasks.id] = tks
    return tokens_dict