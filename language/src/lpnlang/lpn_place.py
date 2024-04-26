from typing import List
from collections import deque
from .lpn_token import Token
from .lpn_extension import Shadowable

class Place(Shadowable):
    def __init__(self, id: str):
        super().__init__()
        self.id = id
        self.tokens = deque()
        self.tokens_init = deque()
        self.type_annotations = []
        'mode 0 is normal sim mode'
        'mode 1 is for lpn2pi or lpn2smt'
        self.mode = 0
    
    def reset(self, keep_type=True):
        if not keep_type:
            self.type_annotations = []
        self.tokens.clear()
        self.tokens_init.clear()
        super().reset()
    
    def assign_marking(self, marking: List[Token], record_init=True):
        if len(marking) == 0:
            return
        self.tokens = marking.copy()
        if record_init:
            self.tokens_init = marking.copy()
        self.type_annotations = marking[0].props()

    def push_token(self, tk: Token):
        if len(self.type_annotations) == 0:
            self.type_annotations = tk.props()
        else:
            assert(set(self.type_annotations) == set(tk.props()))
        self.tokens.append(tk)
    
    def token_len(self):
        return len(self.tokens)

    def __repr__(self):
        return f"Place<{self.id}, {len(self.tokens)}, {self.type_annotations}>\n"

