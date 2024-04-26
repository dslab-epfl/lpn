from .lpn_extension import IntSymbol, Shadowable
from sympy import Symbol

class Token:
    def __init__(self, prop_dict=None, ts=0):
        self.prop_list = []
        if prop_dict is None:
            prop_dict = {}
        for key, value in prop_dict.items(): 
            # if not isinstance(value, int) and not isinstance(value, IntSymbol) and not isinstance(value, Symbol):
            setattr(self, key, value)
            self.prop_list.append(key)
        self.ts = ts

    def copy(self):
        attributes = {key: getattr(self, key) for key in self.prop_list}
        return Token(attributes, self.ts)
    
    def props(self):
        return self.prop_list
    
    def prop(self, key):
        return getattr(self, key)
    
    def dict_items(self):
        return [(key, getattr(self, key)) for key in self.prop_list]

    def prop_dict(self):
        attributes = {key: getattr(self, key) for key in self.prop_list}
        return attributes

    def set_prop(self, key, value):
        if key not in self.prop_list:
            self.prop_list.append(key)
        setattr(self, key, value)
        
    def add_prop(self, key, value):
        setattr(self, key, value)
        self.prop_list.append(key)
