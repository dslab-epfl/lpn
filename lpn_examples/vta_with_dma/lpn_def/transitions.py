from lpnlang import Place, Transition, Token
from .places import *
from .expr_i import *
from .expr_o import *
from .expr_guard import *
from .delay_func import *
from .all_enum import CstStr

t13 = Transition(
    id = "t13", 
    delay_func = con_delay(0), 
    pi=[plaunch],
    po=[psReadCmd],
    pi_w=[take_1_token()], 
    po_w=[output_insn_read_cmd(plaunch)],
)

t9 = Transition(
    id = "t9", 
    delay_func = delay_t9(psReadCmd),
    pi=[psReadCmd, pcontrol, pnumInsn], 
    po=[psDrain, pcontrol_prime], 
    pi_w=[take_1_token(), take_1_token(), take_readLen(psReadCmd)], 
    po_w=[pass_var_token_readLen(pnumInsn, psReadCmd), pass_empty_token()]
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
    po=[pload_process], 
    pi_w=[take_1_token(), take_dep_pop_next(pload_inst_q)], 
    po_w=[pass_token(pload_inst_q, 1)], 
)

tload_done = Transition(
    id = "load_done",
    delay_func = delay_load(pload_process), 
    pi=[pload_process], 
    po=[pload_done, pload2compute, pload_cap], 
    pi_w=[take_1_token()], 
    po_w=[pass_empty_token(), output_dep_push_next(pload_process), pass_empty_token()], 
) 

tstore_launch = Transition(
    id = "store_launch", 
    delay_func = con_delay(0), 
    pi=[pstore_inst_q, pcompute2store], 
    po=[pstore_process], 
    pi_w=[take_1_token(), take_dep_pop_prev(pstore_inst_q)], 
    po_w=[pass_token(pstore_inst_q, 1)], 
)

tstore_done = Transition(
    id = "store_done",
    delay_func = delay_store(pstore_process), 
    pi=[pstore_process], 
    po=[pstore_done, pstore2compute, pstore_cap], 
    pi_w=[take_1_token()], 
    po_w=[pass_empty_token(), output_dep_push_prev(pstore_process), pass_empty_token()], 
)

tcompute_launch = Transition(
    id = "compute_launch", 
    delay_func = con_delay(0), 
    pi=[pcompute_inst_q, pstore2compute, pload2compute], 
    po=[pcompute_process], 
    pi_w=[take_1_token(), take_dep_pop_next(pcompute_inst_q), take_dep_pop_prev(pcompute_inst_q)], 
    po_w=[pass_token(pcompute_inst_q, 1)], 
)

tcompute_done = Transition(
    id = "compute_done",
    delay_func = delay_compute(pcompute_process), 
    pi=[pcompute_process], 
    po=[pcompute_done, pcompute2load, pcompute2store, pcompute_cap], 
    pi_w=[take_1_token()], 
    po_w=[pass_empty_token(), output_dep_push_prev(pcompute_process), output_dep_push_next(pcompute_process),  pass_empty_token()], 
)
