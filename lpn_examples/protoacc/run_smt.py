import json
import argparse
from lpnlang import lpn_sim
from lpnlang.symbex import lpn2symlpn
from lpnlang.lpn2smt import lpn_smt
from lpnlang import dump_place_types, retrieve_place_types
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

        symbolic_setup(p_list, t_list, node_dict, messages)    
    
        'generate cpp lpn for symbex'
        lpn2symlpn(p_list, t_list, CstStr)

    if args.smt:    
        'comes back'
        smt_objective = {
            'type' : 'OPT',
            'maximize' : True,
            'minimize' : False,
            'target_place' : 'pwrite_mem_resp',
            'constraints': [
                ("sum_lt", 1000) # total non scalar is less than 1000 bytes
            ]
        }

        # smt_objective = {
        #     'type' : 'SAT',
        #     'bound' : 200,
        #     'bound_type' : 'lower',
        #     'target_place' : 'pwrite_mem_resp'
        # }

        lpn_smt(p_list, t_list, node_dict,
               PATH_TO_CLASSES='LPNCPP_KLEE/classes',
               smt_obj=smt_objective
        )

parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
parser.add_argument("-b", "--benchmark",  type=str, default="")
parser.add_argument("-s", "--symbex",  type=bool, default=False)
parser.add_argument("-smt", "--smt",  type=bool, default=False)
args = parser.parse_args()
main(args)

