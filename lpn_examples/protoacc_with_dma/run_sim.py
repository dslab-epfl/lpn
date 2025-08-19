import json
import argparse
from lpnlang import lpn_sim
import sympy
from lpnlang import dump_place_types, retrieve_place_types
from lpnlang.lpn2sim import pylpn2cpp
from protoacc_with_dma.lpn_def.funcs.lpn_enum import CstStr
# from lpn_def.sim import lpn_def as ProtoaccDefOnly
from protoacc_with_dma.lpn_def.sim import ProtoaccWithMsg, ProtoaccWithMsgNoSetup, SetupWithMsg
from protoacc_with_dma.lpn_def.sim import setup
from lpnlang.lpn2visual import lpn_visualize

def main(args):
    if False:
        # with open(f'../protoacc/hyperprotobench_processed/{args.benchmark}-ser.json', 'r') as f:
        with open(f'../protoacc/hyperprotobench_processed/test.json', 'r') as f:
        # with open(f'/tmp/zurvan_protoacc_output.json', 'r') as f:
        # with open(f'./run_message.json', 'r') as f:
            messages = json.load(f)

        # with open(f'lpn_message.json', 'r') as f:
        #     messages = json.load(f)
        p_list, t_list, node_dict, comps = ProtoaccWithMsgNoSetup()
        SetupWithMsg(comps, messages)

        # p_list, t_list, node_dict = ProtoaccWithMsg(messages)    
        latency = lpn_sim(t_list, node_dict, debug=False)
        # dump_place_types(p_list, "place_types.txt")
        for p in p_list:
            # if "dma" in p.id:
            print(p.id, len(p.tokens))
        print(" ============ ")
        for t in t_list:
            print(t.id, t.count)
        print(latency)

    else:
        p_list, t_list, node_dict, comps = ProtoaccWithMsgNoSetup()
        retrieve_place_types(p_list, "place_types.txt")
        lpn_visualize(p_list, t_list)
        # pylpn2cpp(p_list, t_list, CstStr)

   

parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
parser.add_argument("-b", "--benchmark",  type=str, default="bench0")
args = parser.parse_args()
main(args)

