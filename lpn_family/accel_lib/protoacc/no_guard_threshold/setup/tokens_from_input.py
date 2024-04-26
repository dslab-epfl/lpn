
from parse_message import parse_control_tokens, parse_fields_and_units


def tokens_from_input(messages):
    """
    Produce tokens from input

    Args:
        messages ([json]): The protobuf messages.

    Returns:
        place_tokens_dict (dict): The dictionary contains the place id and corresponding tokens should put in that place due to inputs.
    """
    parse_control_tokens(messages)
    parse_fields_and_units(messages)
    pmessage_tasks_tokens_out = deque()
    pfields_meta_tokens_out = deque()
    pfields_tokens_out = deque()

    for _tk in control_tokens:
        pmessage_tasks_tokens_out.append(_tk)

    for _tk in fields_meta_tokens:
        pfields_meta_tokens_out.append(_tk)

    for _tk in unit_tokens:
        pfields_tokens_out.append(_tk)
    
    place_tokens_dict = {
        "pmessage_tasks" : pmessage_tasks_tokens_out,
        "pfields_meta" : pfields_meta_tokens_out,
        "pfields" : pfields_tokens_out,
    }

    return place_tokens_dict


