from DMA.lpn_def.dma_ports import *
from DMA.lpn_def.helper import arbiterWTimeOrdHelperNoCap
from task_acc_gb.lpn_def.func import *

pend_send_req = OutWeightFuncA("pend_send_req", buf=Place, req_num_buf=Place, req_idx=int)
@pend_send_req.install
def output_tokens(binding, output_places, buf, req_num_buf, req_idx):
    num = prop_value(binding, req_num_buf, 0, "num")
    for i in range(num):
        token = get_token(binding, buf, i).copy()
        token.set_prop("requester", req_idx)
        output_places[0].push_token(token)
        output_places[1].push_token(Token({"idx": req_idx}))

    output_places[2].push_token(get_token(binding, req_num_buf, 0))


def create_dispatcher(id, inp_buf, list_of_out_buf, list_of_out_buf_cap, porder_keeper):
    total = len(list_of_out_buf)
    take_0_or_1 = InWeightFunc(f"arbiterhelperord_take_0_or_1", my_idx=int, porder_keeper=Place)
    @take_0_or_1.install    
    def weight(binding, my_idx, porder_keeper):
        cur_turn = prop_value(binding, porder_keeper, 0, "idx")
        if cur_turn == my_idx:
            return 1
        else:
            return 0

    dispatcher_output = OutWeightFuncA("dispatcher_output", input_buf=Place, porder_keeper=Place)
    @dispatcher_output.install
    def output_tokens(binding, output_places, input_buf, porder_keeper):
        cur_turn = prop_value(binding, porder_keeper, 0, "idx")
        token = Token({"idx": (cur_turn+1)%total})
        output_places[0].push_token(token)

        cur_turn = prop_value(binding, porder_keeper, 0, "idx")
        token = get_token(binding, input_buf, 0)
        output_places[1+cur_turn].push_token(token)


    dispatcher = Transition(
        id = f"{id}",
        delay_func=con_delay(0),
        pi=[porder_keeper, inp_buf, *list_of_out_buf_cap],
        pi_w=[take_1_token(), take_1_token(), *[take_0_or_1(idx, porder_keeper) for idx in range(total)] ], 
        po=[porder_keeper, *list_of_out_buf],
        po_w=[dispatcher_output(inp_buf, porder_keeper)]
    )
    
    return dispatcher

class Dispatcher(LPNClassBase):
    def __init__(self, id, inp_buf, list_of_out_buf, list_of_out_buf_cap):
        super().__init__(id)
        self.porder_keeper = Place(f"{id}.porder_keeper")
        self.t_list.append(create_dispatcher(id, inp_buf, list_of_out_buf, list_of_out_buf_cap, self.porder_keeper))
    def init_places(self):
        self.porder_keeper.push_token(Token({"idx": 0}))

class PendingOnReq(LPNClassBase):
    '''
    This creates a LPN than can append on request and wait for response
    ctrl is used to halt the parent while waiting for response
    request_func is a custom function that takes a buffer and request index, then sends out the real request 
    '''
    def __init__(self, id, request_ports, 
                 ctrl_to_consume=None, 
                 ctrl_to_produce=None, 
                 ):
        super().__init__(id)
        self.request_buf = Place(f"{id}.request_buf")
        self.requested_num_buf = Place(f"{id}.requested_num_buf") 
        self.requested_num_buf_resp = Place(f"{id}.requested_num_buf_resp") 
        self._internal_buf = Place(f"{id}._internal_buf")
        req_buf, resp_buf, req_order, req_idx = request_ports
        self.resp_buf = resp_buf
        self.send_request = Transition(f'{id}.send_request')
        self.send_request.p_input = [self.requested_num_buf, self.request_buf]
        self.send_request.pi_w = [take_1_token(), take_requested_token(self.requested_num_buf)]

        if ctrl_to_consume is not None:
            self.send_request.p_input.append(ctrl_to_consume)
            self.send_request.pi_w.append(take_1_token())

        self.send_request.p_output = [req_buf, req_order, self._internal_buf]
        self.send_request.po_w = [pend_send_req(self.request_buf, self.requested_num_buf, req_idx)]
        self.send_request.delay_f = con_delay(1)
        
        self.wait_for_request = Transition(f'{id}.wait_for_request')
        self.wait_for_request.p_input = [self._internal_buf, resp_buf]
        self.wait_for_request.pi_w_threshold = [None, take_requested_token(self._internal_buf)]
        self.wait_for_request.pi_w = [take_1_token(), take_some_token(0)]
        self.wait_for_request.delay_f = con_delay(0)
        self.wait_for_request.p_output = [self.requested_num_buf_resp]
        self.wait_for_request.po_w = [pass_token(self._internal_buf, 1)]

        if ctrl_to_produce is not None:
            self.wait_for_request.p_output.append(ctrl_to_produce)
            self.wait_for_request.po_w.append(pass_empty_token())
        
        self.t_list = [self.send_request, self.wait_for_request]

    def get_req_buffers(self):
        '''
        request and number of requests to wait needs to be filled in
        '''
        return self.request_buf, self.requested_num_buf
    
    def get_resp_buffers(self):
        return self.resp_buf, self.requested_num_buf_resp
    
class StateStore(LPNClassBase):
    def __init__(self, id, inc_only, num_reader, num_writer):
        super().__init__(id)
        '''
        Let's have a control token to arbitrate read and write operations
        '''
        self.rdwr_serialized = Place(f"{id}.rdwr_serialized")

        'stores the tokens for states'
        # self.state_store = Place(f"{id}.state_store")
        self.state_store = {}

        'request token {requester: _, state_id:_, rd_or_wr:_, state_data:_, piggyback: _}'
        'response token {requester: _, state_id:_, rd_or_wr:_, state_data:_, piggyback: _}'
        
        'read request buf'
        self.rd_req_list = []
        self.rd_resp_list = []
        for i in range(num_reader):
            self.rd_req_list.append(Place(f"{id}.rd_req_{i}"))
            self.rd_resp_list.append(Place(f"{id}.rd_resp_{i}"))

        'write request buf'
        self.wr_req_list = []
        self.wr_resp_list = []
        for i in range(num_writer):
            self.wr_req_list.append(Place(f"{id}.wr_req_{i}"))
            self.wr_resp_list.append(Place(f"{id}.wr_resp_{i}"))

        'read_write_order_buf'
        self.rdwr_order = Place(f"{id}.rdwr_order")

        arbiter = arbiterWTimeOrdHelperNoCap(f"{id}_arbiter", [*self.rd_req_list, *self.wr_req_list], self.rdwr_serialized, self.rdwr_order)
        process_req = Transition(f"{id}_process_req")
        process_req.delay_f = con_delay(2)
        process_req.p_input = [self.rdwr_serialized]
        process_req.pi_w = [take_1_token()]
        process_req.p_output = [*self.rd_resp_list, *self.wr_resp_list]
        process_req.po_w = [process_state_req(self.rdwr_serialized, self.state_store, inc_only)]
        self.t_list = [arbiter, process_req]
    
    def add_state(self, state_id, state_data):
        # token = Token({"state_id": state_id, "state_data": state_data})
        # self.state_store.push_token(token)
        self.state_store[state_id] = state_data

    def read_port(self, idx):
        return self.rd_req_list[idx], self.rd_resp_list[idx], self.rdwr_order, idx

    def write_port(self, idx):
        return self.wr_req_list[idx], self.wr_resp_list[idx], self.rdwr_order, idx+len(self.rd_req_list)

class StateStoreMultiple(LPNClassBase):
    def __init__(self, id, inc_only, num_reader, num_writer):
        super().__init__(id)
        '''
        Let's have a control token to arbitrate read and write operations
        '''
        self.rdwr_serialized = Place(f"{id}.rdwr_serialized")

        'stores the tokens for states'
        self.state_store_dict = {}

        'request token {requester: _, state_id:_, rd_or_wr:_, state_data:_, piggyback: _}'
        'response token {requester: _, state_id:_, rd_or_wr:_, state_data:_, piggyback: _}'
        
        'read request buf'
        self.rd_req_list = []
        self.rd_resp_list = []
        for i in range(num_reader):
            self.rd_req_list.append(Place(f"{id}.rd_req_{i}"))
            self.rd_resp_list.append(Place(f"{id}.rd_resp_{i}"))

        'write request buf'
        self.wr_req_list = []
        self.wr_resp_list = []
        for i in range(num_writer):
            self.wr_req_list.append(Place(f"{id}.wr_req_{i}"))
            self.wr_resp_list.append(Place(f"{id}.wr_resp_{i}"))

        'read_write_order_buf'
        self.rdwr_order = Place(f"{id}.rdwr_order")

        arbiter = arbiterWTimeOrdHelperNoCap(f"{id}.arbiter", [*self.rd_req_list, *self.wr_req_list], self.rdwr_serialized, self.rdwr_order)
        process_req = Transition(f"{id}_process_req")
        process_req.delay_f = con_delay(2)
        process_req.p_input = [self.rdwr_serialized]
        process_req.pi_w = [take_1_token()]
        process_req.p_output = [*self.rd_resp_list, *self.wr_resp_list]
        process_req.po_w = [process_state_req_multi(self.rdwr_serialized, self.state_store_dict, inc_only)]
        self.t_list = [arbiter, process_req]
    
    def add_store(self, store_id):
        # self.state_store_dict[store_id] = Place(f"{self.id}_state_store_{store_id}")
        self.state_store_dict[store_id] = {}

    def add_state(self, store_id, state_id, state_data):
        # token = Token({"state_id": state_id, "state_data": state_data})
        # self.state_store_dict[store_id].push_token(token)
        self.state_store_dict[store_id][state_id] = state_data

    def read_port(self, idx):
        return self.rd_req_list[idx], self.rd_resp_list[idx], self.rdwr_order, idx

    def write_port(self, idx):
        return self.wr_req_list[idx], self.wr_resp_list[idx], self.rdwr_order, idx+len(self.rd_req_list)
