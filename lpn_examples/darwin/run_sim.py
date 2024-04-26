import json
import argparse
from lpnlang import lpn_sim, dump_place_types
import sympy
from lpn_def.sim import Darwin, setup

def main(args):

    p_list, t_list, node_dict = Darwin()
    ref = args.ref
    qry = args.query   
    setup(p_list, t_list, node_dict, [ref, qry])    
    latency = lpn_sim(t_list, node_dict)
    dump_place_types(p_list, "place_types.txt")
    print(latency)


parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
parser.add_argument("-ref", "--ref",  type=str, default="")
parser.add_argument("-query", "--query",  type=str, default="")
args = parser.parse_args()
main(args)

