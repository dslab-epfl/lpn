from ..lpn_extension import IntSymbol
from collections import deque
from ..lpn_token import Token
from ..lpn_place import Place
from sympy import symbols, Max

class IntSymbolPI(IntSymbol):
    def __init__(self, value=0, lower_bound=None, upper_bound=None, id=None, sym=None):
        super().__init__(value, lower_bound, upper_bound, id)
        self.sym = sym
        if id != None and sym == None:
            self.sym = symbols(self.id)
        if id != None and sym != None:
            raise ValueError("Cannot specify both id and symref()")

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
    
    def __sub__(self, other):
        # if the other or you has symref()bolic value
        # besides tainted 
        # need to create separate z3 value for the new returned IntSymbol 
        if isinstance(other, (int, float)):
            new = IntSymbolPI(self.value - other)
            new.set_sym(self.symref() - other)
        else:
            new = IntSymbolPI(self.value - other.value)
            new.set_sym(self.symref() - other.symref())
        assert( isinstance(new.value, IntSymbolPI) == False)
        return new

    def __rsub__(self, other):
        return self.__sub__(other)
    
    def __add__(self, other):
        # if the other or you has symref()bolic value
        # besides tainted 
        # need to create separate z3 value for the new returned IntSymbol 
        if isinstance(other, (int, float)):
            new = IntSymbolPI(self.value+other)
            new.set_sym(self.symref() + other)
        else:
            new = IntSymbolPI(self.value+other.value)
            new.set_sym(self.symref() + other.symref())
        assert( isinstance(new.value, IntSymbolPI) == False)
        return new

    def __radd__(self, other):
        return self.__add__(other)
    
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            new = IntSymbolPI(int(self.value/other))
            new.set_sym(self.symref() / int(other)) # should be int divide
        else:
            new = IntSymbolPI(self.value/other.value)
            new.set_sym(self.symref() / other.symref())
        assert( isinstance(new.value, IntSymbolPI) == False)
        return new
    
    def __rdiv__(self, other):
        return self.__truediv__(other)
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            new = IntSymbolPI(int(self.value*other))
            new.set_sym(self.symref() * int(other)) # should be int divide
        else:
            new = IntSymbolPI(int(self.value*other.value))
            new.set_sym(self.symref()*other.symref())
        assert( isinstance(new.value, IntSymbolPI) == False)
        return new

    def __rmul__(self, other):
        return self.__mul__(other) 

    def __mod__(self, other):
        if isinstance(other, int):
            new = IntSymbolPI(self.value % other)
            new.set_sym(self.symref() % other)
        else:
            new = IntSymbolPI(self.value % other.value)
            new.set_sym(self.symref() % other.symref())
        assert( isinstance(new.value, IntSymbolPI) == False)
        return new
    
    def __rmod__(self, other):
        return self.__mod__(other)

class FakePlace(Place):
    def __init__(self):
        self.tokens = deque()
    def push_token(self, tk: Token):
        self.tokens.append(tk)
    def clear_tokens(self):
        self.tokens.clear()


class TransitionShadow:
    def __init__(self, transition):
        self.t = transition
        self.nonloop_stall_list = []
        self.loop_stall = dict()
    
    def reset(self):
        self.nonloop_stall_list = []
        self.loop_stall = dict()
        
    def sym_stall(self):
        if self.t.count == 0:
            return 0
        _sum = 0
        _sum_count = 0
        for count, stall_list in self.loop_stall.items():
            _sum += count*Max(*stall_list)
            _sum_count += count

        if self.t.count > _sum_count:
            _sum += (self.t.count - _sum_count)*Max(*self.nonloop_stall_list)
            _sum_count = self.t.count
        return _sum/_sum_count

    def loop_sym_stall(self, loop_count):
        if not loop_count in self.loop_stall:
            self.loop_stall[loop_count] = []
            if self.t.pip is None:
                self.loop_stall[loop_count].append( Max(*self.nonloop_stall_list) )
            return  Max(*self.nonloop_stall_list)
        else:
            return Max(*self.loop_stall[loop_count])
    
    def loop_insert_stall(self, stall, loop_count):
        if not loop_count in self.loop_stall:
            self.loop_stall[loop_count] = []
            if self.t.pip is None:
                self.loop_stall[loop_count].append( Max(*self.nonloop_stall_list) )
        self.loop_stall[loop_count].append(stall)
      
class PlaceShadow:
    def __init__(self, place):
        self.p = place
        # a list of deques, each deque has sorted tokens
        self.invariant_values = dict() # a dict of dict
        self.cap_node = False
        # for time, required_num_tokens
        self.tokens_existence_dir = dict()
        self.tokens_existence_time_holder = None

    def reset(self):
        self.invariant_values = dict() # a dict of dict
        self.cap_node = False
        # for time, required_num_tokens
        self.tokens_existence_dir = dict()
        self.tokens_existence_time_holder = None
        # added for abstract into formulae
        # may not needed

    def record_invariant_values(self, t_id, tokens):
        'happens at firing, which means type annotation have been updated'
        keys = self.p.type_annotations
        # keys = tokens[0].props()
        if len(self.invariant_values.keys()) == 0:
            for key in keys:
                self.invariant_values[key] = dict()
            self.invariant_values["token_time"] = dict()

        for key in self.invariant_values.keys():
            if not t_id in self.invariant_values[key]:
                self.invariant_values[key][t_id] = []
            self.invariant_values[key][t_id].append([])
        
        if tokens is None:
            return
        
        for token in tokens:
            self.invariant_values["token_time"][t_id][-1].append(token.ts)
            for key in token.props():
                if key in self.invariant_values:
                    self.invariant_values[key][t_id][-1].append(token.prop(key))
