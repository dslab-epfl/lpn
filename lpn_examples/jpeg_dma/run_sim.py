import argparse
from lpnlang import lpn_sim
from lpnlang import dump_place_types, retrieve_place_types
from lpnlang.lpn2sim import pylpn2cpp
from jpeg_dma.lpn_def.all_enum import CstStr
from jpeg_dma.lpn_def.lpn import jpeg
from jpeg_dma.lpn_def.setup import setup

def main(args):
    translate = True
    p_list, t_list, node_dict, comps = jpeg()
    print(node_dict)
    if not translate:
        setup(args.img, node_dict)
        cycles = lpn_sim(t_list, node_dict, debug=False)
        dump_place_types(p_list, "place_types.txt")
        for p in p_list:
            print(p.id, len(p.tokens))
        for t in t_list:
            print(t.id, t.count)
        print("latency = ", cycles) 
    else:
        retrieve_place_types(p_list, "place_types.txt")
        pylpn2cpp(p_list, t_list, CstStr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog = 'vta sim',
                    description = 'simulates vta lpn',
                    epilog = '-b linked to benchmark file')
    parser.add_argument("-b", "--img",  type=str, default="test_imgs/420/medium.jpg")
    args = parser.parse_args()
    print(args)
    main(args)
