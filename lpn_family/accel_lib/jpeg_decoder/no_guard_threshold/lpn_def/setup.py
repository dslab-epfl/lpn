import uuid
from lpnlang import Place, Transition, Token
from lpnlang.lpn2pi import detect_class
from .funcs import *
from .transitions import *
from .places import *
from .tokens_from_input import tokens_from_input
from .symbolic_token_with_blocks import symbolic_token_with_blocks
from .lpn_def import JPEG
import ctypes
import math

def init_place():

    p4.assign_marking(create_empty_tokens(4))
    p5.assign_marking(create_empty_tokens(7))
    p6.assign_marking(create_empty_tokens(4))
    p8.assign_marking(create_empty_tokens(1))
    p20.assign_marking(create_empty_tokens(4))
    pt2p_hold.assign_marking(create_empty_tokens(1))
    pt3p_hold.assign_marking(create_empty_tokens(1))
    pt4p_hold.assign_marking(create_empty_tokens(1))
  
def setup(img):
    init_place()
    from_input_dict = tokens_from_input(img)
    # tks = deque()
    # for i in range(x):
    #     tks.append(Token({"nonzero": 63}))
    # from_input_dict[pvarlatency.id] = tks
    pvarlatency.assign_marking(from_input_dict[pvarlatency.id])
    ptasks.assign_marking(create_empty_tokens(len(pvarlatency.tokens)))

    return from_input_dict

def symbolic_setup_with_blocks(num_blocks):
    init_place()
    from_input_dict = symbolic_token_with_blocks(num_blocks)
    pvarlatency.assign_marking(from_input_dict[pvarlatency.id])
    ptasks.assign_marking(create_empty_tokens(len(pvarlatency.tokens)))
    return from_input_dict

def tokens_from_input_wchunk(img, input_class_dir):
    """
    Args:
    img (str) : path to jpeg img
    
    Returns:
    ctypes ([class_types]) : a list of class types for each chunk. 
    symb_list_list ([[symbols]]) : a list of list of symbols
    value_list ([[int]]) : a list of list of sample values, corresponding to the symbols
    """

    p_list, t_list, node_dict = JPEG()
    lib = ctypes.CDLL('lpn_def/cpp/driver.so')

    lib.lpn_driver.restype = ctypes.POINTER(ctypes.c_int)
    # Define the argument types (pointer to int, pointer to char)
    lib.lpn_driver.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_char_p]
    # Prepare the arguments
    size = ctypes.c_int()
    filepath = ctypes.c_char_p(img.encode('utf-8'))
    # Call the function
    array_pointer = lib.lpn_driver(ctypes.byref(size), filepath)

    # Convert to a Python list
    array = [array_pointer[i] for i in range(size.value)]
    print("return size ", size.value)
    node_dict = {}

    #chunking happens here
    chunk_size = 12
    extra = math.ceil(len(array)/chunk_size)*chunk_size - len(array)
    array = array + [0]*extra
    
    ctype_list = []
    symb_list_list = []
    value_list_list = []

    idx = 0
    while idx < len(array):
        for p in p_list:
            p.reset()
        
        init_place()
        for jdx in range(idx, idx+chunk_size):
            pvarlatency.tokens.append(Token({"nonzero": array[jdx]}))
            ptasks.tokens.append(Token())
        
        idx += chunk_size

        # check which class it is
        ctype, symb_list, value_list = detect_class(p_list, input_class_dir)
        if value_list is None:
            print("this chunk Not covered")
            return None, None, None
        ctype_list.append(ctype)
        symb_list_list.append(symb_list)
        value_list_list.append(value_list)

    return ctype_list, symb_list_list, value_list_list
