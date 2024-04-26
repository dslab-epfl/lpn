import json
import argparse
from lpnlang import lpn_sim
import sympy
from lpn_def.sim import lpn_def as ProtoaccDefOnly
from lpn_def.sim import setup

def main(args):
    with open(f'hyperprotobench_processed/{args.benchmark}-ser.json', 'r') as f:
        messages = json.load(f)

    with open(f'lpn_message.json', 'r') as f:
        messages = json.load(f)
    
    p_list, t_list, node_dict = ProtoaccDefOnly()    
    setup(p_list, t_list, node_dict, messages)    
    latency = lpn_sim(t_list, node_dict)
    print(latency)


parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
parser.add_argument("-b", "--benchmark",  type=str, default="")
args = parser.parse_args()
main(args)

