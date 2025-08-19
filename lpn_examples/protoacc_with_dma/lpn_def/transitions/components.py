from DMA.lpn_def.dma_ports import *
from protoacc_with_dma.lpn_def.funcs.funcs import *

class FrontEnd(LPNClassBase):
    def __init__(self, id, num_handlers):
        super().__init__(id)

        self.num_handlers = num_handlers

        self.pfields = Place(f"{self.id}_pfields")

        self.pcontrol = Place(f"{self.id}_pcontrol")
        self.pcontrol_prime = Place(f"{self.id}_pcontrol_prime")
        self.pfields_meta = Place(f"{self.id}_pfields_meta")
        self.pmessage_tasks = Place(f"{self.id}_pmessage_tasks")
        self.ps_hasBitsLoader_HasBitsLoad = Place(f"{self.id}_ps_hasBitsLoader_HasBitsLoad")
        self.pisnot_submessage_value_resp = Place(f"{self.id}_pisnot_submessage_value_resp")
        self.pAdvance_OK = Place(f"{self.id}_pAdvance_OK")
        self.pdescr_request_Q = Place(f"{self.id}_pdescr_request_Q")
        self.psWaitForRequest = Place(f"{self.id}_psWaitForRequest")
        self.ptofieldhandler_dispatcher = Place(f"{self.id}_ptofieldhandler_dispatcher")
        self.pcollect = Place(f"{self.id}_pcollect")
        self.pholder_split_msg = Place(f"{self.id}_pholder_split_msg")
        self.p10_descr = Place(f"{self.id}_p10_descr")
        self.p9_descr = Place(f"{self.id}_p9_descr")

        self.pwrites_input_IF_Q = Place(f"{self.id}_pwrites_input_IF_Q")
        self.pwrites_inject_Q = Place(f"{self.id}_pwrites_inject_Q")
        self.pwrite_index_holder = Place(f"{self.id}_pwrite_index_holder")
        self.pwrite_mem_resp = Place(f"{self.id}_pwrite_mem_resp")
        self.pwrites_inject_Q_non_top = Place(f"{self.id}_pwrites_inject_Q_non_top")
        self.pwrites_inject_Q_top = Place(f"{self.id}_pwrites_inject_Q_top")
        self.phold = Place(f"{self.id}_phold")
        self.pdispatch_index_holder = Place("pdispatch_index_holder")
        self.pdispatch_hold = Place("pdispatch_hold")
        self.pwrite_hold = Place("pwrite_hold")

        self.mem_put_0 = None
        self.mem_put_1 = None
        self.mem_get_0 = None
        self.mem_get_1 = None
        self.mem_port_0 = None
        self.mem_port_1 = None

        # t2 = Transition(
        #         id = "t2",
        #         delay_func = con_delay(1), 
        #         pi=[ps_hasBitsLoader_IsSubmessageLoad, pmessage_tasks], 
        #         pi_w=[take_1_token(), take_1_token()], 
        #         po=[ps_hasBitsLoader_HasBitsLoad, pl2helperUser1Req, pcontrol, pcollect],
        #         po_w=[pass_empty_token(), pass_empty_token(), pass_token(pmessage_tasks, 1), pass_token(pmessage_tasks, 1)],
        #     )
        
        # tadvance_ok = Transition(
        #     id = "tadvance_ok", 
        #     delay_func = con_delay(1),
        #     pi = [pAdvance_OK],
        #     pi_w = [take_1_token()],
        #     po = [ps_hasBitsLoader_IsSubmessageLoad],
        #     po_w = [pass_empty_token()]
        # )

        'pass at most 32 fields to pdescr_request_Q and pass on to handle non-submessage'
        t1 = Transition(
            id = "t1", 
            delay_func = con_delay(0),
            pi = [self.pcontrol],
            pi_w = [take_1_token()],
            po = [self.pdescr_request_Q, self.pisnot_submessage_value_resp],
            po_w = [pass_token(self.pcontrol, 1), pass_not_submessage(self.pcontrol)],
        )

        'if non-submessage, can continue to fetch next 32 fields'
       

        t2 = Transition(
            id = "t2",
            delay_func = con_delay(1),
            pi = [self.pAdvance_OK, self.pmessage_tasks],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.pcontrol],
            po_w = [pass_token(self.pmessage_tasks, 1)]
        )

        # t10 = Transition("10", con_delay(2+mem_read_delay()()),

        'this is for handle in case the field is submessage'
        'it skipped many steps sWaitForSubmADT sIssueCPPObjAddrReq sIssueADTHeaderReq sAcceptCPPObjAddr sAcceptADTHeaderReq s_hasBitsLoader_IsSubmessageLoad'
        'l2helperUser2'
        # t9 = Transition(
        #     id = "t9", 
        #     delay_func = con_delay(MemDelay+2),
        #     pi = [p9_descr, psWaitForRequest],
        #     pi_w = [take_1_token(), take_1_token()],
        #     po = [psWaitForRequest, pAdvance_OK, pholder_split_msg],
        #     po_w = [pass_empty_token(), pass_empty_token(), pass_empty_token()]
        # )

        t19 = Transition(
            id = "t19", 
            delay_func = con_delay(1),
            pi = [self.pwrites_input_IF_Q],
            pi_w = [take_1_token()],
            po = [self.pwrites_inject_Q],
            po_w = [pass_token(self.pwrites_input_IF_Q, 1)],
        )
        
        tdist = Transition(
            id = "tinject_write_dist", 
            delay_func = con_delay(0),
            pi = [self.pwrites_inject_Q, self.phold],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.pwrites_inject_Q_non_top, self.pwrites_inject_Q_top],
            po_w = [pass_non_top_token(self.pwrites_inject_Q), pass_top_token(self.pwrites_inject_Q)],
        )


        t24 = Transition(
            id = "t24", 
            delay_func = con_delay(4),
            pi = [self.pwrites_inject_Q_top],
            pi_w = [take_1_token()],
            po = [self.pwrite_mem_resp, self.phold],
            po_w = [pass_empty_token(), pass_empty_token()],
        )

        # tdispatch_dist = Transition(
        #     id = "tdispatch_dist", 
        #     delay_func = con_delay(0),
        #     pi = [pdispatch_index_holder, pdispatch_hold],
        #     pi_w = [take_1_token(), take_1_token()],
        #     po = [pdispatch_index_holder, pdispatch_index_holder_f1],
        #     po_w = [pass_field_index_add_one(pdispatch_index_holder), pass_field_index_token(pdispatch_index_holder, 1)],
        # )

        # twrite_dist = Transition(
        #     id = "twrite_dist", 
        #     delay_func = con_delay(0),
        #     pi = [pwrite_index_holder, pwrite_hold],
        #     pi_w = [take_1_token(), take_1_token()],
        #     po = [pwrite_index_holder, pwrite_index_holder_f1],
        #     po_w = [pass_field_index_add_one(pwrite_index_holder), pass_field_index_token(pwrite_index_holder, 1)],
        # )

        tdispatch_dist = Transition(
            id = "tdispatch_dist", 
            delay_func = con_delay(0),
            pi = [self.pdispatch_index_holder, self.pdispatch_hold],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.pdispatch_index_holder],
            po_w = [pass_field_index_add_one(self.pdispatch_index_holder, self.num_handlers)],
        )

        twrite_dist = Transition(
            id = "twrite_dist", 
            delay_func = con_delay(0),
            pi = [self.pwrite_index_holder, self.pwrite_hold],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.pwrite_index_holder],
            po_w = [pass_field_index_add_one(self.pwrite_index_holder, self.num_handlers)],
        )
        self.twrite_dist = twrite_dist
        self.dispatch_dist = tdispatch_dist

        self.t_list.extend(
            [
               t1, t2, t19, tdist, t24, tdispatch_dist, twrite_dist
            ]
        )

        self.tdispatch_dist = tdispatch_dist
        self.pwrite_mem_put = None
        self.pwrite_mem_get = None
        self.pwrite_mem_fifo_order = None
        self.write_port_num = None

    def __init_additional_ts(self):
        
        self.p_memread_put_list = [self.mem_put_0, self.mem_put_1]
        self.p_memread_get_list = [self.mem_get_0, self.mem_get_1]
        self.port_num_list = [self.mem_port_0, self.mem_port_1]


        #  t3 = Transition(
        #     id = "t3", 
        #     delay_func = con_delay(1),
        #     pi = [self.pisnot_submessage_value_resp],
        #     pi_w = [take_1_token()],
        #     po = [self.pAdvance_OK],
        #     po_w = [pass_empty_token()]
        # )


        p_t_3_pre = Place(f"{self.id}_p_t_3_pre")

        t3_pre = Transition(
                id = "t3_pre",
                delay_func = con_delay(1), 
                pi=[self.pisnot_submessage_value_resp], 
                pi_w=[take_1_token()],
                po=[p_t_3_pre, self.p_memread_fifo_order, self.p_memread_put_list[0]],
                po_w=[pass_token(self.pisnot_submessage_value_resp, 1), push_request_order(self.port_num_list[0], 2), mem_request(self.port_num_list[0], CstStr.LOAD_HASBITS_AND_IS_SUBMESSAGE, 2)],
                            )
        
        self.p_t_3_pre = p_t_3_pre
        
        t3_post = Transition(
                id = "t3_post",
                delay_func = con_delay(0),
                pi=[p_t_3_pre, self.p_memread_get_list[0]],
                pi_w=[take_1_token(), take_some_token(2)],
                po=[self.pAdvance_OK, self.ps_hasBitsLoader_HasBitsLoad],
                po_w=[pass_empty_token(), pass_empty_token()],
        )
        
        self.p_t_9_pre = Place(f"{self.id}_p_t_9_post")
        t9_pre = Transition(
            id = "t9_pre",
            delay_func = con_delay(0),
            pi = [self.p9_descr, self.psWaitForRequest],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.p_t_9_pre, self.p_memread_put_list[0], self.p_memread_fifo_order],
            po_w = [pass_empty_token(), mem_request(self.port_num_list[0], CstStr.LOAD_NEW_SUBMESSAGE, 2), push_request_order(self.port_num_list[0], 2)]
        )

        self.t9_pre = t9_pre

        t9_post = Transition(
            id = "t9_post",
            delay_func = con_delay(0),
            pi = [self.p_t_9_pre, self.p_memread_get_list[0]],
            pi_w = [take_1_token(), take_some_token(2)],
            po = [self.psWaitForRequest, self.pAdvance_OK, self.pholder_split_msg],
            po_w = [pass_empty_token(), pass_empty_token(), pass_empty_token()]
        )  

        self.t9_post = t9_post

        p10_descr_pre = Place(f"{self.id}_p10_descr_pre")
        p10_descr_post = Place(f"{self.id}_p10_descr_post")
        p10_descr_post2 = Place(f"{self.id}_p10_descr_post2")
        p10_descr_post3 = Place(f"{self.id}_p10_descr_post3")
        tload_field_addr = Transition(
            id = "tload_field_addr",
            delay_func = con_delay(0),
            pi = [p10_descr_pre, self.ps_hasBitsLoader_HasBitsLoad, self.pfields_meta],
            pi_w = [take_1_token(), take_1_token(), take_num_field_as_control(p10_descr_pre)],
            po = [p10_descr_post3, p10_descr_post, self.p_memread_put_list[1], self.p_memread_fifo_order],
            po_w = [anonymous_func_1_pass_token(p10_descr_pre), pass_fields_meta_token(p10_descr_pre, self.pfields_meta), mem_request_v3(self.port_num_list[1], CstStr.LOAD_EACH_FIELD, p10_descr_pre), push_request_order_v3(self.port_num_list[1], p10_descr_pre)]
        )

        self.tload_field_addr = tload_field_addr

        tload_field_addr_post = Transition(
            id = "tload_field_addr_post",
            delay_func = con_delay(2),
            pi = [p10_descr_post, self.p_memread_get_list[1]],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.ptofieldhandler_dispatcher, p10_descr_post2],
            po_w = [pass_token(p10_descr_post, 1), pass_empty_token()]
        )


        t10 = Transition(
            id = "t10",
            delay_func = con_delay(0),
            pi = [p10_descr_post3,  p10_descr_post2],
            pi_w = [take_1_token(), take_all_tokens(p10_descr_post3)],
            po = [self.pholder_split_msg],
            po_w = [pass_empty_token()],
        )

        'branch onto submessage or non-submessage handle' 
        tsplit_msg = Transition(
            id = "split_msg",
            delay_func = con_delay(0),
            pi = [self.pdescr_request_Q, self.pholder_split_msg],
            pi_w = [take_1_token(), take_1_token()],
            po = [p10_descr_pre, self.p9_descr],
            po_w = [pass_non_message_token(self.pdescr_request_Q), pass_message_token(self.pdescr_request_Q)],
        )

        # t23 = Transition(
        #     id = "t23_pre", 
        #     delay_func = write_out_delay(self.pwrites_inject_Q_non_top),
        #     pi = [self.pwrites_inject_Q_non_top],
        #     pi_w = [take_1_token()],
        #     # pi_guard = [take_non_top_level(pwrites_inject_Q)],
        #     po = [self.pwrite_mem_resp, self.phold],
        #     po_w = [pass_empty_token(), pass_empty_token()],
        # )

        self.t_list.extend(
            [
                t3_pre, t3_post, t10, t9_pre, t9_post, tsplit_msg, tload_field_addr, tload_field_addr_post
            ]
        )

    def __init_additional_ts_write(self):
        p_t_23 = Place(f"{self.id}_p_t_23")
        t23_pre = Transition(
            id = "t23_pre", 
            delay_func = con_delay(0),
            pi = [self.pwrites_inject_Q_non_top],
            pi_w = [take_1_token()],
            # pi_guard = [take_non_top_level(pwrites_inject_Q)],
            po = [p_t_23, self.pwrite_mem_put, self.pwrite_mem_fifo_order],
            po_w = [pass_empty_token(), mem_request_write_v4(self.write_port_num, CstStr.WRITE_OUT, self.pwrites_inject_Q_non_top), push_write_request_order_v4(self.write_port_num, self.pwrites_inject_Q_non_top)],
        )

        t23_post = Transition(
            id = "t23_post",
            delay_func = con_delay(0),
            pi = [p_t_23],
            pi_w = [take_1_token()],
            po = [self.phold],
            po_w = [pass_empty_token()],
        )

        self.t_list.extend(
            [t23_pre, t23_post]
        )

    def init_places(self):
        self.pAdvance_OK.assign_marking(deque([Token()]))
        self.psWaitForRequest.assign_marking(deque([Token()])) 
        self.pdispatch_index_holder.assign_marking(deque([Token({"field_index": 1})])) 
        self.pwrite_index_holder.assign_marking(deque([Token({"field_index": 1})])) 
        self.phold.assign_marking(deque([Token()]))   
        self.pdispatch_hold.assign_marking(deque([Token()]))   
        self.pwrite_hold.assign_marking(deque([Token()]))   
        self.pholder_split_msg.assign_marking(deque([Token()]))   
         
    def install_input_tokens(self, control_tokens, fields_meta_tokens, unit_tokens):
        print("install input tokens")
        self.pmessage_tasks.assign_marking(control_tokens)
        self.pfields_meta.assign_marking(fields_meta_tokens)
        self.pfields.assign_marking(unit_tokens)

    def connect_field_handler(self, field_handler, handler_no):
        field_handler.ptofieldhandler_dispatcher = self.ptofieldhandler_dispatcher
        field_handler.pfields = self.pfields
        field_handler.pdispatch_hold = self.pdispatch_hold
        field_handler.pwrite_hold = self.pwrite_hold
        field_handler.pwrites_input_IF_Q = self.pwrites_input_IF_Q
        field_handler.init_dependent_ts()
        self.tdispatch_dist.p_output.append(field_handler.pdispatch_index_holder_)
        self.tdispatch_dist.po_w.append(pass_field_index_token(self.pdispatch_index_holder, handler_no))
        self.twrite_dist.p_output.append(field_handler.pwrite_index_holder_)
        self.twrite_dist.po_w.append(pass_field_index_token(self.pwrite_index_holder, handler_no))


    def connect_memread_port(self, memread_port_put_p_list, memread_port_get_p_list, memread_fifo_order_p, port_num_list):
        self.mem_put_0, self.mem_put_1 = memread_port_put_p_list
        self.mem_get_0, self.mem_get_1 = memread_port_get_p_list
        self.mem_port_0, self.mem_port_1 = port_num_list
        self.p_memread_fifo_order = memread_fifo_order_p
        self.__init_additional_ts()
        # print(self.mem_put_0, self.mem_put_1, self.mem_get_0, self.mem_get_1, self.mem_port_0, self.mem_port_1)

    def connect_memwrite_port(self, memwrite_port_put_p, memwrite_port_get_p, memwrite_fifo_order_p, port_num):
        self.pwrite_mem_put = memwrite_port_put_p
        self.pwrite_mem_get = memwrite_port_get_p
        self.pwrite_mem_fifo_order = memwrite_fifo_order_p
        self.write_port_num = port_num
        self.__init_additional_ts_write()

      

class FieldHandler(LPNClassBase):
    def __init__(self, id, handler_id):
        super().__init__(id)
        self.handler_id = handler_id
        
        self.pops_in_ = Place(f"{self.id}_pops_in_")
        self.p_dist_hold = Place(f"{self.id}_p_dist_hold")
        self.pops_in__eom = Place(f"{self.id}_pops_in__eom")
        self.pops_in__scalar = Place(f"{self.id}_pops_in__scalar")
        self.pops_in__non_scalar = Place(f"{self.id}_pops_in__non_scalar")
        self.pops_in__repeated = Place(f"{self.id}_pops_in__repeated")

        self.pdispatch_index_holder_ = Place(f"{self.id}_pdispatch_index_holder_")


        self.p_S_WAIT_CMD = Place(f"{self.id}_p_S_WAIT_CMD")
        self.p_S_SCALAR_DISPATCH_REQ = Place(f"{self.id}_p_S_SCALAR_DISPATCH_REQ")
        # p_S_SCALAR_OUTPUT_DATA = Place(f"{self.id}_p_S_SCALAR_OUTPUT_DATA")
        self.p_S_STRING_GETPTR = Place(f"{self.id}_p_S_STRING_GETPTR")
        # p_S_STRING_GETHEADER1 = Place(f"{self.id}_p_S_STRING_GETHEADER1")
        # p_S_STRING_GETHEADER2 = Place(f"{self.id}_p_S_STRING_GETHEADER2")
        # p_S_STRING_RECVHEADER1 = Place(f"{self.id}_p_S_STRING_RECVHEADER1")
        # p_S_STRING_RECVHEADER2 = Place(f"{self.id}_p_S_STRING_RECVHEADER2")
        self.p_S_STRING_LOADDATA = Place(f"{self.id}_p_S_STRING_LOADDATA")
        # p_S_STRING_LOADDATA_resp = Place(f"{self.id}_p_S_STRING_LOADDATA_resp")
        self.p_S_STRING_WRITE_KEY = Place(f"{self.id}_p_S_STRING_WRITE_KEY")
        self.p_S_UNPACKED_REP_GETPTR = Place(f"{self.id}_p_S_UNPACKED_REP_GETPTR")
        # p_S_UNPACKED_REP_GETSIZE = Place(f"{self.id}_p_S_UNPACKED_REP_GETSIZE")
        # p_S_UNPACKED_REP_RECVPTR = Place(f"{self.id}_p_S_UNPACKED_REP_RECVPTR")
        # p_S_UNPACKED_REP_RECVSIZE = Place(f"{self.id}_p_S_UNPACKED_REP_RECVSIZE")
        self.p_S_WRITE_KEY = Place(f"{self.id}_p_S_WRITE_KEY")
        self.p_outputQ = Place(f"{self.id}_p_outputQ")
        self.p_finished = Place(f"{self.id}_p_finished")
        self.p_num_units = Place(f"{self.id}_p_num_units")
        self.p_units = Place(f"{self.id}_p_units")
        self.p_hold = Place(f"{self.id}_p_hold")

        self.pwrite_index_holder_ = Place(f"{self.id}_pwrite_index_holder_")

       
        
      
        self.pwrites_input_IF_Q = None
        self.ptofieldhandler_dispatcher = None
        self.pfields = None

        self.pdispatch_hold = None
        self.pwrite_hold = None


        # self.p_mem_read_resp = Place(f"{self.id}_mem_read_resp")

        # tissue_memread = Transition(
        #     id = f"{self.id}_issue_memread",
        #     delay_func = con_delay(0),
        #     pi = [self.p_memread_put],
        #     pi_w = [take_1_token()],
        #     po = [p_mem_read_resp],
        #     po_w = [pass_token(self.p_memread_put, 1)]
        # )


        t_resume = Transition(
            id = f"{self.id}_resume",
            delay_func = con_delay(0),
            pi = [self.p_num_units, self.p_finished],
            pi_w = [take_1_token(), take_resume_token(self.p_num_units)],
            po = [self.p_S_WAIT_CMD, self.p_outputQ],
            po_w = [pass_empty_token(), pass_field_end_token()],
            )
        

        t_dist = Transition(
            id = f"{self.id}_dist", 
            delay_func = con_delay(0),
            pi = [self.pops_in_, self.p_dist_hold],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.pops_in__eom, self.pops_in__scalar, self.pops_in__non_scalar, self.pops_in__repeated],
            po_w = [pass_eom(self.pops_in_), pass_scalar(self.pops_in_), pass_non_scalar(self.pops_in_), pass_repeated(self.pops_in_)],
        )

        t_eom = Transition(
            id = f"{self.id}_eom", 
            delay_func = con_delay(2),
            pi = [self.pops_in__eom, self.p_S_WAIT_CMD, self.p_units],
            pi_w = [take_1_token(), take_1_token(), take_1_token()],
            po = [self.p_outputQ, self.p_finished, self.p_dist_hold],
            po_w = [pass_key_outputQ_end_of_toplevel_token(self.pops_in__eom), pass_empty_token(), pass_empty_token()],
        )

        t_25 = Transition(
            id = f"{self.id}_25", 
            delay_func = con_delay(1),
            pi = [self.pops_in__scalar, self.p_S_WAIT_CMD],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.p_S_SCALAR_DISPATCH_REQ, self.p_dist_hold],
            po_w = [pass_empty_token(), pass_empty_token()],
        )

        t_26 = Transition(
            id = f"{self.id}_26", 
            delay_func = con_delay(1),
            pi = [self.pops_in__non_scalar, self.p_S_WAIT_CMD],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.p_S_STRING_GETPTR, self.p_dist_hold],
            po_w = [pass_empty_token(), pass_empty_token()],
        )

        t_28 = Transition(
            id = f"{self.id}_28", 
            delay_func = con_delay(1),
            pi = [self.pops_in__repeated, self.p_S_WAIT_CMD],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.p_S_UNPACKED_REP_GETPTR, self.p_dist_hold],
            po_w = [pass_token(self.pops_in__repeated, 1), pass_empty_token()],
        )


        t_31 = Transition(
            id = f"{self.id}_31", 
            delay_func = con_delay(1),
            pi = [self.p_S_WRITE_KEY],
            pi_w = [take_1_token()],
            po = [self.p_finished, self.p_hold, self.p_outputQ],
            po_w = [pass_empty_token(), pass_empty_token(), pass_key_outputQ_token()],
        )

        # t_36 = Transition(
        #     id = f"{self.id}_36", 
        #     delay_func = con_delay(4+2*10),
        #     pi = [p_S_STRING_GETPTR, p_hold,  p_units],
        #     pi_w = [take_1_token(), take_1_token(), take_1_token()],
        #     po = [p_S_STRING_LOADDATA],
        #     po_w = [pass_token(p_units, 1)],
        # )

        # t_37 = Transition(
        #     id = f"{self.id}_37", 
        #     delay_func = all_bytes_delay(p_S_STRING_LOADDATA),
        #     pi = [p_S_STRING_LOADDATA],
        #     pi_w = [take_1_token()],
        #     po = [p_outputQ, p_S_STRING_WRITE_KEY],
        #     po_w = [pass_all_bytes_outputQ_token(p_S_STRING_LOADDATA), pass_empty_token()],
        # )

        t_40 = Transition(
            id = f"{self.id}_40", 
            delay_func = con_delay(1),
            pi = [self.p_S_STRING_WRITE_KEY],
            pi_w = [take_1_token()],
            po = [self.p_finished, self.p_outputQ, self.p_hold],
            po_w = [pass_empty_token(), pass_key_outputQ_token(), pass_empty_token() ],
        )

        # t_44 = Transition(
        #     id = f"{self.id}_44", 
        #     delay_func = con_delay(3+10),
        #     pi = [p_S_UNPACKED_REP_GETPTR],
        #     pi_w = [take_1_token()],
        #     po = [p_S_SCALAR_DISPATCH_REQ, p_S_STRING_GETPTR],
        #     po_w = [pass_repeated_array_token(p_S_UNPACKED_REP_GETPTR, CstStr.SCALAR), pass_repeated_array_token(p_S_UNPACKED_REP_GETPTR, CstStr.NONSCALAR)],
        # )

      
        
        self.t_list.extend([
            t_resume, t_dist, t_eom, t_25, t_26, t_28, t_31, t_40
        ])

        self.p_memread_get = None
        self.p_memread_put = None
        self.p_memread_fifo_order = None
        self.port_num = None

    def init_dependent_ts(self):
        tdispatch = Transition(
            id = f"{self.id}_dispatch", 
            delay_func = con_delay(1),
            pi = [self.ptofieldhandler_dispatcher, self.pdispatch_index_holder_, self.pfields],
            pi_w = [take_1_token(), take_1_token(), take_num_field_tokens(self.ptofieldhandler_dispatcher)],
            po = [self.pdispatch_hold, self.pops_in_, self.p_units, self.p_num_units],
            po_w = [pass_empty_token(), pass_token(self.ptofieldhandler_dispatcher, 1), pass_field_token(self.ptofieldhandler_dispatcher, self.pfields), pass_num_field_token(self.ptofieldhandler_dispatcher)], # return to pfields after fetch
        )
        
        t_write_req_out = Transition(
            id = f"{self.id}_write_req_out", 
            delay_func = field_end_cond_delay(self.p_outputQ),
            pi = [self.p_outputQ, self.pwrite_index_holder_],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.pwrites_input_IF_Q, self.pwrite_hold, self.pwrite_index_holder_],
            po_w = [pass_non_field_end_token(self.p_outputQ, 1), pass_write_hold_cond(self.p_outputQ),  pass_write_index_holder_cond(self.p_outputQ, self.pwrite_index_holder_)],
        )

        self.t_list.extend([
            tdispatch, t_write_req_out
        ])

        
    def __init_additional_ts(self):
    
        p_t_36_pre = Place(f"{self.id}_p_t_36_pre")

        t_36_pre = Transition(
            id = f"{self.id}_36_pre", 
            delay_func = con_delay(4),
            pi = [self.p_S_STRING_GETPTR,self.p_hold],
            pi_w = [take_1_token(), take_1_token()],
            po = [p_t_36_pre, self.p_memread_put, self.p_memread_fifo_order],
            po_w = [pass_empty_token(), mem_request(self.port_num, CstStr.STRING_GETPTR_REQ, 3), push_request_order(self.port_num, 3)],
        )

        t_36_post = Transition(
            id = f"{self.id}_36_post", 
            delay_func = con_delay(0),
            pi = [p_t_36_pre, self.p_memread_get, self.p_units],
            pi_w = [take_1_token(), take_some_token(3), take_1_token()],
            po = [self.p_S_STRING_LOADDATA],
            po_w = [pass_token(self.p_units, 1)],
        )


        p_t_30_pre = Place(f"{self.id}_p_t_30_pre")
        
        t_30_pre = Transition(
            id = f"{self.id}_30_pre", 
            delay_func = con_delay(2),
            pi = [self.p_S_SCALAR_DISPATCH_REQ, self.p_hold],
            pi_w = [take_1_token(), take_1_token()],
            po = [p_t_30_pre, self.p_memread_put, self.p_memread_fifo_order],
            po_w = [pass_empty_token(), mem_request(self.port_num, CstStr.SCALAR_DISPATCH_REQ, 1), push_request_order(self.port_num, 1)],
        )

        t_30_post = Transition(
            id = f"{self.id}_30_post", 
            delay_func = con_delay(0),
            pi = [p_t_30_pre, self.p_memread_get, self.p_units],
            pi_w = [take_1_token(), take_1_token(), take_1_token()],
            po = [self.p_outputQ, self.p_S_WRITE_KEY],
            po_w = [pass_scalar_outputQ_token(self.p_units), pass_empty_token()],
        )


        p_t_37_pre = Place(f"{self.id}_p_t_37_pre")
        p_t_37_pre2 = Place(f"{self.id}_p_t_37_pre2")
        p_t_37_pre3 = Place(f"{self.id}_p_t_37_pre3")

        t_37_pre = Transition(
            id = f"{self.id}_37_pre", 
            delay_func = con_delay(0),
            pi = [self.p_S_STRING_LOADDATA],
            pi_w = [take_1_token()],
            po = [p_t_37_pre, p_t_37_pre3, self.p_memread_put, self.p_memread_fifo_order],
            po_w = [pass_16_bytes_outputQ_token(self.p_S_STRING_LOADDATA),  
                    pass_bytes_token(self.p_S_STRING_LOADDATA), 
                    mem_request_v2(self.port_num, CstStr.STRING_LOADDATA_REQ, self.p_S_STRING_LOADDATA),
                    push_request_order_v2(self.port_num, self.p_S_STRING_LOADDATA)
                    ],
        )

        t_37_post = Transition(
            id = f"{self.id}_37_post",
            delay_func = con_delay(0),
            pi = [p_t_37_pre, self.p_memread_get],
            pi_w = [take_1_token(), take_1_token()],
            po = [self.p_outputQ, p_t_37_pre2],
            po_w = [pass_token(p_t_37_pre, 1), pass_empty_token()],
        )

        t_37_post2 = Transition(
            id = f"{self.id}_37_post2",
            delay_func = con_delay(0),
            pi = [p_t_37_pre3, p_t_37_pre2],
            pi_w = [take_1_token(), take_all_tokens(p_t_37_pre3)],
            po = [self.p_S_STRING_WRITE_KEY],
            po_w = [pass_empty_token()]
        )

        p_t_44_pre = Place(f"{self.id}_p_t_44_pre")
        
        t_44_pre = Transition(
            id = f"{self.id}_44_pre", 
            delay_func = con_delay(2),
            pi = [self.p_S_UNPACKED_REP_GETPTR],
            pi_w = [take_1_token()],
            po = [self.p_memread_put, p_t_44_pre, self.p_memread_fifo_order],
            po_w = [mem_request(self.port_num, CstStr.UNPACKED_REP_GETPTR_REQ, 2), 
                    pass_token(self.p_S_UNPACKED_REP_GETPTR, 1),
                    push_request_order(self.port_num, 2)
                    ],
        )

        t_44_post = Transition(
            id = f"{self.id}_44_post", 
            delay_func = con_delay(0),
            pi = [p_t_44_pre, self.p_memread_get],
            pi_w = [take_1_token(), take_some_token(2)],
            po = [self.p_S_SCALAR_DISPATCH_REQ, self.p_S_STRING_GETPTR],
            po_w = [pass_repeated_array_token(p_t_44_pre, CstStr.SCALAR), pass_repeated_array_token(p_t_44_pre, CstStr.NONSCALAR)],
        )


        self.t_list.extend([
            t_30_pre, t_30_post, t_36_pre, t_36_post, t_44_pre, t_44_post, t_37_pre, t_37_post, t_37_post2
        ])


    def init_places(self):
        self.p_S_WAIT_CMD.assign_marking(deque([Token()]))  
        self.p_hold.assign_marking(deque([Token()]))  
        self.p_dist_hold.assign_marking(deque([Token()]))   

    def connect_memread_port(self, memread_port_put_p, memread_port_get_p, memread_fifo_order_p, port_num):
        self.p_memread_put = memread_port_put_p
        self.p_memread_get = memread_port_get_p
        self.p_memread_fifo_order = memread_fifo_order_p
        self.port_num = port_num
        self.__init_additional_ts()
