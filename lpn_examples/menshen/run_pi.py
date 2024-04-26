import os
import argparse
from lpnlang import lpn_sim
from lpnlang.symbex import lpn2symlpn, log_out_as_one_class
from lpnlang.lpn2pi import lpn_pi
from lpnlang import dump_place_types, retrieve_place_types
from lpn_def.lpn import lpn_def as menshen
from lpn_def.setup import lpn_init
from lpn_def.symb_sim import symbolic_setup
from lpn_def.all_enums import CstStr


def main(args):

    'this step is to infer place types'
    p_list, t_list, node_dict = menshen()
    if not os.path.exists("place_types.txt"):
        lpn_init(args)
        lpn_sim(t_list, node_dict)
        dump_place_types(p_list, "place_types.txt")
    
    retrieve_place_types(p_list, "place_types.txt")

    # if args.symbex:
    'setup input domain'
    symbolic_setup(p_list, t_list, node_dict, args)    
    'generate cpp lpn for symbex'
    # lpn2symlpn(p_list, t_list, CstStr)
    log_out_as_one_class(p_list, f"LPNCPP_KLEE/classes/class.0000")

    if args.pi:    
        'comes back'
        lpn_pi(p_list, t_list, node_dict, 
               input_name='pkts', 
               PATH_TO_CLASSES='LPNCPP_KLEE/classes', 
               name_map={},
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

