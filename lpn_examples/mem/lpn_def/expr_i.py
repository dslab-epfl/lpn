import lpnlang 
from lpnlang import Place, Transition, Token
from lpnlang import InWeightFunc, DelayFunc, OutWeightFunc, GuardFunc, ThresholdFunc
from lpnlang import prop_value

take_1_token = InWeightFunc("take_1_token")
@take_1_token.install
def number_of_token(binding):
    return 1 

take_dep_pop_next = InWeightFunc("take_dep_pop_next", dependent_place=Place)
@take_dep_pop_next.install
def number_of_token(binding, dependent_place):
    if(prop_value(binding, dependent_place, 0, "pop_next") == 1):
        return 1
    else:
        return 0
    
take_dep_pop_prev = InWeightFunc("take_dep_pop_prev", dependent_place=Place)
@take_dep_pop_prev.install
def number_of_token(binding, dependent_place):
    if(prop_value(binding, dependent_place, 0, "pop_prev") == 1):
        return 1
    else:
        return 0

take_readLen = InWeightFunc("take_readLen", dependent_place=Place)
@take_readLen.install
def number_of_token(binding, dependent_place):
    # this dependences have to go away
    return prop_value(binding, dependent_place, 0, "insn_count")

# p1 = Place("p1")
# test = take_readLen(dependent_place=p1)
# binding=dict()
# binding["p1.0.insn_count"] = 10
# a = test(binding)
# print(a)

take_some_token = InWeightFunc("take_some_token", number=int)
@take_some_token.install
def number_of_token(number):
    return number 