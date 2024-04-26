import json
import argparse
from lpnlang import lpn_sim
from lpnlang.symbex import lpn2symlpn
from lpnlang.lpn2pi import lpn_pi
from lpnlang import IntSymbol
from lpnlang import dump_place_types, retrieve_place_types
import sympy
from lpn_def.sim import lpn_def as ProtoaccDefOnly
from lpn_def.sim import setup
from lpn_def.symb_sim import symbolic_setup
from lpn_def.funcs.lpn_enum import CstStr

def main(args):
    'this step is to infer place types'
    p_list, t_list, node_dict = ProtoaccDefOnly()
    retrieve_place_types(p_list, "place_types.txt")
    if args.symbex:
        # with open(f'hyperprotobench_processed/{args.benchmark}-ser.json', 'r') as f:
        with open(f'lpn_message.json', 'r') as f:
            messages = json.load(f)

        'setup input domain'
        symbolic_setup(p_list, t_list, node_dict, messages)    
    
        'generate cpp lpn for symbex'
        lpn2symlpn(p_list, t_list, CstStr)

    if args.pi:    
        'comes back'
        lpn_pi(p_list, t_list, node_dict, 
               input_name='msg', 
               PATH_TO_CLASSES='LPNCPP_KLEE/classes', 
               name_map={"sum_symref": "sum_var_bytes"},
               setup_func_path = "lpn_def"
        )
  
parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
parser.add_argument("-b", "--benchmark",  type=str, default="")
parser.add_argument("-s", "--symbex",  type=bool, default=False)
parser.add_argument("-pi", "--pi",  type=bool, default=False)
args = parser.parse_args()
main(args)

