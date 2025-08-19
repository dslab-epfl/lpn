from lpnlang import lpn_all_nodes
from task_acc_gb.lpn_def.all_enum import CstStr
from task_acc_gb.lpn_def.func import *
from task_acc_gb.lpn_def.helper import *

class GBPE(LPNClassBase):
    def __init__(self, id, finish_buffer, trace):
        super().__init__(id)
        
        '''
        The types are SORT, REORDER, SPOLY, REDUCE
        '''
        self.id = id
        self.task_buffer = Place(f'{id}.task_buffer')  
        self.task_buffer_cap = Place(f'{id}.task_buffer_cap')
        'its fine to share a finish buffer in LPN, in real hardware, there needs to be a separate buffer for each PE'
        self.finished_task_buffer = finish_buffer
        self.trace = trace

    def init_places(self):
        self.task_buffer_cap.assign_marking(deque([Token() for _ in range(4)]))

class REDUCEPE(GBPE):
    def __init__(self, id, finish_buffer, trace):
        super().__init__(id, finish_buffer, trace)
        
        self.reduce_monomials = Transition(
            id = f'{id}.reduce_monomials',
            pi = [self.task_buffer],
            pi_w = [take_1_token()],
            po = [self.finished_task_buffer, self.task_buffer_cap],
            po_w = [pass_token(self.task_buffer, 1), pass_empty_token()],
            # delay_func = reduce_delay(self.task_buffer, self.trace)
            delay_func = con_delay(100)
        )

        self.t_list = [self.reduce_monomials]
    
class SPOLYPE(GBPE):
    def __init__(self, id, finish_buffer, trace):
        super().__init__(id, finish_buffer, trace)
        
        self.spoly_monomials = Transition(
            id = f'{id}.spoly_monomials',
            pi = [self.task_buffer],
            pi_w = [take_1_token()],
            po = [self.finished_task_buffer, self.task_buffer_cap],
            po_w = [pass_token(self.task_buffer, 1), pass_empty_token()],
            delay_func = con_delay(10)
        )

        self.t_list = [self.spoly_monomials]

class REORDERPE(GBPE):
    def __init__(self, id, finish_buffer, trace):
        super().__init__(id, finish_buffer, trace)
        '''
        Assume reoder of one monomials is done in one cycle
        '''
        self.reorder_monomials = Transition(
            id = f'{id}.reorder_monomials',
            pi = [self.task_buffer],
            pi_w = [take_1_token()],
            po = [self.finished_task_buffer, self.task_buffer_cap],
            po_w = [pass_token(self.task_buffer, 1), pass_empty_token()],
            delay_func = con_delay(10)
        )
        self.t_list = [self.reorder_monomials]
  
class SortPE(GBPE):
    def __init__(self, id, finish_buffer, trace):
        super().__init__(id, finish_buffer, trace)
        '''
        Assume comparision of monomials is done in one cycle
        '''
        self.sort_monomials = Transition(
            id = f'{id}.sort_monomials',
            pi = [self.task_buffer],
            pi_w = [take_1_token()],
            po = [self.finished_task_buffer, self.task_buffer_cap],
            po_w = [pass_token(self.task_buffer, 1), pass_empty_token()],
            delay_func = con_delay(100)
        )
        self.t_list = [self.sort_monomials]

class TaskDispatcher(LPNClassBase):
    annoy_buf_cnt = 0
    def create_a_buf(self):
        TaskDispatcher.annoy_buf_cnt += 1
        return Place(f'{self.id}.annybuffer_{TaskDispatcher.annoy_buf_cnt}')
    '''
    Dispatcher also needs to kill a path --> a task generator
        Dispatcher hence needs to keep a few best performing path
    '''
    def __init__(self, id, state_stores, pe_buffers, trace):
        super().__init__(id)
        self.trace = trace
        self.poly_store = state_stores[0]
        self.path_states_store = state_stores[1]

        'stores all possible path'
        self.path_store = state_stores[2]

        poly_read_def = self.poly_store.read_port(0)
        poly_store_def = self.poly_store.write_port(1)
        pss_read_def = self.path_states_store.read_port(0)

        'Token({path_id: _, gen_type:, gen_arg1: cur_poly_id, gen_arg2: total_poly_cnt, gen_arg3: None})'
        self.best_performing_path = Place(f"{id}.best_performing_path")

        '''
        A task_generator_buffer is used to store the generators that will generate tasks
        The buffer is a fifo queue
        '''
        self.task_generator_buffer = Place(f"{id}.task_buffer")

        '''
        NOTE: poly_id increases by 1 each time
        Task generator can be different types

        A path generator generates several spoly-gen generators
        A path generator 
            Token(path_id: _, gen_type: PATH_GEN, gen_arg1: cur_poly_id, gen_arg2: total_poly_cnt, gen_arg3: None)

            This generator stops when cur_poly_id == total_poly_cnt
                    
        A spoly-gen generator 
            Token(path_id: _, gen_type: SPOLY_GEN_GEN, gen_arg1: poly_id, gen_arg2: pair_poly_id, gen_arg3: None)

            this generator stops when pair_poly_id == poly_id

        A non-zero spoly after reduction can create a new spoly-gen generator
            Token(path_id: _, gen_type: SPOLY_GEN_GEN, gen_arg1: spoly_id, gen_arg2: 0, gen_arg3: None) 
        
        A spoly task generates a chain of tasks reorder -> sort -> spoly -> reduce
        A spoly task generator
            Token(path_id: _, gen_type:SPOLY_GEN, gen_arg1: _, gen_arg2: _, gen_arg3: <stage>)
            at stage 0, 1, 2 untill spoly, gen_arg1 store the first poly id, gen_arg2 store the second poly id
            at stage 3, 4 until finish, gen_arg1 store the new spoly id
            the final state of the new poly is REDUCED
        '''
        'a task_generator is used to generate tasks'
        self.task_generator = Transition(f"{id}.task_generator")

        '''
        a task has a path_id, cond, and several task discriptors'
        a poly sort task:
            Token({path_id: _, task_type: SORT, cond: <cond_ref>, task_arg1: <poly_ref>, task_arg2: _, task_arg3: _})
        a poly reorder task:
            Token({path_id: _, task_type: REORDER, cond: <cond_ref>, task_arg1: <poly_ref>, task_arg2: _, task_arg3: _})
        a spoly task:
            Token({path_id: _, task_type: SPOLY, cond: <cond_ref>, task_arg1: <poly_ref>, task_arg2: <poly_ref>, task_arg3: _})
        a reduction task:
            Token({path_id: _, task_type: REDUCE, cond: _, task_arg1: <poly_ref>, task_arg2: <poly_list_ref>, task_arg3: _})
        '''

        'a pe_task_buffer is used to store the tasks will dispatch to the PEs'
        self.pe_task_buffer = Place(f"{id}.task_buffer")
        self.sort_buffer, self.reorder_buffer, self.spoly_buffer, self.reduce_buffer = pe_buffers 

        'a pe_task_dispatcher is used to dispatch the tasks to the PEs'
        self.pe_task_dispatcher = Transition("pe_task_dispatcher")

        buf = self.create_a_buf()

        '''
        request_path_stats is used to request path stats to the path_stats_store
        '''
        self.request_path_stats = Transition(f'{id}.request_path_stats')
        self.ctrl = Place(f'{id}.ctrl')
        self.request_path_stats.p_input = [self.task_generator_buffer, self.best_performing_path, self.ctrl]
        self.request_path_stats.pi_w_threshold = [take_1_token(), take_1_token(), None]
        self.request_path_stats.pi_w = [None, None, take_1_token()]
        self.request_path_stats.p_output = [pss_read_def[0], pss_read_def[2]]
        self.request_path_stats.po_w = [read_path_stats(self.task_generator_buffer, self.best_performing_path, pss_read_def[3])]
        self.request_path_stats.delay_f = con_delay(1)

        '''
        generator manager is used to kill the generator and update best performing path
        each time before spawn a new task, the generator_manager will check the task_generator
        '''
        self.generator_manager = Transition(f'{id}.generator_manager')
        self.generator_manager.p_input = [self.task_generator_buffer, self.best_performing_path, pss_read_def[1], self.path_store]
        self.generator_manager.pi_w = [take_1_token(), take_1_token(), take_some_token(2), take_some_token(0)]
        buf_ctrl_spawn = self.create_a_buf()
        self.generator_manager.p_output = [buf, self.best_performing_path, self.ctrl, buf_ctrl_spawn]
        self.generator_manager.po_w = [exam_task_generator(self.best_performing_path, self.task_generator_buffer, pss_read_def[1], self.path_store)]
        self.generator_manager.delay_f = con_delay(1)

        'NOTE there are two transitions that can produce to task_generator_buffer'
        # new_generators_buf1 = self.create_a_buf()
        # new_generators_buf2 = self.create_a_buf()
        # new_generator_order = self.create_a_buf()
        # new_generator_arbiter = arbiterWTimeOrdHelperNoCap(f'{id}.new_generator_arbiter', [new_generators_buf1, new_generators_buf2], self.task_generator_buffer, new_generator_order)

        self.spawn_new_generator = Transition(f'{id}.spawn_new_generator')
        self.spawn_new_generator.p_input = [buf_ctrl_spawn, self.path_store]
        self.spawn_new_generator.pi_w = [take_1_token(), take_1_token()]
        self.spawn_new_generator.p_output = [self.task_generator_buffer, self.ctrl]
        self.spawn_new_generator.po_w = [pass_token(self.path_store, 1), pass_empty_token()]
        self.spawn_new_generator.delay_f = con_delay(1)

        self.pend_poly_read = PendingOnReq(f'{id}.pending_on_req_read_poly', 
                                            request_ports=poly_read_def)
        
        poly_read_req, requested_num_poly_states = self.pend_poly_read.get_req_buffers()
        poly_read_resp, requested_num_poly_states_resp = self.pend_poly_read.get_resp_buffers()
        
        self.ctrl2 = Place(f'{id}.ctrl2')
        self.prepare_poly_read_req = Transition(f'{id}.prepare_poly_read_req')
        self.prepare_poly_read_req.p_input = [buf, self.ctrl2]
        self.prepare_poly_read_req.pi_w_threshold = [take_1_token(), None]
        self.prepare_poly_read_req.pi_w = [None, take_1_token()]
        self.prepare_poly_read_req.p_output = [poly_read_req, requested_num_poly_states]
        self.prepare_poly_read_req.po_w = [read_poly_states(buf)]
        self.prepare_poly_read_req.delay_f = con_delay(0)
        
        self.pend_poly_update = PendingOnReq(f'{id}.pending_on_req_update_poly', 
                                            request_ports=poly_store_def, 
                                            ctrl_to_produce=self.ctrl2)
        
        poly_update_buf, poly_update_num_buf = self.pend_poly_update.get_req_buffers()
        
        self.task_generator.p_input = [buf, requested_num_poly_states_resp, poly_read_resp]
        self.task_generator.pi_w = [take_1_token(), take_1_token(), take_requested_token(requested_num_poly_states_resp)]
        self.task_generator.p_output = [self.task_generator_buffer, self.pe_task_buffer, poly_update_buf, poly_update_num_buf, self.ctrl2]
        self.task_generator.po_w = [new_generators(buf, poly_read_def[1], trace)]
        self.task_generator.delay_f = con_delay(1)

        'NOTE if the store fails, should kill the path, because there is not enough space to store the poly states'

        self.pe_task_dispatcher.p_input = [self.pe_task_buffer]
        self.pe_task_dispatcher.pi_w = [take_1_token()]
        self.pe_task_dispatcher.p_output = [self.sort_buffer, self.reorder_buffer, self.spoly_buffer, self.reduce_buffer]
        self.pe_task_dispatcher.po_w = [dispatch_pe(self.pe_task_buffer)]

        self.pe_task_dispatcher.delay_f = con_delay(1)
        self.comp_list = [self.pend_poly_update, self.pend_poly_read]
        self.t_list = [self.request_path_stats, self.generator_manager, self.spawn_new_generator, self.task_generator, self.pe_task_dispatcher, self.prepare_poly_read_req]
        for comp in self.comp_list:
            self.t_list.extend(comp.transitions())

    def init_places(self):
        print(f"{self.id} init places")
        self.ctrl.push_token(Token())
        self.ctrl2.push_token(Token())
        self.best_performing_path.push_token(Token({"path_id": 0, "gen_type": CstStr.PATH_GEN, "gen_arg1": 0, "gen_arg2": 0, "gen_arg3": None}))

class TaskCollector(LPNClassBase):
    def __init__(self, id, states_store, pe_task_finish_buffer, trace):
        '''
        we are cheating here by not computing anything in the LPN, but leverages func_sim trace directly
        '''
        self.trace = trace

        poly_store = states_store[0]
        path_states_store = states_store[1]

        'the port_def are 0:write_req, 1:write_resp, 2:order, 3:idx'
        poly_store_write_port_def = poly_store.write_port(0)
        pss_write_port_def = path_states_store.write_port(1)
        
        self.pe_task_finish_buffer = pe_task_finish_buffer
        self.ctrl = Place(f"{id}.ctrl")
        self.collect_finish_task = Transition(f"{id}.collect_finish_task")
        self.collect_finish_task.p_input = [self.pe_task_finish_buffer, self.ctrl]
        self.collect_finish_task.pi_w = [take_1_token(), take_1_token()]
        self.collect_finish_task.p_output = [poly_store_write_port_def[0], poly_store_write_port_def[2], pss_write_port_def[0], pss_write_port_def[2]]
        self.collect_finish_task.po_w = [update_poly_state(self.pe_task_finish_buffer, poly_store_write_port_def[3], pss_write_port_def[3], self.trace)]
        self.collect_finish_task.delay_f = con_delay(1)

        self.wait_for_store_update = Transition(f"{id}.wait_for_store_update")
        self.wait_for_store_update.p_input = [poly_store_write_port_def[1]]
        self.wait_for_store_update.pi_w = [take_1_token()]
        self.wait_for_store_update.p_output = [self.ctrl]
        self.wait_for_store_update.po_w = [pass_empty_token()]
        self.wait_for_store_update.delay_f = con_delay(1)

        self.t_list = [self.collect_finish_task, self.wait_for_store_update]

    def init_places(self):
        self.ctrl.push_token(Token())

class TaskGBAcc(LPNClassBase):
    def __init__(self, id, max_concurrent_path, num_PEs_each_type, trace):
        super().__init__(id)

        self.trace = trace
        self.max_concurrent_path = max_concurrent_path
        '''
        create all data stores
        meant to be internal to the accelerator
        Note, a write may never return because not enough space in the store
        '''
        
        'poly store states only increases'
        self.poly_store = StateStoreMultiple("poly_store", True, 2, 2)

        '''
        includes stats of the path: for exampe num of tasks will be generate
        A token in the path_stats will be like:
            Token({path_id: _, stats1: generated_tasks, stats2: task_avg_cycle_cnt})
        '''
        self.path_states_store = StateStore("path_states_store", False, 2, 2)

        self.path_fifo = Place(f"{id}.path_fifo")
        data_stores = [self.poly_store, self.path_states_store, self.path_fifo]

        pe_sort_buffer = Place(f"{id}.sort_buffer")
        pe_reorder_buffer = Place(f"{id}.reorder_buffer")
        pe_spoly_buffer = Place(f"{id}.spoly_buffer")
        pe_reduce_buffer = Place(f"{id}.reduce_buffer")

        pe_buffers = [pe_sort_buffer, pe_reorder_buffer, pe_spoly_buffer, pe_reduce_buffer]

        pe_task_finish_buffer = Place(f"{id}.pe_task_finish_buffer")
        self.dispatcher = TaskDispatcher("task_dispatcher", data_stores, pe_buffers, trace)
        self.collector = TaskCollector("task_collector", data_stores, pe_task_finish_buffer, trace)

        '''
        Create all PEs
        '''
        sort_PEs = []
        reorder_PEs = []
        spoly_PEs = []
        reduce_PEs = []

        # how do you balance the PEs?
        for i in range(num_PEs_each_type):
            sort_PEs.append(SortPE(f'sort_{i}', pe_task_finish_buffer, trace))
            reorder_PEs.append(REORDERPE(f'reorder_{i}', pe_task_finish_buffer, trace))
        
        for i in range(num_PEs_each_type):
            spoly_PEs.append(SPOLYPE(f'spoly_{i}', pe_task_finish_buffer, trace))
        
        for i in range(num_PEs_each_type):
            reduce_PEs.append(REDUCEPE(f'reduce_{i}', pe_task_finish_buffer, trace))

        list_of_dispatchers = []
        list_of_dispatchers.append(
            Dispatcher(f'{id}.sort_dispatcher', pe_sort_buffer, [pe.task_buffer for pe in sort_PEs], [pe.task_buffer_cap for pe in sort_PEs])
        )
        list_of_dispatchers.append(
            Dispatcher(f'{id}.reorder_dispatcher', pe_reorder_buffer, [pe.task_buffer for pe in reorder_PEs], [pe.task_buffer_cap for pe in reorder_PEs])
        )
        list_of_dispatchers.append(
            Dispatcher(f'{id}.spoly_dispatcher', pe_spoly_buffer, [pe.task_buffer for pe in spoly_PEs], [pe.task_buffer_cap for pe in spoly_PEs])
        )
        list_of_dispatchers.append(
            Dispatcher(f'{id}.reduce_dispatcher', pe_reduce_buffer, [pe.task_buffer for pe in reduce_PEs], [pe.task_buffer_cap for pe in reduce_PEs])
        )
        
        '''
        collect all comp and transitions
        '''
        for PEs in sort_PEs, reorder_PEs, spoly_PEs, reduce_PEs:
            for pe in PEs:
                self.comp_list.append(pe)

        self.comp_list.extend([self.dispatcher, self.collector, self.poly_store, self.path_states_store])
        self.comp_list.extend(list_of_dispatchers)
        for comp in self.comp_list:
            self.t_list.extend(comp.t_list)

    def init_places(self):
        for comp in self.comp_list:
            comp.init_places()
        
    def setup_path(self, path_list):
        for i, path in enumerate(path_list):
            id, poly_nums = path
            print(f"Setting up path {id}, poly_nums {poly_nums}")
            token = Token({"path_id": id, "gen_type": CstStr.PATH_GEN, "gen_arg1": 1, "gen_arg2": poly_nums, "gen_arg3": None})
            self.poly_store.add_store(id)
            self.path_states_store.add_state(id, {"stats1": 0, "stats2": 0})
            if i >= self.max_concurrent_path:
                # store in path_fifo
                self.path_fifo.push_token(token)
            else:
                self.dispatcher.task_generator_buffer.push_token(token)
                'NOTE this is just to avoid the case where the poly is None in the state'
                for poly_i in self.trace[i]['poly_stats'].keys():
                    if poly_i < poly_nums:
                        self.poly_store.add_state(id, poly_i, CstStr.INITIAL)
                    else:
                        self.poly_store.add_state(id, poly_i, CstStr.EMPTY)


       