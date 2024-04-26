import json
import argparse
from lpnlang import lpn_sim
from lpnlang.lpn2pi import lpn_pi
from lpnlang import retrieve_place_types
from lpnlang.symbex import lpn2symlpn, log_out_as_one_class
from lpnlang import retrieve_place_types
from lpn_def.sim import Darwin
from lpn_def.symb_sim import symbolic_setup


def main(args):

    'this step is to infer place types'
    p_list, t_list, node_dict = Darwin()
    retrieve_place_types(p_list, "place_types.txt")
    'setup input domain'
    symbolic_setup(p_list, t_list, node_dict, None)    
    print("symbolic_setup done")
    log_out_as_one_class(p_list, f"tmp/classes/class.0000")
    if args.pi:    
        'comes back'
        lpn_pi(p_list, t_list, node_dict, 
               input_name='dna_pairs', 
               PATH_TO_CLASSES='tmp/classes', 
               name_map={
                   "SYMREF1": "query_len",
                   "SYMREF0": "ref_len",
                   "SYMREF2": "backtracking_steps",},
               setup_func_path = "lpn_def",
               iterations=1,
               repeatitive=False
        )
  
parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
parser.add_argument("-s", "--symbex",  type=bool, default=False)
parser.add_argument("-pi", "--pi",  type=bool, default=False)
args = parser.parse_args()
main(args)

