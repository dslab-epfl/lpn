from lpnlang import lpn_all_nodes
from DMA.lpn_def.dma_ports import *
from vta_with_dma.lpn_def.expr_i import *
from vta_with_dma.lpn_def.expr_o import *
from vta_with_dma.lpn_def.expr_guard import *
from vta_with_dma.lpn_def.delay_func import *
from vta_with_dma.lpn_def.mem_func import *
from vta_with_dma.lpn_def.all_enum import CstStr

class VTA(LPNClassBase):
    def __init__(self, id, dma_read:DMAPortBase, dma_write:DMAPortBase):
        super().__init__(id)
        # three dma read ports
        read_put_port_0, read_get_port_0, self.p_memread_fifo_order, _ = dma_read.port(0)
        read_put_port_1, read_get_port_1, _, _ = dma_read.port(1)
        read_put_port_2, read_get_port_2, _, _ = dma_read.port(2)
        
        self.p_memread_put_list = [read_put_port_0, read_put_port_1, read_put_port_2]
        self.p_memread_get_list = [read_get_port_0, read_get_port_1, read_get_port_2]

        # one dma write port
        write_put_port_0, write_get_port_0, self.p_memwrite_fifo_order, _ = dma_write.port(0)
        self.p_memwrite_put_list = [write_put_port_0]
        self.p_memwrite_get_list = [write_get_port_0]

        load_insn_port, load_port, compute_port = 0, 1, 2
        
        store_port = 0

        pcompute2store = Place("pcompute2store")
        pcompute2load = Place("pcompute2load")
        pstore2compute = Place("pstore2compute")
        pload2compute = Place("pload2compute")
        pcompute_process = Place("pcompute_process");  
        pload_process = Place("pload_process");  
        pstore_process = Place("pstore_process");  
        pcompute_cap = Place("pcompute_cap") 
        pload_cap = Place("pload_cap") 
        pstore_cap = Place("pstore_cap")
        plaunch = Place("plaunch")
        psReadCmd = Place("psReadCmd")
        pnumInsn = Place("pnumInsn")
        psDrain = Place("psDrain") 
        pcontrol = Place("pcontrol")
        pcontrol_prime = Place("pcontrol_prime")
        pcompute_inst_q = Place("pcompute_inst_q")
        pcompute_done = Place("pcompute_done")
        pstore_inst_q = Place("pstore_inst_q")
        pstore_done = Place("pstore_done")
        pload_inst_q = Place("pload_inst_q")
        pload_done = Place("pload_done")

        t13 = Transition(
            id = "t13", 
            delay_func = con_delay(0), 
            pi=[plaunch],
            po=[psReadCmd],
            pi_w=[take_1_token()], 
            po_w=[output_insn_read_cmd(plaunch)],
        )

        load_insn_cmd = Place("load_insn_cmd")
        
        tload_insn_pre = Transition(
            id = "tload_insn_pre", 
            delay_func = con_delay(0),
            pi=[psReadCmd, pcontrol], 
            pi_w=[take_1_token(), take_1_token()], 
            po=[load_insn_cmd, self.p_memread_put_list[load_insn_port], self.p_memread_fifo_order], 
            po_w=[pass_token(psReadCmd, 1), mem_request(load_insn_port, CstStr.DMA_LOAD_INSN, 1), push_request_order(load_insn_port, 1)],

        )   

        tload_insn_post = Transition(
            id = "tload_insn_post",
            delay_func = con_delay(0),
            pi=[load_insn_cmd, pnumInsn, self.p_memread_get_list[load_insn_port]],
            pi_w=[take_1_token(), take_readLen(load_insn_cmd), take_1_token()],
            po=[psDrain, pcontrol_prime],
            po_w=[pass_var_token_readLen(pnumInsn, load_insn_cmd), pass_empty_token()]
        )

        t12 = Transition(
            id = "t12",
            delay_func = con_delay(1),
            pi=[pcontrol_prime],
            po=[pcontrol], 
            pi_w=[take_1_token()], 
            po_w=[pass_empty_token()], 
        ) 

        t14 = Transition(
            id = "t14",
            delay_func = con_delay(1),
            pi=[psDrain, pload_cap],
            po=[pload_inst_q],
            pi_w=[take_1_token(), take_1_token()],
            pi_guard=[take_opcode_token(psDrain, CstStr.LOAD), empty_guard()],
            po_w=[pass_token(psDrain, 1)], 
        )

        t15 = Transition(
            id = "t15",
            delay_func = con_delay(1), 
            pi=[psDrain, pcompute_cap], 
            po=[pcompute_inst_q], 
            pi_w=[take_1_token(), take_1_token()], 
            pi_guard=[take_opcode_token(psDrain,  CstStr.COMPUTE), empty_guard()],
            po_w=[pass_token(psDrain, 1)], 
        )

        t16 = Transition(
            id = "t16",
            delay_func = con_delay(1), 
            pi=[psDrain, pstore_cap], 
            po=[pstore_inst_q], 
            pi_w=[take_1_token(), take_1_token()], 
            pi_guard=[take_opcode_token(psDrain, CstStr.STORE), empty_guard()], 
            po_w=[pass_token(psDrain, 1)], 
        )

        tload_launch = Transition(
            id = "tload_launch", 
            delay_func = con_delay(0), 
            pi=[pload_inst_q, pcompute2load], 
            pi_w=[take_1_token(), take_dep_pop_next(pload_inst_q)], 
            po=[pload_process, self.p_memread_put_list[load_port], self.p_memread_fifo_order], 
            po_w=[pass_token(pload_inst_q, 1), mem_request_load_module(load_port, pload_inst_q), push_request_order_load_module(load_port, pload_inst_q)], 
        )

        tload_done = Transition(
            id = "load_done",
            delay_func = delay_load(pload_process), 
            pi=[pload_process, self.p_memread_get_list[load_port]], 
            pi_w=[take_1_token(), take_resp_token_load_module(pload_process)], 
            po=[pload_done, pload2compute, pload_cap], 
            po_w=[pass_empty_token(), output_dep_push_next(pload_process), pass_empty_token()], 
        ) 

        tstore_launch = Transition(
            id = "store_launch", 
            delay_func = con_delay(0), 
            pi=[pstore_inst_q, pcompute2store], 
            pi_w=[take_1_token(), take_dep_pop_prev(pstore_inst_q)], 
            po=[pstore_process, self.p_memwrite_put_list[store_port], self.p_memwrite_fifo_order], 
            po_w=[pass_token(pstore_inst_q, 1), mem_request_store_module(store_port, pstore_inst_q), push_request_order_store_module(store_port, pstore_inst_q)], 
        )

        tstore_done = Transition(
            id = "store_done",
            delay_func = delay_store(pstore_process), 
            pi=[pstore_process, self.p_memwrite_get_list[store_port]], 
            pi_w=[take_1_token(), take_resp_token_store_module(pstore_process)], 
            po=[pstore_done, pstore2compute, pstore_cap], 
            po_w=[pass_empty_token(), output_dep_push_prev(pstore_process), pass_empty_token()], 
        )

        tcompute_launch = Transition(
            id = "compute_launch", 
            delay_func = con_delay(0), 
            pi=[pcompute_inst_q, pstore2compute, pload2compute], 
            pi_w=[take_1_token(), take_dep_pop_next(pcompute_inst_q), take_dep_pop_prev(pcompute_inst_q)], 
            po=[pcompute_process, self.p_memread_put_list[compute_port], self.p_memread_fifo_order],
            po_w=[pass_token(pcompute_inst_q, 1), mem_request_compute_module(compute_port, pcompute_inst_q), push_request_order_compute_module(compute_port, pcompute_inst_q)]
        )

        tcompute_done = Transition(
            id = "compute_done",
            delay_func = delay_compute(pcompute_process),
            pi=[pcompute_process, self.p_memread_get_list[compute_port]], 
            pi_w=[take_1_token(), take_resp_token_compute_module(pcompute_process)], 
            po=[pcompute_done, pcompute2load, pcompute2store, pcompute_cap], 
            po_w=[pass_empty_token(), output_dep_push_prev(pcompute_process), output_dep_push_next(pcompute_process),  pass_empty_token()], 
        )

        self.t_list = [t13, tload_insn_pre, tload_insn_post,
        t12, t14, t15, t16, tload_launch, tload_done, tstore_launch, tstore_done, 
        tcompute_launch, tcompute_done]
        self.p_list, _, self.node_dict = lpn_all_nodes(self.t_list)

    def init_places(self):
        def empty_tokens(x):
            new_queue = deque()
            [new_queue.append(Token()) for i in range(x)]
            return new_queue
        self.access("pcompute_cap").assign_marking(empty_tokens(512)) 
        self.access("pload_cap").assign_marking(empty_tokens(512)) 
        self.access("pstore_cap").assign_marking(empty_tokens(512))
        self.access("pcontrol").assign_marking(empty_tokens(1))
        