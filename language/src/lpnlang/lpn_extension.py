class Shadowable:
    def __init__(self):
        self.shadow = None
    
    def __getattr__(self, name):
        """Fallback to shadow's attributes if not found."""
        if name in self.__dict__:
            return self.__dict__[name]
        if self.__dict__['shadow'] is not None and hasattr(self.__dict__['shadow'], name):
            return getattr(self.__dict__['shadow'] , name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def reset(self):
        if self.shadow is not None:
            self.shadow.reset()

    def register_shadow(self, shadow):
        self.shadow = shadow

class IntSymbol:
    def __init__(self, value, lower_bound=None, upper_bound=None, id=None):
        self.value = value
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.id = id
        self.sym = None
    
    def __int__(self):
        return self.value
    
    def __index__(self):
        return self.value

    def symref(self):
        if self.sym == None:
            return self.value
        else:
            return self.sym
    
    def set_sym(self, sym_value):
        if not isinstance(sym_value, int):
            self.sym = sym_value
    
    def __repr__(self):
        return f"IntSymbol({self.value}, '{self.symref()}')"

def createIntSymbol(value, lower_bound=None, upper_bound=None, id=None):
    return IntSymbol(value, lower_bound, upper_bound, id)
