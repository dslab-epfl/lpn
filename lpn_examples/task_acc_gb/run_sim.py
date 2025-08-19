import json
import argparse
from lpnlang import lpn_sim
import sympy
from task_acc_gb.lpn_def.components import TaskGBAcc
from task_acc_gb.func_sim.GB import gb_example

def CreateTaskGBAcc(trace, max_concurrent_path=1, num_PEs_each_type=1):
    acc = TaskGBAcc("acc", max_concurrent_path, num_PEs_each_type, trace=trace)
    def init_p_list(t_list):
        p_set = set()
        for t in t_list:
            for p in t.p_input:
                p_set.add(p)
            for p in t.p_output:
                p_set.add(p)
        return list(p_set) 

    t_list = acc.transitions()
    p_list = init_p_list(t_list)
    node_dict = {}
    for p in p_list:
        node_dict[p.id] = p 
    for t in t_list:
        node_dict[t.id] = t 
    return acc, p_list, t_list, node_dict

def main(args):
    paths, func_sim_trace = gb_example()
    print(func_sim_trace[0]["poly_stats"])
    exit(0)
    #     func_sim_trace[key] = {}

    for concurrency in [1, 2, 3]:
        for num_PE in [2, 4, 6, 8, 16, 32]:   
            acc, p_list, t_list, node_dict = CreateTaskGBAcc(func_sim_trace, concurrency, num_PE)
            acc.setup_path(paths)    
            acc.init_places()
            latency = lpn_sim(t_list, node_dict, debug=False, wait=50000)
            print(f"latency:{latency} config concurrency: {concurrency} num_PE{num_PE}")

    # for p in p_list:
    #     if len(p.tokens) > 0:
    #         print(p.id, len(p.tokens))
    #     if p.id == "task_dispatcher.task_buffer":
    #         for tk in p.tokens:
    #             print(tk.dict_items())



parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
parser.add_argument("-b", "--benchmark",  type=str, default="")
args = parser.parse_args()
main(args)

