
from typing import Callable, List, Any
from collections import deque
from .lpn_token import Token
from .lpn_place import Place
from .lpn_expr import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from .lpn_extension import Shadowable

class Transition(Shadowable):
    def __init__(self, 
                    id:str = None, 
                    delay_func:DelayFunc = None,
                    pi: List[Place] = None, 
                    pi_w: List[InWeightFunc] = None, 
                    po: List[Place] = None, 
                    po_w: List[OutWeightFunc] = None,
                    pi_guard: List[GuardFunc] = None, 
                    pi_w_threshold: List[ThresholdFunc]= None, 
                    pip: DelayFunc = None):
        super().__init__()
        self.id = id
        self.delay_f = delay_func
        self.p_input = [] if pi is None else pi
        self.p_output = [] if po is None else po
        self.pi_w = [] if pi_w is None else pi_w
        self.po_w = [] if po_w is None else po_w
        self.pi_guard = [] if pi_guard is None else pi_guard
        self.pi_w_threshold = [] if pi_w_threshold is None else pi_w_threshold
        self.pip = pip 
        self.pip_place = Place(f"{id}_pip")
        self.pip_place.assign_marking(deque([Token()]))

        self.binding = dict()
        self.delay_event = []
        self.time = 0
        self.count = 0
        self.last_ft = 0
        self.disabled = False
    
    def reset(self):
        self.time = 0
        self.last_ft = 0
        self.count = 0
        self.disabled = False

        self.binding.clear()
        self.delay_event.clear()
        self.pip_place.reset()
        self.pip_place.assign_marking(deque([Token()]))
        super().reset()
      
    
