import uuid
from collections import deque
from jpeg_dma.lpn_def.tokens_from_input import tokens_from_input

def setup(img, node_dict):
    from_input_dict = tokens_from_input(img, node_dict)
    return from_input_dict

