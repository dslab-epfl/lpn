import os
from collections import deque
import re
from ..lpn_token import Token
from .extension  import IntSymbolPI as IntSymbol

def ls_files_in_directory(directory):
    """
    Reads the content of each file in the specified directory.

    Parameters:
    directory (str): The path to the directory containing the files.

    Returns:
    filenames: 
    """
    file_paths = []

    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"The directory {directory} does not exist.")
        return file_paths

    # List all files in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        # Check if it's a file and not a directory
        if os.path.isfile(filepath):
            file_paths.append(filepath)

    return file_paths


def input_classes(directory:str):
    """
    Parameters: 
    directory(str): the path to classes files

    Returns:
    classes ([place_tokens]): a list of place_tokens, where each place_tokens contains the place_id and corresponding fake tokens.
    """
    class_files = ls_files_in_directory(directory)
    classes = {}
    seqs = {}
    for input_class_file in class_files:
        if "class." in input_class_file:
            number = input_class_file.split(".")[-1]
            classes[number] = lpnsetup_with_input_class(input_class_file)
        elif "seq." in input_class_file:
            number = input_class_file.split(".")[-1]
            seqs[number] = parse_seqs(input_class_file)
    
    return classes, seqs

def parse_seqs(input_file):
    """
    Parameters:
    input_file (str): The path to the input file.

    Returns:
    seqs (list): A list of transition id parsed from the input file.
    """
    seqs = []
    with open(input_file, "r") as f:
        for line in f.readlines():
            seqs.append(line.strip())
    return seqs

def parse_ranges(ranges_str):
    if ranges_str == "NULL":
        return None
    return list(map(int, re.findall(r'\d+', ranges_str)))

def lpnsetup_with_input_class(input_class_file):
    """
    Args:
    input_class_file (str): path to input class file

    Returns:
    place_tokens (dir) : a dictionary where keys are place ids, and values are queues of fake tokens;
                         In fake tokens, the dir contains property, and (sample_value, symbol_name, symbolic_range).
                         symbol_name is used by lpn2pi. 
                         symbolic_range is used by lpn2smt. 
    """
    place_tokens = {}
    current_place_id = None
    current_token = None
    tk_count = 0
    with open(input_class_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith("==="):
                continue
            if line.startswith("=="):
                if current_token != None:
                    place_tokens[current_place_id].append(current_token)
                # tk_count = 0
                current_token = None
                current_place_id = line.split()[-1]
                place_tokens[current_place_id] = deque()
            elif line.startswith("="):
                if current_token:
                    # tk_count += 1
                    place_tokens[current_place_id].append(current_token)
                # could be empty
                current_token = Token()
            elif line.startswith("property"):
                parts = line.split(';')
                name = parts[0].split(':')[1]
                sample = int(parts[1].split(":")[1])
                ranges = parse_ranges(parts[2].split(":")[1])
                if ranges is None:
                    current_token.add_prop(name, (sample, None, None))
                else:
                    current_token.add_prop(name, (sample, f"SYMREF{tk_count}", ranges))
                    tk_count += 1

        # Add the last token for the last place_id
        if current_token:
            place_tokens[current_place_id].append(current_token)

    return place_tokens

def places_marking_setup(place_dir, place_tokens):
    symb_list, value_list = [], []
    for pid, tokens in place_tokens.items():
        new_tokens_queue = deque()
        for tk in tokens:
            new_tk = Token()
            for key, value in tk.dict_items():
                sample, symrefname, ranges = value
                if ranges == None:
                    new_tk.add_prop(key, IntSymbol(sample))
                else:
                    # print("symrefname", symrefname)
                    new_tk.add_prop(key, IntSymbol(sample, ranges[0], ranges[1], symrefname))
                    symb_list.append(new_tk.prop(key).symref())
                    value_list.append(sample)
            new_tokens_queue.append(new_tk)
        place_dir[pid].assign_marking(new_tokens_queue)
    return symb_list, value_list

def match_class(p_list, one_class):
    symb_list = []
    value_list = []
    for p in p_list:
        if p.id not in one_class:
            if len(p.tokens) > 0:
                print("ERROR: extra place ", p.id, len(p.tokens))
                return False, None, None
            continue
        cp_tokens = one_class[p.id]
        if len(p.tokens) != len(cp_tokens):
            return False, None, None
        for pt, cpt in zip(p.tokens, cp_tokens):
            for _property in pt.props():
                if isinstance(pt.prop(_property), IntSymbol):
                    pt_value = pt.prop(_property).value
                else:
                    pt_value = pt.prop(_property)
                sample, symb_name, ranges = cpt.prop(_property)
                if ranges is None:
                    if sample != pt_value:
                        print("ERROR: sample value not match at ", p.id, _property, sample, pt_value)
                        return False, None, None
                else:
                    if not( pt_value <= ranges[1] and pt_value >= ranges[0] ):
                        print("ERROR: sample value not in range at ", p.id, _property, ranges, pt_value)
                        return False, None, None
                    else:
                        symb_list.append(symb_name)
                        value_list.append(pt_value)
    # print("found class")
    return True, symb_list, value_list

def detect_class(p_list, input_class_dir):
    classes, _ = input_classes(input_class_dir)
    for i, (class_id, one_class) in enumerate(classes.items()):
        match, symb_list, value_list = match_class(p_list, one_class)
        if match:
            return i ,symb_list, value_list
    return None, None, None
