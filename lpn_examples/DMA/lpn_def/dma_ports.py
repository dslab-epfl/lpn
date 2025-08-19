from lpnlang import Place, Transition, Token
from DMA.lpn_def.funcs import *
from DMA.lpn_def.helper import arbiterWTimeOrdHelperNoCap


class LPNClassBase:
    def __init__(self, id):
        self.id = id
        self.t_list = []
        self.node_dict = {}
        self.comp_list = []

    def access(self, id):
        return self.node_dict[id]

    def transitions(self):
        return self.t_list
    
    def init_places(self):
        pass

    def components(self):
        return self.comp_list

class DMAPortBase(LPNClassBase):
    def __init__(self, id, rw, num_ports, parallel=1, send_delay=0, recv_delay=0):
        super().__init__(id)
        self.num_ports = num_ports
        self.rw = rw
        # for recv req 
        self.req_put_ps = []
        self.parallel = parallel

        # for get response
        self.req_get_ps = []
        for i in range(num_ports):
            self.req_put_ps.append(Place(f"{self.id}_req_put_{i}"))
            self.req_get_ps.append(Place(f"{self.id}_req_get_{i}"))
            
        if num_ports >= 1:
            
            self.mem_put_p = Place(f"{self.id}_mem_put_buf")
            self.fifo_order_p = Place(f"{self.id}_fifo_order")
            self.t_list.append(
                arbiterWTimeOrdHelperNoCap(self.id, self.req_put_ps, self.mem_put_p, self.fifo_order_p)
            )
        else:
            self.mem_put_p = self.req_put_ps[0]
            self.fifo_order_p = None

        self.send_cap_place = Place(f"{self.id}_send_cap")
        dummy_sink = Place(f"{self.id}_SINK")
        self.send = Transition(f"{self.id}_mem_put")
        self.send.delay_f = con_delay_ns(send_delay)
        self.send.p_input.extend([self.mem_put_p, self.send_cap_place])
        self.send.pi_w.extend([take_1_token(), take_1_token()])
        self.send.p_output.append(dummy_sink)
        self.send.pip = con_delay_ns(0)
       

        # this one should call a function to put mem
        self.send.po_w.append(call_put_mem(self.mem_put_p, self.rw))

        recv_buf = Place(f"{self.id}_recv_buf")        
        self.recv_from_mem = Transition(f"{self.id}_recv_from_mem")
        self.recv_from_mem.delay_f = delay_0_if_resp_ready(self.rw)
        # self.recv_from_mem.p_input.append(dummy_sink)
        # self.recv_from_mem.pi_w.append(take_some_token(0))
        self.recv_from_mem.p_output.append(recv_buf)
        self.recv_from_mem.po_w.append(call_get_mem(self.rw))

        self.recv = Transition(f"{self.id}_mem_get")
        self.recv.delay_f = con_delay_ns(recv_delay)

        self.recv.p_input.append(recv_buf)
        self.recv.pi_w.append(take_1_token())
        self.recv.p_output.append(self.send_cap_place)
        self.recv.po_w.append(pass_empty_token())
        self.recv.pip = con_delay_ns(0)

        for i in range(num_ports):
            self.recv.p_output.append(self.req_get_ps[i])
            self.recv.po_w.append(pass_token_match_port(recv_buf, i))

        self.t_list.append(self.recv)
        self.t_list.append(self.recv_from_mem)
        self.t_list.append(self.send)
    def init_places(self):
        self.send_cap_place.assign_marking(deque([Token() for _ in range(self.parallel)]))
    
    def port(self, idx):
        return [self.req_put_ps[idx], self.req_get_ps[idx], self.fifo_order_p, idx]
    
    def put(self, port, id, addr, size, buffer, rw):
        self.req_put_ps[port].push_token(Token({"ref": port, "id": id, "addr": addr, "size": size, "buffer":buffer, "rw": rw}))
        self.fifo_order_p.push_token(Token({"idx": port}))

    def get(self, port):
        return self.req_get_ps[port].tokens