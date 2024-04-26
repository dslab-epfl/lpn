import json
import argparse
from lpnlang import lpn_sim
from lpnlang.lpn2sim import pylpn2cpp
from lpnlang import dump_place_types, retrieve_place_types
import sympy
from lpn_def.sim import lpn_def as ProtoaccDefOnly
from lpn_def.sim import setup
from lpn_def.funcs.lpn_enum import CstStr

def main(args):

    with open(f'hyperprotobench_processed/{args.benchmark}-ser.json', 'r') as f:
        messages = json.load(f)

    p_list, t_list, node_dict = ProtoaccDefOnly()
    setup(p_list, t_list, node_dict, messages)    
    retrieve_place_types(p_list, "place_types.txt")
    pylpn2cpp(p_list, t_list, CstStr)


parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
parser.add_argument("-b", "--benchmark",  type=str, default="")
args = parser.parse_args()
main(args)

