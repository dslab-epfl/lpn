import numpy as np
from typing import List
from collections import deque
from ..lpn_token import Token
from ..lpn_place import Place
from .extension import IntSymbolPI as IntSymbol
from .extension import FakePlace
out_place = FakePlace()

def p_enabled_token_time(self, num_of_tokens: int):
    'inhibitor'
    num_of_tokens = int(num_of_tokens)
    if num_of_tokens == -2:
        return 0
    'no token required'        
    if num_of_tokens == 0:
        return 0
    return self.tokens[num_of_tokens-1].ts

def p_check_token_requirement(self, num_of_tokens: int):
    'inhibitor'
    if num_of_tokens == -2:
        return len(self.tokens) == 0
    return len(self.tokens) >= num_of_tokens

def p_fire(self, num_of_tokens: int):
    tokens = deque()
    for _ in range(num_of_tokens):
        tokens.append(self.tokens[0])
        self.tokens.popleft()
    return tokens

'''
since the output weight function already pushes tokens into output places, 
this accept is no longer used.
'''
def p_accept(self, tokens_queue: List[Token]):
    if tokens_queue == None:
        return 
    if len(self.type_annotations) == 0:
        self.type_annotations = tokens_queue[0].props()
    else:
        if set(self.type_annotations) != set(tokens_queue[0].props()):
            raise ValueError("pushed tokens have different types than the place.")
    all_tk = len(tokens_queue) 
    if len(self.tokens) != 0:
        assert( tokens_queue[0].t >= self.tokens[-1].t)
    for i in range(all_tk):
        self.tokens.append(tokens_queue.popleft())

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

def t_able_to_fire(self):
    able_to_fire = True
    time_list = []
    if self.pip_place != None:
        if not p_check_token_requirement(self.pip_place, 1):
            return False, 0
        else:
            time_list.append(p_enabled_token_time(self.pip_place, 1))
    
    for p in self.p_input:
        self.binding[f"{p.id}.tk_len"] = len(p.tokens)
    
    for i, p in enumerate(self.p_input):
        if self.pi_w_threshold != None and len(self.pi_w_threshold) != 0 and int(self.pi_w_threshold[i](self.binding)) > 0:
            consume_num_tokens = int(self.pi_w_threshold[i](self.binding))
        else:
            consume_num_tokens = int(self.pi_w[i](self.binding))
        if not p_check_token_requirement(p, consume_num_tokens):
            self.binding.clear()
            return False, 0
        else:
            time_list.append(p_enabled_token_time(p, consume_num_tokens))
            self.binding = t_extend_binding(p, consume_num_tokens, self.binding)
        if self.pi_guard is not None and len(self.pi_guard) != 0:
            pass_guard = self.pi_guard[i](self.binding)
            if pass_guard == False:
                self.binding.clear()
                return False, 0

    last_input_ready = max(time_list)
    return able_to_fire, last_input_ready

def t_fire(self):
    if self.pip_place != None:
        p_fire(self.pip_place, 1)
    for p in self.p_input:
        i = self.p_input.index(p)
        consume_num_tokens = int(self.pi_w[i](self.binding))
        if consume_num_tokens == 0 or consume_num_tokens == -2:
            p.record_invariant_values(self.id, None)
            continue
        tokens = p_fire(p, consume_num_tokens)
        # if p.id == ""
        p.record_invariant_values(self.id, tokens)

def t_accept(self, enabled_time, fire_time):
    self.binding["ts"] = fire_time
    if self.pip is None:
        self.pip_place.push_token(Token(None, fire_time))
    else:
        self.pip_place.push_token(Token(None, enabled_time+self.pip(self.binding)))
    for p in self.p_output:
        i = self.p_output.index(p)
        old_len = self.p_output[i].token_len()
        self.po_w[i](self.binding, out_place)
        for tk in out_place.tokens:
            new_tk = Token()
            new_tk.ts = fire_time
            for key, value in tk.dict_items():
                if isinstance(value, int):
                    new_tk.set_prop(key, IntSymbol(value))
                elif isinstance(value, IntSymbol):
                    new_tk.set_prop(key, value)
                else:
                    new_tk.set_prop(key, IntSymbol(sym=value))
            p.push_token(new_tk)
        out_place.clear_tokens()
    self.last_ft = fire_time

def t_delay(self):
    return int(self.delay_f(self.binding))

def t_trigger(self):
    if self.disabled:
        return 0
    if len(self.delay_event) != 0:
        return 0
    can_fire, enabled_time = t_able_to_fire(self)
    enabled_time = max(enabled_time, self.time)
    if len(self.delay_event)==0 and can_fire:
        delay_time = t_delay(self)
        mature_time = max(self.last_ft, enabled_time+delay_time)
        self.delay_event.append([mature_time, enabled_time])
        self.count += 1

    return can_fire 

def t_earliest_ts(self):
    if len(self.delay_event) > 0:
        return self.delay_event[0][0]
    else:
        return np.Inf

def t_sync(self, time, debug=False):
    if len(self.delay_event) == 0:
        self.time = time 
        return 1
    if time >= self.delay_event[0][0]:
        assert(time == self.delay_event[0][0])
        if debug:
            print("""commit={t_id} at {time}""".format(t_id=self.id, time=time))
        t_accept(self, self.delay_event[0][1], self.delay_event[0][0])
        t_fire(self)
        self.delay_event.pop(0)
    return 0

def min_fire_time(t_list):
    min_ts = np.Inf
    min_trans = None
    for t in t_list:
        t_earlist = t_earliest_ts(t)
        if min_ts > t_earlist:
            min_ts, min_trans = t_earlist, t
    return min_ts, min_trans
    
def all_enabled_trans(t_list, min):
    enabled_ts = []
    for t in t_list:
        if min == t_earliest_ts(t):
            enabled_ts.append(t)
    return enabled_ts

def lpn_sim(t_list, node_dict, debug=False, wait=100000000000, halt_cond_transition_id=None, repeat_before_halt=None):
    total = wait
    time = 0
    prev_time = 0
    while time < total :

        for t in t_list:
            t_trigger(t) 

        time, min_trans = min_fire_time(t_list)
        enabled_ts = all_enabled_trans(t_list, time)
        # for t in enabled_ts:
        #     print("enabled@", time, t.id)
        if time == np.Inf:
            print(" === no events === ")
            break
        prev_time = time
        for t in t_list:
            t_sync(t, time, debug=debug)

        if halt_cond_transition_id != None:
            if node_dict[halt_cond_transition_id].count == repeat_before_halt-1:
                node_dict[halt_cond_transition_id].disabled = True
            
    return prev_time
