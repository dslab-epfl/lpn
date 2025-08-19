import argparse
from vta_with_dma.lpn_def.lpn import vta
from vta_with_dma.lpn_def.setup import setup
from lpnlang import lpn_sim
from lpnlang import dump_place_types, retrieve_place_types
from lpnlang.lpn2sim import pylpn2cpp
from vta_with_dma.lpn_def.all_enum import CstStr

def main(args):
    translate = True
    p_list, t_list, node_dict, comps = vta()
    if not translate:
        setup(comps, node_dict, args.benchmark)
        cycles = lpn_sim(t_list, node_dict, debug=True)
        dump_place_types(p_list, "place_types.txt")
        for p in p_list:
            print(p.id, len(p.tokens))
        print("latency = ", cycles) 
    else:
        retrieve_place_types(p_list, "place_types.txt")
        pylpn2cpp(p_list, t_list, CstStr)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog = 'vta sim',
                    description = 'simulates vta lpn',
                    epilog = '-b linked to benchmark file')
    parser.add_argument("-b", "--benchmark",  type=str, default="reference.insns")
    args = parser.parse_args()
    print(args)
    main(args)
