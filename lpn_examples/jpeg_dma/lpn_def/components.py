from lpnlang import lpn_all_nodes
from DMA.lpn_def.dma_ports import *
from jpeg_dma.lpn_def.func import *
from jpeg_dma.lpn_def.mem_func import *
from jpeg_dma.lpn_def.all_enum import CstStr

class JPEG(LPNClassBase):
    def __init__(self, id, dma_read:DMAPortBase, dma_write:DMAPortBase):
        super().__init__(id)
        # three dma read ports
        read_put_port_0, read_get_port_0, self.p_memread_fifo_order, _ = dma_read.port(0)
       
        self.p_memread_put_list = [read_put_port_0]
        self.p_memread_get_list = [read_get_port_0]

        # one dma write port
        write_put_port_0, write_get_port_0, self.p_memwrite_fifo_order, _ = dma_write.port(0)
        self.p_memwrite_put_list = [write_put_port_0]
        self.p_memwrite_get_list = [write_get_port_0]

        ptasks_bef_header = Place("ptasks_bef_header")
        ptasks_aft_header = Place("ptasks_aft_header")
        pstart = Place("pstart")
        p4 = Place("p4")
        p0 = Place("p0")
        p1 = Place("p1")
        p2 = Place("p2")
        p3 = Place("p3")
        p5 = Place("p5")
        p6 = Place("p6")
        pstall = Place("pstall")
        p7 = Place("p7")
        p8 = Place("p8")
        p10 = Place("p10")
        p20 = Place("p20")
        p21 = Place("p21")
        p22 = Place("p22")
        pdone = Place("pdone")
        pvarlatency = Place("pvarlatency")

        p_req_mem = Place("p_req_mem")
        p_recv_buf = Place("p_recv_buf")

        t0 = Transition(
            id="t0", 
            delay_func=mcu_delay(pvarlatency), 
            pi=[p7, p4, pvarlatency, p_recv_buf], 
            po=[p0, p8], 
            pi_w=[c1, c1, c1, con_edge(100000)], 
            po_w=[ct1, ct1]
        )

        twait_header = Transition(
            id="twait_header", 
            delay_func=constant_func(0), 
            pi=[ptasks_bef_header, p_recv_buf], 
            pi_w=[take_all(ptasks_bef_header), con_edge(18*32)], 
            po=[ptasks_aft_header], 
            po_w=[pass_all_tokens(ptasks_bef_header)]
        )

        t2 = Transition(id="t2", delay_func=constant_func(66), pi=[p0, p20, p6], po=[p1, p21, p4], pi_w=[c1,  c1,  c0], pi_w_threshold=[const_threshold(0), const_threshold(0),  const_threshold(2)], po_w=[ct1,  ct1, ct1])
        t3 = Transition(id="t3", delay_func=constant_func(66), pi=[p0, p21, p6], po=[p2, p22, p4], pi_w=[c1,  c4,  c0], pi_w_threshold=[const_threshold(0), const_threshold(0),  const_threshold(2)], po_w=[ct4,  ct1, ct1])
        t4 = Transition(id="t4", delay_func=constant_func(66), pi=[p0, p22, p6], po=[p3, p20, p4], pi_w=[c1,  c1,  c4], pi_w_threshold=[const_threshold(0), const_threshold(0),  const_threshold(2)], po_w=[ct4,  ct4, ct1])
        t5 = Transition(id="t5", delay_func=constant_func(65), pi=[p1, p2, p3], po=[pdone, p6], pi_w=[c1, c1, c1], po_w=[ct1, ct1, ct1])
        t1 = Transition(id="t1", delay_func=constant_func(0), pi=[ptasks_aft_header, p8], po=[p7, pstart], pi_w=[c1, c1], po_w=[ct1, ct1])

        p_send_dma = Place("p_send_dma")

        tinput_fifo = Transition(
            id="tinp_fifo", 
            delay_func=constant_func(8), 
            pi=[p_req_mem], 
            pi_w=[take_max_16_tokens(p_req_mem)],
            po=[p_send_dma, self.p_memread_fifo_order, self.p_memread_put_list[0]],
            po_w=[record_max_16(p_req_mem), push_request_order(0, p_req_mem), mem_request(0, CstStr.DMA_READ, p_req_mem)]
        )

        t_input_fifo_recv = Transition(
            id="t_input_fifo_recv",
            delay_func=constant_func(0),
            pi=[p_send_dma, self.p_memread_get_list[0]],
            pi_w=[take_1_token(), take_resp_token(p_send_dma)],
            po=[p_recv_buf],
            po_w=[put_recv_buf(p_send_dma)]
        )
        
        toutput_fifo = Transition(
            id="toutput_fifo", 
            delay_func=constant_func(64), 
            pi=[pdone], 
            pi_w=[c1],
            po = [self.p_memwrite_fifo_order, self.p_memwrite_put_list[0]],
            po_w = [push_request_order_write(0, 32), mem_request_write(0, CstStr.DMA_WRITE, 32) ]
        )

        toutput_fifo_recv = Transition(
            id="toutput_fifo_recv",
            delay_func=constant_func(0),
            pi=[self.p_memwrite_get_list[0]],
            pi_w=[take_resp_token_write(32)],
        )

        self.t_list = [
            twait_header, t2, t3, t4, t5, t0, t1, twait_header, tinput_fifo, toutput_fifo,
            t_input_fifo_recv, toutput_fifo_recv]
        self.p_list, _, self.node_dict = lpn_all_nodes(self.t_list)

    def init_places(self):
        def empty_tokens(x):
            new_queue = deque()
            [new_queue.append(Token()) for i in range(x)]
            return new_queue
        self.access("p4").assign_marking(empty_tokens(4))
        self.access("p6").assign_marking(empty_tokens(4))
        # self.access("p5").assign_marking(empty_tokens(7))
        # self.access("pstall").assign_marking(empty_tokens(4))
        self.access("p8").assign_marking(empty_tokens(1))
        self.access("p20").assign_marking(empty_tokens(4))
        self.access("pvarlatency").type_annotations = ["nonzero"]   
        self.access("p_req_mem").type_annotations = ["device","req","cmpl","from"] 


       