from lpnlang import lpn_all_nodes
from DMA.lpn_def.dma_ports import *
from mem.lpn_def.expr_i import *
from mem.lpn_def.expr_o import *
from mem.lpn_def.expr_guard import *
from mem.lpn_def.delay_func import *
from mem.lpn_def.mem_func import *

class Memory(LPNClassBase):
    def __init__(self, id):
        super().__init__(id)
        memory_req_front = Place("memory_req_front")
        memory_req_cl = Place("memory_req_cl")
        memory_req_store = Place("memory_req_store")
        memory_resp_cl = Place("memory_resp_cl")
        memory_resp = Place("memory_resp")
        memory_inflight_cap = Place("memory_inflight_cap")
        inflight_cl_cnt = Place("inflight_cl_cnt")

        tprocess_mem_req_front = Transition(
            id = "tprocess_mem_req_front", 
            delay_func = con_delay(2), 
            pi=[memory_req_front], 
            pi_w=[take_1_token()], 
            po=[memory_req_store, memory_req_cl, inflight_cl_cnt], 
            po_w=[pass_token(memory_req_front, 1), pass_cl_token(memory_req_front), pass_cl_cnt(memory_req_front)], 
        )

        tlatency_sim = Transition(
            id = "tlatency_sim", 
            delay_func = con_delay(0), 
            pi=[memory_req_cl, memory_inflight_cap], 
            pi_w=[take_1_token(), take_1_token()], 
            po=[memory_resp_cl, memory_inflight_cap], 
            po_w=[pass_token(memory_req_cl, 1), pass_token(memory_inflight_cap, 1)], 
            # this pip decides the bandiwdth of the memory
            pip = con_delay(10),
        )

        tforge_mem_resp = Transition(
            id = "tforge_mem_resp",
            delay_func = delay_num_cl(inflight_cl_cnt), 
            pi=[memory_req_store, inflight_cl_cnt, memory_resp_cl], 
            pi_w=[take_1_token(), take_1_token(), take_cl_cnt(inflight_cl_cnt)], 
            po=[memory_resp], 
            po_w=[pass_token(memory_req_store, 1)], 
        )

        self.t_list = [tprocess_mem_req_front, tlatency_sim, tforge_mem_resp]
        self.p_list, _, self.node_dict = lpn_all_nodes(self.t_list)

    def init_places(self):
        def empty_tokens(x):
            new_queue = deque()
            [new_queue.append(Token()) for i in range(x)]
            return new_queue
        self.access("memory_inflight_cap").assign_marking(empty_tokens(64)) 
        