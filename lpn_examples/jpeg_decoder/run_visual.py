import argparse
from lpn_def.sim import JPEG, setup
from lpnlang import lpn_sim
from lpnlang.lpn2visual import lpn_visual_video

def main(args):
    p_list, t_list, node_dict = JPEG()
    setup(p_list, t_list, node_dict, args.image)    
    lpn_visual_video(p_list, t_list, steps=1000)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog = 'JPEG visual',
                    description = 'simulates JPEG lpn',
                    epilog = '-b linked to benchmark file')
    parser.add_argument("-img", "--image",  type=str, default="test_imgs/8x8/49.jpg")
    args = parser.parse_args()
    print(args)
    main(args)
