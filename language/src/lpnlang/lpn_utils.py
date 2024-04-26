from collections import deque
import math
import z3
from sympy import Symbol
from .lpn_extension import IntSymbol
from .lpn_token import Token
from .lpn_place import Place

class LpnControlledIterable:
    def __init__(self, dtype, iterable=None):
        if iterable:
            # Check if all elements in the iterable have the specified type
            if not all(isinstance(item, dtype) for item in iterable):
                raise TypeError("ERROR: All elements must have the specified data type")
        self._deque = deque(iterable)

    def __getattr__(self, attr):
        # Forward all other attribute/method accesses to the underlying deque
        return getattr(self._deque, attr)

# class LpnDeque(LpnControlledIterable):
#     def __init__(self, dtype, iterable=None):
#         super.__init__(dtype, iterable)

#     def append(self, item):
#         # Check if the appended item has the specified data type
#         if isinstance(item, type(self._deque[0])):
#             self._deque.append(item)
#         else:
#             raise TypeError("Appended item must have the same data type as existing elements")

class LpnList(LpnControlledIterable):
    def __init__(self, dtype, iterable=None):
        super.__init__(dtype, iterable)
    
    def append(self, item):
        # Check if the appended item has the specified data type
        if isinstance(item, type(self._deque[0])):
            self._deque.append(item)
        else:
            raise TypeError("Appended item must have the same data type as existing elements")

def copy_tokens_from_place(from_place:Place, num:int):
    tokens = LpnList(Token)
    for i in range(num):
        tokens.append( Place.tokens[i].copy() )
    return tokens

def prop_value(binding: dict, from_place:Place, nth:int, key:str):
    if from_place.mode == 0:
        if nth is None:
            return binding[f"{from_place.id}.{key}"]
        return binding[f"{from_place.id}.{nth}.{key}"]
    else:
        if nth is None:
            raise ValueError(f"ACCESS ERROR: key {key}, n-th cannot be None in mode 1")
        return binding[f"{from_place.id}.{nth}.{key}"]

def get_token(binding: dict, place: Place, nth:int):
    if place.mode == 0:
        'could be dangerous if not copy'
        return place.tokens[nth]
    else:
        keys = place.type_annotations
        tk = Token()
        for key in keys:
            tk.set_prop(key, binding[f"{place.id}.{nth}.{key}"])
        return tk
    
def lpn_int(x):
    print("lpn_int", x)
    if isinstance(x, float) or isinstance(x, int):
        return int(x)
    elif isinstance(x, z3.ArithRef):
        return z3.ToInt(z3.ToReal(x))
    elif isinstance(x, Symbol):
        return x
    return x


binding = dict()

def lpn_all_nodes(t_list):
    p_list = []
    for t in t_list:
        for p in t.p_input + t.p_output:
            if p not in p_list:
                p_list.append(p)        
    
    node_dict = {}
    for _t in t_list:
        node_dict[_t.id] = _t

    for _p in p_list:
        node_dict[_p.id] = _p 

    return p_list, t_list, node_dict

def dump_place_types(p_list, file_path):
    place_types = {}
    for p in p_list:
        place_types[p.id] = p.type_annotations
    with open(file_path, 'w') as file:
        for place_id, place_type in place_types.items():
            file.write(f"{place_id}: {place_type}\n")
    return place_types

def retrieve_place_types(p_list, file_path):
    place_types = {}
    with open(file_path, 'r') as file:
        for line in file:
            place_id, place_type = line.split(':')
            fields = place_type.strip().replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(',')
            fields = [field for field in fields if field]
            place_types[place_id] = fields
    for p in p_list:
        p.type_annotations = place_types[p.id]

