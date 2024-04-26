import uuid
from lpnlang import Place, Transition, Token
from lpnlang import createIntSymbol
from lpnlang.lpn2pi import detect_class
from .funcs import *
from .transitions import *
from .places import *
from .tokens_from_input import tokens_from_input
from .lpn_def import Darwin
import ctypes
import math

def get_tokens_from_input(dna_pairs):
    """
    Args:
    img (str) : path to dna sequence
    
    Returns:
    ctypes ([class_types]) :  
    symb_list_list ([[symbols]]) : a list of list of symbols
    value_list ([[int]]) : a list of list of sample values, corresponding to the symbols
    """

    # p_list, t_list, node_dict = Darwin()
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
    tokens_dict[ptasks.id] = tks
    return tokens_dict

def setup(dna_pairs):
    from_input_dict = get_tokens_from_input(dna_pairs)
    ptasks.assign_marking(from_input_dict[ptasks.id])
    return from_input_dict

def symbolic_setup_():
    tks = deque()
    tks.append(Token(
        {
            "ref_len": createIntSymbol(320, 0, 10000, "ref_len0"), 
            "query_len": createIntSymbol(320, 0, 10000, "query_len0"), 
            "steps": createIntSymbol(320, 0, 10000, "steps0")
        }))
    ptasks.assign_marking(tks)
    return None
