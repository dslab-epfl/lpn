from collections import deque
from lpnlang import Place, Transition, Token
from .places import *
from .parse_out import collect_insns, collect_dependency

def empty_tokens(x):
    new_queue = deque()
    [new_queue.append(Token()) for i in range(x)]
    return new_queue

def lpn_init(args):
    # l2c, c2l, c2s, s2c = collect_dependency(f"/home/jiacma/npc/tvm/3rdparty/vta-hw/src/tsim/small_petri_net/dump/{args.benchmark}.status")
    # l2c, c2l, c2s, s2c = collect_dependency(f"{args.benchmark}.status")
    # pcompute2store = VPlace("pcompute2store", empty_tokens(c2s))
    # pcompute2load = VPlace("pcompute2load", empty_tokens(c2l))
    # pstore2compute = VPlace("pstore2compute", empty_tokens(s2c))
    # pload2compute = VPlace("pload2compute", empty_tokens(l2c))

    pcompute_cap.assign_marking(empty_tokens(512)) 
    pload_cap.assign_marking(empty_tokens(512)) 
    pstore_cap.assign_marking(empty_tokens(512))

    # all_inst = collect_insns(f"/home/jiacma/npc/tvm/3rdparty/vta-hw/src/tsim/small_petri_net/dump/{args.benchmark}")
    all_inst = collect_insns(f"{args.benchmark}")
    numInst = deque() 
    numInst.append(Token({"total_insn":len(all_inst)}))
    print("total insns ", len(all_inst))
    plaunch.assign_marking(numInst)
    pnumInsn.assign_marking(all_inst)
    pcontrol.assign_marking(empty_tokens(1))
