from collections import deque
from lpnlang import Token
from lpnlang import createIntSymbol
import random
from lpn_def.funcs.lpn_enum import CstStr, MetaInfoTranslate

symb_control_tokens = deque()
symb_fields_meta_tokens = deque()
symb_unit_tokens = deque()
CNT = 0
def clear_message_trace():
    symb_control_tokens.clear()
    symb_fields_meta_tokens.clear()
    symb_unit_tokens.clear()


def parse_control_tokens(messages, control_count=0):
    if isinstance(messages, list):
        for message in messages:
            parse_control_tokens_per_message(message, control_count, depth=0)
    else:
        parse_control_tokens_per_message(messages, control_count, depth=0)

def parse_control_tokens_per_message(message, control_count=0, depth=-1):
    continuous_fields_count = 0
    
    if depth == 0:
        type_info = CstStr.END_OF_MESSAGE_TOP_LEVEL
    else:
        type_info = CstStr.END_OF_MESSAGE

    field_info = {
        "type": type_info,
        "is_repeated": False,
        "data": [1]
    }
    message["f0"] = field_info
    # only works after python3.7 insertion order of dict is important
    for field, field_info in message.items():
        field_info["type"] = MetaInfoTranslate(field_info["type"])
        field_type = field_info['type']
        if field_type == CstStr.SUBMESSAGE:  # Submessage
            # Close any previous continuous field tokens
            if continuous_fields_count > 0:
                while continuous_fields_count > 0:
                    token_range = min(continuous_fields_count, 32)
                    symb_control_tokens.append(Token({"type": CstStr.NONSUBMESSAGE, "control_range": token_range}))
                    continuous_fields_count -= token_range

            # Add submessage token
            symb_control_tokens.append(Token({"type": CstStr.SUBMESSAGE, "control_range": 0}))
            
            # Recursive call for submessage
            parse_control_tokens_per_message(field_info['data']) 
            
            # End of submessage
            # control_tokens.append(Token({"type": CstStr.SUBMESSAGE, "control_range": -1}))  
        else:
            # Increment the continuous field counter
            continuous_fields_count += 1

    # Handle any remaining continuous fields
    while continuous_fields_count > 0:
        token_range = min(continuous_fields_count, 32)
        symb_control_tokens.append(Token({"type": CstStr.NONSUBMESSAGE, "control_range": token_range}))
        continuous_fields_count -= token_range

def parse_fields_and_units(messages):
    if isinstance(messages, list):
        for message in messages:
            parse_fields_and_units_per_message(message, depth=0)
    else:
        parse_fields_and_units_per_message(messages, depth=0)

def parse_fields_and_units_per_message(message,depth=-1):
    
    if depth == 0:
        type_info = CstStr.END_OF_MESSAGE_TOP_LEVEL
    else:
        type_info = CstStr.END_OF_MESSAGE

    field_info = {
        "type": type_info,
        "is_repeated": False,
        "data": [1]
    }
    message["f0"] = field_info
    for field, field_info in message.items():
        field_info["type"] = MetaInfoTranslate(field_info["type"])
        if field_info["type"] == CstStr.SUBMESSAGE:
            parse_fields_and_units_per_message(field_info["data"])  # Recursive call for submessage
        else:
            # Populate fields_meta_tokens
            symb_fields_meta_tokens.append(Token({"type": field_info["type"], "num": len(field_info["data"])}))
            # Populate unit_tokens
            if field_info["type"] == CstStr.NONSCALAR:
                for v in field_info["data"]:
                    global CNT
                    symb_unit_tokens.append(Token({"bytes": createIntSymbol(v, 0, 10000000, f"bytes{CNT}")}))
                    CNT += 1
            else:
                for v in field_info["data"]:
                    symb_unit_tokens.append(Token({"bytes": v}))