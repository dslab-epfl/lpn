from sympy import Max
from ..lpn_token import Token
from .extension import IntSymbolPI as IntSymbol
from .extension import FakePlace
from .pi_simulate import p_accept, p_fire, p_enabled_token_time, p_check_token_requirement
from .helper import symref

out_place = FakePlace()


def t_extend_binding(p, num_of_tokens, binding):
    if num_of_tokens <= 0:
        return binding
    if len(p.tokens) == 0:
        return binding
    keys = p.tokens[0].props()
    for i in range(num_of_tokens):
        for key in keys:
            binding[f"{p.id}.{i}.{key}"] = p.tokens[i].prop(key)

    return binding

def prepare_binding(self):
    binding = {}
    for p in self.p_input:
        binding[f"{p.id}.tk_len"] = len(p.tokens)
    
    for i, p in enumerate(self.p_input):
        if self.pi_w_threshold != None and len(self.pi_w_threshold) != 0 and int(self.pi_w_threshold[i](binding)) > 0:
            consume_num_tokens = int(self.pi_w_threshold[i](binding))
        else:
            consume_num_tokens = int(self.pi_w[i](binding))
            binding = t_extend_binding(p, consume_num_tokens, binding)
    return binding

def t_fire(self, binding):
    enable_time = 0
    if self.pip_place != None:
        enable_time = Max(p_enabled_token_time(self.pip_place, 1), enable_time)
        p_fire(self.pip_place, 1)
    else:
        assert(0)
    for p in self.p_input:
        i = self.p_input.index(p)
        consume_num_tokens = int(self.pi_w[i](binding))
        check_enable_tokens = consume_num_tokens
        if self.pi_w_threshold != None and len(self.pi_w_threshold) != 0 and int(self.pi_w_threshold[i](binding)) > 0:
            check_enable_tokens = int(self.pi_w_threshold[i](binding))
        enable_time = Max(p_enabled_token_time(p, check_enable_tokens), enable_time)
        if consume_num_tokens == 0 or consume_num_tokens == -2:
            continue
        p_fire(p, consume_num_tokens)
    return enable_time

def t_accept(self, binding, enabled_time):
    fire_time = symref(self.delay_f(binding)) + enabled_time 
    if self.pip is None:
        'pip_place reflects self time already'
        self.pip_place.push_token(Token(None, fire_time))
    else:
        self.pip_place.push_token(Token(None, enabled_time+self.pip(binding)))
    for p in self.p_output:
        i = self.p_output.index(p)
        self.po_w[i](binding, out_place)
        for tk in out_place.tokens:
            tk.ts = fire_time
            for key, value in tk.dict_items():
                if isinstance(value, int):
                    tk.set_prop(key, IntSymbol(value))
                elif isinstance(value, IntSymbol):
                    tk.set_prop(key, value)
                else:
                    tk.set_prop(key, IntSymbol(sym=value))
            p.push_token(tk)
        out_place.clear_tokens()

    return fire_time

def sync(self):
    binding = prepare_binding(self)
    enabled_time = t_fire(self, binding)
    fire_time = t_accept(self, binding, enabled_time)
    return fire_time


def lpn_walk_seq(t_list, node_dict, fire_seqs):
        last_ts_dict = {}
        for t_id in fire_seqs:
            'this sequences is timeless, so we need to find the maximum'
            fire_time = sync(node_dict[t_id])
            last_ts_dict[t_id] = fire_time
        fire_time = 0
        for t_id, ts in last_ts_dict.items():
            fire_time = Max(fire_time, ts)
        return fire_time         