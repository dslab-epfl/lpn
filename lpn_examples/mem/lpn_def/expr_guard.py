import lpnlang 
from lpnlang import Place, Transition, Token
from lpnlang import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from lpnlang import prop_value

empty_guard = GuardFunc("empty_guard")
@empty_guard.install
def guard(binding):
    return True

take_opcode_token = GuardFunc("take_opcode_token", dependent_place=Place, opcode=int)
@take_opcode_token.install
def guard(binding, dependent_place, opcode):
    if prop_value(binding, dependent_place, 0, "opcode") != opcode:
        return False
    return True

take_subopcode_token = GuardFunc("take_subopcode_token", dependent_place=Place, subopcode=int)
@take_subopcode_token.install
def guard(binding, dependent_place, subopcode):
    # key not in binding, means the dependent place has no tokens ! 
    if prop_value(binding, dependent_place, 0, "subopcode") != subopcode:
        return False
    return True