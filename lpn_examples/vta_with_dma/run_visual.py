import argparse
from lpn_def.lpn import lpn_def as vta
from lpn_def.all_enum import CstStr
from lpn_def.setup import lpn_init
from lpnlang import lpn_sim
from lpnlang.lpn2sim import pylpn2cpp
from lpnlang.lpn2visual import lpn_visualize, lpn_visual_video

def main(args):
    p_list, t_list, node_dict = vta()
    lpn_init(args)
    # cycles = lpn_sim(t_list, node_dict)
    # lpn_visualize(p_list, t_list)
    lpn_visual_video(p_list, t_list, steps=1000)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog = 'vta sim',
                    description = 'simulates vta lpn',
                    epilog = '-b linked to benchmark file')
    parser.add_argument("-b", "--benchmark",  type=str, default="")
    args = parser.parse_args()
    print(args)
    main(args)
