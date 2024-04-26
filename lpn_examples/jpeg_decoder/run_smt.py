import json
import argparse
from lpnlang.symbex import lpn2symlpn
from lpnlang.lpn2smt import lpn_smt
from lpnlang import retrieve_place_types
from lpn_def.sim import JPEG
from lpn_def.symb_sim import symbolic_setup


def main(args):
    if args.num_blocks < 6:
        raise ValueError("num_blocks (YCbCr) must be at least 6 and a multiple of 6. 6 YCbCr block is turned into 4 RGB block")
    
    'this step is to infer place types'
    p_list, t_list, node_dict = JPEG()
    retrieve_place_types(p_list, "place_types.txt")
    if args.symbex:
        symbolic_setup(p_list, t_list, node_dict, args.num_blocks)    
    
        'generate cpp lpn for symbex'
        lpn2symlpn(p_list, t_list, None)

    if args.smt:    
        'comes back'
        smt_objective = {
            'type' : 'OPT',
            'maximize' : False,
            'minimize' : True,
            'target_place' : 'pdone',
            'constraints' : [
                ("avg_lt", 18),
                ("avg_gt", 16),
            ]
        }

        # smt_objective = {
        #     'type' : 'SAT',
        #     'bound' : 200,
        #     'bound_type' : 'lower',
        #     'target_place' : 'pdone'
        # }

        lpn_smt(p_list, t_list, node_dict,
               PATH_TO_CLASSES='LPNCPP_KLEE/classes',
               smt_obj=smt_objective
        )

parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
parser.add_argument("-nb", "--num_blocks",  type=int, default=6)
parser.add_argument("-s", "--symbex",  type=bool, default=False)
parser.add_argument("-smt", "--smt",  type=bool, default=False)
args = parser.parse_args()
main(args)

