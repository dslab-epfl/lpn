from ..lpn_extension import IntSymbol
from collections import deque
from ..lpn_token import Token
from ..lpn_place import Place
from . import z3_util
from .params import *

class TokenSMT(Token):
    def __init__(self, prop_dict=None, ts=0, ts_symbolize=True):
        self.prop_list = []
        if prop_dict is None:
            prop_dict = {}
        for key, value in prop_dict.items(): 
            setattr(self, key, value)
            self.prop_list.append(key)
        self.ts = ts
        self.track_id = None
        self.consumed_t = z3_util.makeIntVar(IntSymbolSMT.solver, f"symbol_consume{z3_util.getNewId()}", min_val, max_val)
        if ts_symbolize and isinstance(ts, int):
            self.ts = IntSymbolSMT(ts)

    def __repr__(self):
        return f"TokenSMT(timestamp={self.ts}-({self.consumed_t})"

class IntSymbolSMT(IntSymbol):
    solver = None
    def __init__(self, value, lower_bound=None, upper_bound=None, id=None):
        super().__init__(value, lower_bound, upper_bound, id)
        self.sym = None
        self.taint = False
        if id != None:
            self.sym = z3_util.makeIntVar(IntSymbolSMT.solver, self.id, lower_bound, upper_bound)

    def copy(self):
        # Create a new instance with the same value
        new_instance = IntSymbolSMT(self.value, self.lower_bound, self.upper_bound, self.id)
        new_instance.set_sym(self.symref())
        new_instance.taint = self.taint
        return new_instance
    
    def __lt__(self, other):
        if isinstance(other, (int,float)) :
            compare_to = other
        else: 
            compare_to = other.value 
        return self.value < compare_to

    def __gt__(self, other):
        if isinstance(other, (int,float)):
            compare_to = other
        else: 
            compare_to = other.value 
        return self.value > compare_to
    
    def __le__(self, other):
        if isinstance(other, (int,float)):
            compare_to = other
        else: 
            compare_to = other.value 
        return self.value <= compare_to

    def __ge__(self, other):
        if isinstance(other, (int,float)):
            compare_to = other
        else: 
            compare_to = other.value 
        return self.value >= compare_to
    
    def __eq__(self, other):
        if isinstance(other, (int,float)):
            compare_to = other
        else:
            compare_to = other.value
        return self.value == compare_to

    def __add__(self, other):
        # if the other or you has symbolic value
        # besides tainted 
        # need to create separate z3 value for the new returned IntSymbol 
        if isinstance(other, int):
            new = IntSymbolSMT(self.value+other)
            new.set_sym(self.symref() + other)
            new.taint = self.taint
        else:
            new = IntSymbolSMT(self.value+other.value)
            new.set_sym(self.symref() + other.symref())
            new.taint = self.taint or other.taint
        assert( isinstance(new.value, IntSymbolSMT) == False)
        return new

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        # if the other or you has symbolic value
        # besides tainted 
        # need to create separate z3 value for the new returned IntSymbol 
        if isinstance(other, int):
            new = IntSymbolSMT(self.value - other)
            new.set_sym(self.symref() - other)
            new.taint = self.taint
        else:
            new = IntSymbolSMT(self.value - other.value)
            new.set_sym(self.symref() - other.symref())
            new.taint = self.taint or other.taint
        assert( isinstance(new.value, IntSymbolSMT) == False)
        return new

    def __rsub__(self, other):
        return self.__sub__(other)
    
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            new = IntSymbolSMT(int(self.value/other))
            new.set_sym( self.symref() / int(other)) # should be int divide
            new.taint = self.taint
        else:
            new = IntSymbolSMT(self.value/other.value)
            new.set_sym( self.symref() / other.symref())
            new.taint = self.taint or other.taint
        assert( isinstance(new.value, IntSymbol) == False)
        return new
    
    def __rdiv__(self, other):
        return self.__truediv__(other)
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            new = IntSymbolSMT(int(self.value*other))
            new.set_sym(self.symref() * int(other))
            new.taint = self.taint
        else:
            new.set_sym(self.symref()*other.symref())
            new.taint = self.taint or other.taint
        assert( isinstance(new.value, IntSymbolSMT) == False)
        return new

    def __rmul__(self, other):
        return self.__mul__(other) 

    def __repr__(self):
        return f"IntSymbol({self.value}, '{self.sym}', tainted={self.taint})"

class FakePlace(Place):
    def __init__(self):
        self.tokens = deque()
    def push_token(self, tk: TokenSMT):
        self.tokens.append(tk)
    def clear_tokens(self):
        self.tokens.clear()


class TransitionShadow:
    def __init__(self, transition):
        self.transition = transition
        self.history_pre = dict()
        for idx, p in enumerate(transition.p_input):
            self.history_pre[p.id] = deque()
        self.history_firing = deque()
        self.history_t = []
        self.history_enabled_t = []
        self.symbolic_history_t = []
        self.symbolic_history_enabled_t = []
    
    def reset(self):
        for key in self.history_pre.keys():
            self.history_pre[key].clear()
        self.history_firing.clear()
        self.history_t = []
        self.history_enabled_t = []
        self.symbolic_history_t = []
        self.symbolic_history_enabled_t = []
        self.transition.pip_place.reset()
        self.transition.pip_place.assign_marking(deque([TokenSMT()]))

class PlaceShadow:
    def __init__(self, place):
        self.p = place
        # a list of deques, each deque has sorted tokens
        self.produced = []
        self.consumed = []
        self.invariant_values = dict() # a dict of dict
        self.tokens_init_symbolic = False
        self.tokens_init_symbolic_range = [0, 0]
        self.symbolic_num_of_zeros = 0
        # for time, required_num_tokens
        self.tokens_existence_dir = dict()
        self.tokens_existence_time_holder = None

    def reset(self):
        self.produced = []
        self.consumed = []
        self.invariant_values = dict() # a dict of dict
        self.tokens_init_symbolic = False
        self.tokens_init_symbolic_range = [0, 0]
        self.symbolic_num_of_zeros = 0
        # for time, required_num_tokens
        self.tokens_existence_dir = dict()
        self.tokens_existence_time_holder = None

    def record_invariant_values(self, t_id, tokens):
        if tokens == None:
            return

        keys = tokens[0].props()
        if len(self.invariant_values.keys()) == 0:
            for key in keys:
                self.invariant_values[key] = dict()
            self.invariant_values["token_time"] = dict()

        for key in self.invariant_values.keys():
            if not t_id in self.invariant_values[key]:
                self.invariant_values[key][t_id] = []
            self.invariant_values[key][t_id].append([])
        
        for token in tokens:
            self.invariant_values["token_time"][t_id][-1].append(token.ts)
            for key in token.props():
                if key in self.invariant_values:
                    self.invariant_values[key][t_id][-1].append(token.prop(key))

