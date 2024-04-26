from collections import deque
from place_transition import Token
import random

control_tokens = deque()
fields_meta_tokens = deque()
unit_tokens = deque()

def clear_message_trace():
    control_tokens.clear()
    fields_meta_tokens.clear()
    unit_tokens.clear()
    symb_list.clear()
    bytes_list.clear()
    global COUNT
    COUNT=0


def parse_control_tokens(messages, control_count=0):
    if isinstance(messages, list):
        for message in messages:
            parse_control_tokens_per_message(message, control_count, depth=0)
    else:
        parse_control_tokens_per_message(messages, control_count, depth=0)

def parse_control_tokens_per_message(message, control_count=0, depth=-1):
    continuous_fields_count = 0
    
    if depth == 0:
        type_info = 'end_of_message_top_level'
    else:
        type_info = 'end_of_message'

    field_info = {
        "type": type_info,
        "is_repeated": False,
        "data": [1]
    }
    message["f0"] = field_info
    # only works after python3.7 insertion order of dict is important
    for field, field_info in message.items():
        field_type = field_info['type']
        
        if field_type == 'submessage':  # Submessage
            # Close any previous continuous field tokens
            if continuous_fields_count > 0:
                while continuous_fields_count > 0:
                    token_range = min(continuous_fields_count, 32)
                    control_tokens.append(Token({"type": "non-submessage", "control_range": token_range}))
                    continuous_fields_count -= token_range

            # Add submessage token
            control_tokens.append(Token({"type": "submessage", "control_range": 0))
            
            # Recursive call for submessage
            parse_control_tokens_per_message(field_info['data']) 
            
            # End of submessage
            # control_tokens.append(Token({"type": "submessage", "control_range": -1}))  
        else:
            # Increment the continuous field counter
            continuous_fields_count += 1

    # Handle any remaining continuous fields
    while continuous_fields_count > 0:
        token_range = min(continuous_fields_count, 32)
        control_tokens.append(Token({"type": "non-submessage", "control_range": token_range}))
        continuous_fields_count -= token_range

def parse_fields_and_units(messages):
    if isinstance(messages, list):
        for message in messages:
            parse_fields_and_units_per_message(message, depth=0)
    else:
        parse_fields_and_units_per_message(messages, depth=0)

def parse_fields_and_units_per_message(message,depth=-1):
    
    if depth == 0:
        type_info = 'end_of_message_top_level'
    else:
        type_info = 'end_of_message'

    field_info = {
        "type": type_info,
        "is_repeated": False,
        "data": [1]
    }
    message["f0"] = field_info
    for field, field_info in message.items():
        if field_info["type"] == 'submessage':
            parse_fields_and_units_per_message(field_info["data"])  # Recursive call for submessage
        else:
            # Populate fields_meta_tokens
            fields_meta_tokens.append(Token({"type": field_info["type"], "num": len(field_info["data"])}))
            
            # Populate unit_tokens
            for v in field_info["data"]:
                unit_tokens.append(Token({"bytes": v}))
