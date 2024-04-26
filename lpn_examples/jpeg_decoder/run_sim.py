import json
import argparse
from lpnlang import lpn_sim, dump_place_types
import sympy
from lpn_def.sim import JPEG, setup

def main(args):

    p_list, t_list, node_dict = JPEG()    
    setup(p_list, t_list, node_dict, args.image)    
    latency = lpn_sim(t_list, node_dict)
    dump_place_types(p_list, "place_types.txt")
    print(latency)


parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
parser.add_argument("-img", "--image",  type=str, default="")
args = parser.parse_args()
main(args)

