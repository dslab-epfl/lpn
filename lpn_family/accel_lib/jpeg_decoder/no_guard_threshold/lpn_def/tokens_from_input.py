from collections import deque
from lpnlang import Place, Transition, Token
from lpnlang import createIntSymbol
from .funcs import *
from .transitions import *
from .places import *
import ctypes

COUNTER = 0
def tokens_from_input(img):
    """
    Args:
    img (str) : path to img
    
    Returns:
    node_dict (dir) : a dictionary of key as place id, value as token queues. 
    symb_list ([symbols]) : a list of symbols
    value_list ([int]) : a list of sample values, corresponding to the symbols
    """
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
    tokens_dict = {}
    tks = deque()
    for i, ele in enumerate(array):
        global COUNTER
        tks.append(Token({"nonzero": ele}))
        COUNTER += 1
    tokens_dict[pvarlatency.id] = tks
    return tokens_dict