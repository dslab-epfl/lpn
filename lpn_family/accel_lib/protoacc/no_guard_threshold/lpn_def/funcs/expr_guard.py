from collections import deque
from lpnlang import Token
from .funcs import pass_token, create_empty_token
from protoacc_lpn.funcs.lpn_enum import CstStr

def empty_guard():
    def guard(binding=None):
        return True
    return guard


def take_top_level(from_place):
    def guard(binding):
        if binding[f"{from_place.id}.0.end_of_top_level"].concrete() == 1:
            return True
        else:
            return False
    return guard

def take_non_top_level(from_place):
    def guard(binding):
        if binding[f"{from_place.id}.0.end_of_top_level"].concrete() == 0:
            return True
        else:
            return False
    return guard

def take_repeated_token(from_place):
    def guard(binding=None):
        if binding[f"{from_place.id}.0.num"].concrete() > 1:
            return True
        else:
            return False
    return guard

def take_scalar_token(from_place):
    def guard(binding=None):
        if MetaInfo.SCALAR.value  == binding[f"{from_place.id}.0.type"].concrete() and binding[f"{from_place.id}.0.num"].concrete() == 1:
            return True
        else:
            return False
    return guard

def take_non_scalar_token(from_place):
    def guard(binding=None):
        if MetaInfo.NONSCALAR.value  == binding[f"{from_place.id}.0.type"].concrete() and binding[f"{from_place.id}.0.num"].concrete() == 1:
            return True
        else:
            return False
    return guard

def take_non_zero_bytes(from_place):
    def guard(binding=None):
        bytes = binding[f"{from_place.id}.0.bytes"].concrete()
        if bytes == 0:
            return False
        else:
            return True
    return guard

def take_eom_token(from_place):
    def guard(binding):
        if (MetaInfo.END_OF_MESSAGE.value  == binding[f"{from_place.id}.0.type"].concrete() or MetaInfo.END_OF_MESSAGE_TOP_LEVEL.value  == binding[f"{from_place.id}.0.type"].concrete()) and binding[f"{from_place.id}.0.num"].concrete() == 1:
            return True
        else:
            return False
    return guard

def take_zero_bytes(from_place):
    def guard(binding=None):
        bytes = binding[f"{from_place.id}.0.bytes"].concrete()
        if bytes == 0:
            return True
        else:
            return False
    return guard


def take_field_index(from_place, index):
    def guard(binding=None):
        if binding == None or len(binding) == 0:
            return True
        if binding[f"{from_place.id}.0.field_index"].concrete() == index:
            return True
        else:
            return False
    return guard

def take_non_message_token():
    def guard(binding=None):
        if binding["pdescr_request_Q.0.type"].concrete() == MetaInfo.NONSUBMESSAGE.value :
            return True
        else:
            return False
    return guard


def take_message_token():
    def guard(binding=None):

        if binding["pdescr_request_Q.0.type"].concrete() == MetaInfo.SUBMESSAGE.value :
            return True
        else:
            return False
    return guard

def pass_message_token(from_place):
    def output_token(binding=None):
        is_msg = binding[f"{from_place.id}.0.type"].concrete() ==  MetaInfo.SUBMESSAGE.value 
        if is_msg:
            return pass_token(from_place, 1)(binding) 
        else:
            return None
    return output_token


def pass_non_message_token(from_place):
    def output_token(binding=None):
        is_msg = binding[f"{from_place.id}.0.type"].concrete() ==  MetaInfo.SUBMESSAGE.value 
        if not is_msg:
            return pass_token(from_place, 1)(binding) 
        else:
            return None
    return output_token
 

def pass_non_top_token(from_place):
    def output_token(binding=None):
        is_top = binding[f"{from_place.id}.0.end_of_top_level"].concrete() == 1
        if is_top:
            return None
        else:
            return pass_token(from_place, 1)(binding)
    return output_token

def pass_top_token(from_place):
    def output_token(binding=None):
        is_top = binding[f"{from_place.id}.0.end_of_top_level"].concrete() == 1
        if not is_top:
            return None
        else:
            return pass_token(from_place, 1)(binding)
    return output_token

def pass_eom(from_place):
    def output_token(binding=None):
        if (MetaInfo.END_OF_MESSAGE.value  == binding[f"{from_place.id}.0.type"].concrete() or MetaInfo.END_OF_MESSAGE_TOP_LEVEL.value  == binding[f"{from_place.id}.0.type"].concrete()) and binding[f"{from_place.id}.0.num"].concrete() == 1:
            return pass_token(from_place, 1)(binding)
        else:
            return None
    return output_token
   
def pass_scalar(from_place):
    def output_token(binding=None):
        if MetaInfo.SCALAR.value  == binding[f"{from_place.id}.0.type"].concrete() and binding[f"{from_place.id}.0.num"].concrete() == 1:
            return pass_token(from_place, 1)(binding)
        else:
            return None
    return output_token
    
def pass_non_scalar(from_place):
    def output_token(binding=None):
        if MetaInfo.NONSCALAR.value  == binding[f"{from_place.id}.0.type"].concrete() and binding[f"{from_place.id}.0.num"].concrete() == 1:
            return pass_token(from_place, 1)(binding)
        else:
            return None
    return output_token
    
def pass_repeated(from_place):
    def output_token(binding=None):
        if binding[f"{from_place.id}.0.num"].concrete() > 1:
            return pass_token(from_place, 1)(binding)
        else:
            return None
    return output_token
    

def pass_field_index_token(from_place, index):
    def output_token(binding=None):
        if binding[f"{from_place.id}.0.field_index"].concrete() == index:
            return create_empty_token(1)
        else:
            return None

    return output_token



def pass_field_index_add_one(from_place):
    def output_token(binding=None):
        cur_idx = binding[f"{from_place.id}.0.field_index"].concrete()
        tokens = deque()
        tokens.append( Token({"field_index": IntSymbol((cur_idx)%6+1)}) )
        # tokens.append( Token({"field_index": IntSymbol(1)}))
        return tokens
    return output_token

def pass_write_hold_cond(from_place):
    def output_token(binding=None):
        end_of_field = binding[f"{from_place.id}.0.end_of_field"].concrete()
        if end_of_field == 0:
            return None            
        else:
            return create_empty_token(1)
    return output_token

def pass_write_index_holder_cond(from_place, pass_token_place):
    def output_token(binding=None):
        end_of_field = binding[f"{from_place.id}.0.end_of_field"].concrete()
        if end_of_field == 0:
            return pass_token(pass_token_place, 1)(binding)     
        else:
            return None
    return output_token