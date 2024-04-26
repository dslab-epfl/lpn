import argparse
from lpn_def.lpn import lpn_def as menshen
from lpn_def.setup import lpn_init
from lpn_def.all_enums import CstStr
from lpnlang import lpn_sim
from lpnlang.lpn2sim import pylpn2cpp

def main(args):
    p_list, t_list, node_dict = menshen()
    lpn_init(args)
    cycles = lpn_sim(t_list, node_dict)
    print("latency = ", cycles) 

    pylpn2cpp(p_list, t_list, CstStr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog = 'vta sim',
                    description = 'simulates vta lpn',
                    epilog = '-b linked to benchmark file')
    parser.add_argument("-b", "--benchmark",  type=str, default="")
    args = parser.parse_args()
    print(args)
    main(args)
