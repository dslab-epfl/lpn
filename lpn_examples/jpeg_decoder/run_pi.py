import json
import argparse
from lpnlang import lpn_sim
from lpnlang.lpn2pi import lpn_pi
from lpnlang import retrieve_place_types
from lpnlang.symbex import lpn2symlpn, log_out_as_one_class
from lpnlang import retrieve_place_types
from lpn_def.sim import JPEG
from lpn_def.symb_sim import symbolic_setup

def main(args):

    'this step is to infer place types'
    p_list, t_list, node_dict = JPEG()
    retrieve_place_types(p_list, "place_types.txt")
    if args.symbex:
        'setup input domain'
        symbolic_setup(p_list, t_list, node_dict, args.num_blocks)    
    
        'generate cpp lpn for symbex'
        lpn2symlpn(p_list, t_list, None)

    if args.pi:    
        'comes back'
        lpn_pi(p_list, t_list, node_dict, 
               input_name='img', 
               PATH_TO_CLASSES='LPNCPP_KLEE/classes', 
               name_map={"sum_symref": "sum_non_zero"},
               setup_func_path = "lpn_def",
               iterations=10,
               repeatitive=True
        )
  
parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
parser.add_argument("-nb", "--num_blocks",  type=int, default=6)
parser.add_argument("-s", "--symbex",  type=bool, default=False)
parser.add_argument("-pi", "--pi",  type=bool, default=False)
args = parser.parse_args()
main(args)

