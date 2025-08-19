import os
from lpnlang import Token
from jpeg_dma.lpn_def.func import *
from jpeg_dma.lpn_def.all_enum import CstStr
import ctypes

def tokens_from_input(img, node_dict):
    """
    Args:
    img (str) : path to img
    
    Returns:
    node_dict (dir) : a dictionary of key as place id, value as token queues. 
    symb_list ([symbols]) : a list of symbols
    value_list ([int]) : a list of sample values, corresponding to the symbols
    """
    lib = ctypes.CDLL('lpn_def/driver.so')

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
    # array = array[:12]
    size_of_img = os.path.getsize(img)
    size_of_data = size_of_img - 18*32
    avg_block_size = size_of_data//len(array)
    
    # jpeg header 
    pvarlatency = node_dict["pvarlatency"]
    p_req_mem = node_dict["p_req_mem"]
    t0 = node_dict["t0"]
    ptasks_bef_header = node_dict["ptasks_bef_header"]
    
    tokens = deque()
    for i, ele in enumerate(array):
        tokens.append(Token({"nonzero": ele}))
    pvarlatency.assign_marking(tokens)

    tokens = deque()
    for _ in range(18):
        tokens.append(Token({"req_len": 32}))
    
    for _ in range(avg_block_size*len(array)//32):
        tokens.append(Token({"req_len": 32}))
    left = avg_block_size*len(array) - avg_block_size*len(array)//32*32
    if left > 0:
        tokens.append(Token({"req_len": left}))
    p_req_mem.assign_marking(tokens)

    print(t0.p_input[-1].id, "avg_block_size: ", avg_block_size)
    t0.pi_w[-1] = con_edge(avg_block_size)

    print("len p_req_mem ", len(p_req_mem.tokens))
    ptasks_bef_header.assign_marking(create_empty_tokens(len(pvarlatency.tokens)))
    