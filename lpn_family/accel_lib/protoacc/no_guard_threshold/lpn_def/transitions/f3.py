from lpnlang import Place, Transition
from lpn_def.funcs.funcs import *
from lpn_def.places.places import *

def f3_ts():

    tdispatch_f3 = Transition(
        id = "dispatch_f3", 
        delay_func = con_delay(1),
        pi = [ptofieldhandler_dispatcher, pdispatch_index_holder_f3, pfields],
        pi_w = [take_1_token(), take_1_token(), take_num_field_tokens(ptofieldhandler_dispatcher)],
        po = [pdispatch_hold, pops_in_f3, pf3_units, pf3_num_units, pfields],
        po_w = [pass_empty_token(), pass_token(ptofieldhandler_dispatcher, 1), pass_field_token(ptofieldhandler_dispatcher, pfields), pass_num_field_token(ptofieldhandler_dispatcher), pass_field_token(ptofieldhandler_dispatcher, pfields)], # return to pfields after fetch
        )

    tf3_resume = Transition(
        id = "f3_resume",
        delay_func = con_delay(0),
        pi = [pf3_num_units, pf3_finished],
        pi_w = [take_1_token(), take_resume_token(pf3_num_units)],
        po = [pf3_S_WAIT_CMD, pf3_outputQ],
        po_w = [pass_empty_token(), pass_field_end_token()],
        )
    

    tf3_dist = Transition(
        id = "f3_dist", 
        delay_func = con_delay(0),
        pi = [pops_in_f3, pf3_dist_hold],
        pi_w = [take_1_token(), take_1_token()],
        po = [pops_in_f3_eom, pops_in_f3_scalar, pops_in_f3_non_scalar, pops_in_f3_repeated],
        po_w = [pass_eom(pops_in_f3), pass_scalar(pops_in_f3), pass_non_scalar(pops_in_f3), pass_repeated(pops_in_f3)],
    )

    tf3_eom = Transition(
        id = "f3_eom", 
        delay_func = con_delay(2),
        pi = [pops_in_f3_eom, pf3_S_WAIT_CMD, pf3_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf3_outputQ, pf3_finished, pf3_dist_hold],
        po_w = [pass_key_outputQ_end_of_toplevel_token(pops_in_f3_eom), pass_empty_token(), pass_empty_token()],
    )

    tf3_25 = Transition(
        id = "f3_25", 
        delay_func = con_delay(1),
        pi = [pops_in_f3_scalar, pf3_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf3_S_SCALAR_DISPATCH_REQ, pf3_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf3_26 = Transition(
        id = "f3_26", 
        delay_func = con_delay(1),
        pi = [pops_in_f3_non_scalar, pf3_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf3_S_STRING_GETPTR, pf3_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf3_28 = Transition(
        id = "f3_28", 
        delay_func = con_delay(1),
        pi = [pops_in_f3_repeated, pf3_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf3_S_UNPACKED_REP_GETPTR, pf3_dist_hold],
        po_w = [pass_token(pops_in_f3_repeated, 1), pass_empty_token()],
    )

    tf3_30 = Transition(
        id = "f3_30", 
        delay_func = con_delay(2+10),
        pi = [pf3_S_SCALAR_DISPATCH_REQ, pf3_hold, pf3_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf3_outputQ, pf3_S_WRITE_KEY],
        po_w = [pass_scalar_outputQ_token(pf3_units), pass_empty_token()],
    )

    tf3_31 = Transition(
        id = "f3_31", 
        delay_func = con_delay(1),
        pi = [pf3_S_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf3_finished, pf3_hold, pf3_outputQ],
        po_w = [pass_empty_token(), pass_empty_token(), pass_key_outputQ_token()],
    )

    tf3_36 = Transition(
        id = "f3_36", 
        delay_func = con_delay(4+2*10),
        pi = [pf3_S_STRING_GETPTR, pf3_hold,  pf3_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf3_S_STRING_LOADDATA],
        po_w = [pass_token(pf3_units, 1)],
    )

    tf3_37 = Transition(
        id = "f3_37", 
        delay_func = all_bytes_delay(pf3_S_STRING_LOADDATA),
        pi = [pf3_S_STRING_LOADDATA],
        pi_w = [take_1_token()],
        po = [pf3_outputQ, pf3_S_STRING_WRITE_KEY],
        po_w = [pass_all_bytes_outputQ_token(pf3_S_STRING_LOADDATA), pass_empty_token()],
    )

    tf3_40 = Transition(
        id = "f3_40", 
        delay_func = con_delay(1),
        pi = [pf3_S_STRING_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf3_finished, pf3_outputQ, pf3_hold],
        po_w = [pass_empty_token(), pass_key_outputQ_token(), pass_empty_token() ],
    )

    tf3_44 = Transition(
        id = "f3_44", 
        delay_func = con_delay(3+10),
        pi = [pf3_S_UNPACKED_REP_GETPTR],
        pi_w = [take_1_token()],
        po = [pf3_S_SCALAR_DISPATCH_REQ, pf3_S_STRING_GETPTR],
        po_w = [pass_repeated_array_token(pf3_S_UNPACKED_REP_GETPTR, CstStr.SCALAR), pass_repeated_array_token(pf3_S_UNPACKED_REP_GETPTR, CstStr.NONSCALAR)],
    )

    tf3_memconnect = Transition(
        id = "f3_memconnect", 
        delay_func = mem_read_delay(),
        pi = [pf3_memreadReq],
        pi_w = [take_1_token()],
        po = [pf3_memreadResp],
        po_w = [pass_empty_token()],
        pip = con_delay(1)
    )

    tf3_write_req_out = Transition(
        id = "f3_write_req_out", 
        delay_func = field_end_cond_delay(pf3_outputQ),
        pi = [pf3_outputQ, pwrite_index_holder_f3],
        pi_w = [take_1_token(), take_1_token()],
        po = [pwrites_input_IF_Q, pwrite_hold, pwrite_index_holder_f3],
        po_w = [pass_non_field_end_token(pf3_outputQ, 1), pass_write_hold_cond(pf3_outputQ),  pass_write_index_holder_cond(pf3_outputQ, pwrite_index_holder_f3)],
        )

    return [tdispatch_f3,tf3_25, tf3_26, tf3_28, tf3_30, tf3_31, tf3_36, tf3_37, tf3_40, tf3_44, tf3_memconnect, tf3_write_req_out, tf3_resume, tf3_eom, tf3_dist]
