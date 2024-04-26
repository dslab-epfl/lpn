from lpnlang import Place, Transition, Token
from lpn_def.funcs import *
from lpn_def.all_enum import *
from lpn_def.helper import arbiterHelper, arbiterWTimeOrdHelper, arbiterHelperNoCap, arbiterHelperNoCapWPort, pass_type_idx
# from parameters import *
from param_x8 import *

class PcieBase:
    def __int__(self):
        pass

    def access(self, id):
        pass

    def transitions(self):
        pass

class PcieUniDirLink(PcieBase):
    def __init__(self, id):
        self.id = id
        self.tlp = Place(f"{self.id}_tlp")
        self.linkbuf = Place(f"{self.id}_linkbuf")
        self.transfer = Transition(id=f"{self.id}_transfer", pip=con_delay(LinkDelay))
        self.outbuf = Place(f"{self.id}_outbuf")
        self.merge_into_tlp = Transition(id=f"{self.id}_merge")
        
        self.transfer.delay_f = con_delay(DelayCycle)
        self.transfer.p_input.append(self.linkbuf)
        self.transfer.pi_w.append(take_1_token())
        self.transfer.p_output.append(self.outbuf)
        self.transfer.po_w.append(pass_empty_token(1))

        self.merge_into_tlp.delay_f = merge_delay(self.tlp)
        self.merge_into_tlp.p_input.append(self.tlp)
        self.merge_into_tlp.pi_w.append(take_1_token())
        self.merge_into_tlp.p_input.append(self.outbuf)
        self.merge_into_tlp.pi_w.append(take_credit_token(self.tlp, UNIT))
        
    def connect(self, recv):
        self.merge_into_tlp.p_output.append(recv)
        self.merge_into_tlp.po_w.append(pass_rm_header_token(self.tlp, 1, HBYTE))

    def transitions(self):
        return [self.transfer, self.merge_into_tlp]

class PcieSwitch(PcieBase):
    def __init__(self, id, in_port_list, is_rootcomplex = None):
        self.id = id
        self.is_rc = False if is_rootcomplex is None else is_rootcomplex
        out_port_list = in_port_list
        self.out_port_list = out_port_list
        self.in_port_list = in_port_list
        self.routinfo = {}
        # send
        self.out_port_trans = []

        self.place_list = []
        self.tmp_buffer_for_in_out_pair = {}
        self.tmp_trans_for_in_out_pair = {}

        # buf for recv
        self.in_port_buf = []
        
        self.in_port_buf_cap = []

        for ipt in in_port_list:
            for opt in out_port_list:
                if ipt == opt:
                    continue
                self.tmp_buffer_for_in_out_pair[(ipt,opt)] = Place(f"{self.id}_tmpbuf_{ipt}_{opt}")
 
        #external setup
        for ipt in in_port_list:
            pr = Place(f"{self.id}_recv_{ipt}")
            prcap = Place(f"{self.id}_recvcap_{ipt}")
            
            self.in_port_buf.append(pr) 
            self.in_port_buf_cap.append(prcap) 

            for opt in out_port_list:
                if ipt == opt:
                    continue
                ts = Transition(f"t{self.id}_tmpbuf_{ipt}_{opt}")
                ts.delay_f = con_delay(AdditionalCost)
                self.tmp_trans_for_in_out_pair[(ipt,opt)] = ts
                ts.p_input.append(pr)
                ts.pi_w.append(con_edge(1))
                ts.pi_guard.append(take_out_port(pr, self.routinfo, opt))
                ts.p_output.append(self.tmp_buffer_for_in_out_pair[(ipt,opt)])
                if self.is_rc:
                    ts.po_w.append(pass_atomic_smaller_token(RCTLP_SIZE, pr))
                else:
                    ts.po_w.append(pass_token(pr, 1))
            
        for idx, opt in enumerate(out_port_list):
            p_send = Place(f"{self.id}_sendbuf_{opt}")
            self.place_list.append(p_send)
            p_ids = []
            port_list = []
            for ipt in in_port_list:
                if ipt == opt:
                    continue
                port_list.append(ipt)
                p_ids.append(self.tmp_buffer_for_in_out_pair[(ipt,opt)])
            arbiter = arbiterHelperNoCapWPort(f"{self.id}_tmpbuf_to_sendbuf_{opt}", p_ids, port_list, p_send)
            self.out_port_trans.append(arbiter)            

            t_send = Transition(id=f"{self.id}_send_{opt}")
            self.out_port_trans.append(t_send)
            t_send.delay_f = var_tlp_process_delay(p_send, ProcessTLPCost)
            # if self.is_rc:
            #     t_send.delay_f = con_delay(RootDelayCycle)
            # else:
            #     t_send.delay_f = con_delay(0)
            t_send.p_input.append(p_send)
            t_send.pi_w.append(take_1_token())
             
            for jdx, ipt in enumerate(in_port_list):
                if ipt == opt:
                    continue
                pcap = self.in_port_buf_cap[jdx]
                # increase the capacity
                t_send.p_output.append(pcap)
                t_send.po_w.append(increase_credit(p_send, ipt, UNIT))
        
        #initialize
        for jdx, ipt in enumerate(in_port_list):
            pcap = self.in_port_buf_cap[jdx]
            pcap.assign_marking(create_empty_tokens(Credit))
        
        self.node_dict = {}
        all_trans = []
        for _, trans in self.tmp_trans_for_in_out_pair.items():
            all_trans.append(trans)
        all_trans.extend(self.out_port_trans)

        for trans in all_trans:
            self.node_dict[trans.id] = trans

        all_places = []
        for _, p in self.tmp_buffer_for_in_out_pair.items():
            all_places.append(p)

        all_places.extend(self.in_port_buf)
        all_places.extend(self.in_port_buf_cap)
        all_places.extend(self.place_list)

        for p in all_places:
            self.node_dict[p.id] = p 

    def transitions(self):
        all_trans = []
        for _, trans in self.tmp_trans_for_in_out_pair.items():
            all_trans.append(trans)
        all_trans.extend(self.out_port_trans)
        return all_trans

    def access_node(self, id):
        return self.node_dict[id]
    
    def connect(self, outport, recv_credit, link:PcieUniDirLink):
        for ipt in self.in_port_list:
            if ipt == outport:
                continue
            dispatch = self.node_dict[f"t{self.id}_tmpbuf_{ipt}_{outport}"]
            dispatch.p_input.append(recv_credit)
            dispatch.pi_guard.append(empty_guard())
            dispatch.pi_w.append(take_some_token(0))

            # # turn on the following
            # # HOL blocking 
            dispatch.pi_w_threshold.extend([empty_threshold()]*(len(dispatch.p_input)-1))
            dispatch.pi_w_threshold.append(take_credit_token(self.node_dict[f"{self.id}_recv_{ipt}"], UNIT))

        send_buf = self.node_dict[f"{self.id}_sendbuf_{outport}"]
        outport_t = self.node_dict[f"{self.id}_send_{outport}"]

        outport_t.p_input.append(recv_credit)
        outport_t.pi_w.append(take_credit_token(send_buf, UNIT))

        # if self.is_rc:
        # else:
        #     outport_t.pi_w.append(take_credit_token(send_buf, UNIT))

        outport_t.p_output.append(link.linkbuf)
        outport_t.po_w.append(pass_credit_with_header_token(send_buf, HBYTE, UNIT))
        
        outport_t.p_output.append(link.tlp)
        outport_t.po_w.append(pass_add_header_token(send_buf, 1, HBYTE))
        
    def install_rout(self, device_id, port):
        self.routinfo[device_id] = port

class PcieDevice(PcieBase):

    def __init__(self, id, fair=True):
        self.id = id
        seq_num = int(id[-1])

        """
            recv data
        """
        self.in_buf = Place(f"{self.id}_recv")
        self.in_buf_cap = Place(f"{self.id}_recvcap")
        self.in_buf_cap.assign_marking(create_empty_tokens(Credit))
        
        """
            process recved data 
        """
        self.process = Transition(id=f"{self.id}_proc")
        self.recv_comp = Place(f"{self.id}_recvcomp")
        self.recv_req = Place(f"{self.id}_recvreq")

        self.process.delay_f = con_delay(0)
        self.process.p_input.append(self.in_buf)
        self.process.pi_w.append(take_1_token())
        self.process.p_output.append(self.recv_comp)
        self.process.po_w.append(store_readcomp_1byte(self.in_buf))
        self.process.p_output.append(self.recv_req)
        self.process.po_w.append(store_request(seq_num, self.in_buf, MPS))
        self.process.p_output.append(self.in_buf_cap)
        self.process.po_w.append(increase_credit_wc(self.in_buf, UNIT))

        """
            separate buffers for posted request, nonposted request, and completion
        """
        self.req_buf = Place(f"{self.id}_reqbuf")
        self.req_buf_post = Place(f"{self.id}_reqbuf_post")
        self.req_buf_post_cap = Place(f"{self.id}_reqbuf_post_cap")
        NUM_BUF_CAP = 1
        self.req_buf_post_cap.assign_marking(create_empty_tokens(NUM_BUF_CAP))
        self.req_buf_nonpost = Place(f"{self.id}_reqbuf_nonpost")
        self.req_buf_nonpost_cap = Place(f"{self.id}_reqbuf_nonpost_cap")
        self.req_buf_nonpost_cap.assign_marking(create_empty_tokens(NUM_BUF_CAP))
        self.req_buf_cmpl = Place(f"{self.id}_reqbuf_cmpl")
        self.req_buf_cmpl_cap = Place(f"{self.id}_reqbuf_cmpl_cap")
        self.req_buf_cmpl_cap.assign_marking(create_empty_tokens(NUM_BUF_CAP))
        self.req_buf_map = {CstStr.NONPOST:0, CstStr.POST:1, CstStr.CMPL:2}
        self.order_keeper = Place(f"{self.id}_order_keeper")

        in_buf = [self.req_buf_nonpost, self.req_buf_post, self.req_buf_cmpl]
        in_buf_cap = [self.req_buf_nonpost_cap, self.req_buf_post_cap, self.req_buf_cmpl_cap]
        out_buf = self.req_buf
        self.out_buf_cap = Place(f"{self.id}_reqbuf_cap")
        self.out_buf_cap.assign_marking(create_empty_tokens(8))

        if fair:
            self.arbit_p_np = arbiterHelper(self.id, in_buf, in_buf_cap, out_buf, self.out_buf_cap)
        else:
            self.arbit_p_np = arbiterWTimeOrdHelper(self.id, in_buf, in_buf_cap, out_buf, self.out_buf_cap, self.order_keeper)
        
        """
            send out request
        """
        self.out_trans = Transition(id=f"{self.id}_send")
        self.out_trans.delay_f = var_tlp_process_delay(self.req_buf, ProcessTLPCost) 
        self.out_trans.p_input.append(self.req_buf)
        self.out_trans.pi_w.append(take_1_token())
        self.out_trans.p_output.append(self.out_buf_cap)
        self.out_trans.po_w.append(pass_empty_token(1))

        """
            readcmpl should not exists here
        """
        self.send_readcmpl = Transition(id=f"{self.id}_send_readcmpl", pip=con_delay(1))
        self.send_readcmpl.delay_f = mem_delay(self.recv_req, ReadDelay)
        self.send_readcmpl.p_input.append(self.recv_req)
        self.send_readcmpl.pi_w.append(take_1_token())
        self.send_readcmpl.p_input.append(self.req_buf_cmpl_cap)
        self.send_readcmpl.pi_w.append(take_1_token())
        self.send_readcmpl.p_output.append(self.req_buf_cmpl)
        self.send_readcmpl.po_w.append(pass_token(self.recv_req, 1))
        
        if not fair:
            self.send_readcmpl.p_output.append(self.order_keeper)
            self.send_readcmpl.po_w.append(pass_type_idx(self.req_buf_map, CstStr.CMPL))

        """
            put all places and transitions here
        """
        p_list = [self.in_buf, self.in_buf_cap, self.recv_comp, self.recv_req, 
        self.req_buf, self.req_buf_post,self.req_buf_nonpost,self.req_buf_cmpl,
        self.req_buf_post_cap, self.req_buf_nonpost_cap, self.req_buf_cmpl_cap,
        self.out_buf_cap]
        t_list = [self.out_trans, self.process, self.send_readcmpl, self.arbit_p_np]
        self.t_list = t_list
        self.node_dict = {}
        for p in p_list:
            self.node_dict[p.id] = p
        for t in t_list:
            self.node_dict[t.id] = t
            
    def access_node(self, id):
        return self.node_dict[id]

    def transitions(self):
        return self.t_list

    def connect(self, recv_credit, link:PcieUniDirLink):
        self.out_trans.p_input.append(recv_credit)
        self.out_trans.pi_w.append(take_credit_token(self.req_buf, UNIT))
        self.out_trans.p_output.append(link.tlp)
        self.out_trans.po_w.append(pass_add_header_token(self.req_buf, 1, HBYTE))
        self.out_trans.p_output.append(link.linkbuf)
        self.out_trans.po_w.append(pass_credit_with_header_token(self.req_buf, HBYTE, UNIT))
    