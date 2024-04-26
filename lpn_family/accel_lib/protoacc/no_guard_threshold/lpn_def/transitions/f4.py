from lpnlang import Place, Transition
from lpn_def.funcs.funcs import *
from lpn_def.places.places import *

def f4_ts():

    tdispatch_f4 = Transition(
        id = "dispatch_f4", 
        delay_func = con_delay(1),
        pi = [ptofieldhandler_dispatcher, pdispatch_index_holder_f4, pfields],
        pi_w = [take_1_token(), take_1_token(), take_num_field_tokens(ptofieldhandler_dispatcher)],
        po = [pdispatch_hold, pops_in_f4, pf4_units, pf4_num_units, pfields],
        po_w = [pass_empty_token(), pass_token(ptofieldhandler_dispatcher, 1), pass_field_token(ptofieldhandler_dispatcher, pfields), pass_num_field_token(ptofieldhandler_dispatcher), pass_field_token(ptofieldhandler_dispatcher, pfields)], # return to pfields after fetch
        )

    tf4_resume = Transition(
        id = "f4_resume",
        delay_func = con_delay(0),
        pi = [pf4_num_units, pf4_finished],
        pi_w = [take_1_token(), take_resume_token(pf4_num_units)],
        po = [pf4_S_WAIT_CMD, pf4_outputQ],
        po_w = [pass_empty_token(), pass_field_end_token()],
        )
    

    tf4_dist = Transition(
        id = "f4_dist", 
        delay_func = con_delay(0),
        pi = [pops_in_f4, pf4_dist_hold],
        pi_w = [take_1_token(), take_1_token()],
        po = [pops_in_f4_eom, pops_in_f4_scalar, pops_in_f4_non_scalar, pops_in_f4_repeated],
        po_w = [pass_eom(pops_in_f4), pass_scalar(pops_in_f4), pass_non_scalar(pops_in_f4), pass_repeated(pops_in_f4)],
    )

    tf4_eom = Transition(
        id = "f4_eom", 
        delay_func = con_delay(2),
        pi = [pops_in_f4_eom, pf4_S_WAIT_CMD, pf4_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf4_outputQ, pf4_finished, pf4_dist_hold],
        po_w = [pass_key_outputQ_end_of_toplevel_token(pops_in_f4_eom), pass_empty_token(), pass_empty_token()],
    )

    tf4_25 = Transition(
        id = "f4_25", 
        delay_func = con_delay(1),
        pi = [pops_in_f4_scalar, pf4_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf4_S_SCALAR_DISPATCH_REQ, pf4_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf4_26 = Transition(
        id = "f4_26", 
        delay_func = con_delay(1),
        pi = [pops_in_f4_non_scalar, pf4_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf4_S_STRING_GETPTR, pf4_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf4_28 = Transition(
        id = "f4_28", 
        delay_func = con_delay(1),
        pi = [pops_in_f4_repeated, pf4_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf4_S_UNPACKED_REP_GETPTR, pf4_dist_hold],
        po_w = [pass_token(pops_in_f4_repeated, 1), pass_empty_token()],
    )

    tf4_30 = Transition(
        id = "f4_30", 
        delay_func = con_delay(2+10),
        pi = [pf4_S_SCALAR_DISPATCH_REQ, pf4_hold, pf4_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf4_outputQ, pf4_S_WRITE_KEY],
        po_w = [pass_scalar_outputQ_token(pf4_units), pass_empty_token()],
    )

    tf4_31 = Transition(
        id = "f4_31", 
        delay_func = con_delay(1),
        pi = [pf4_S_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf4_finished, pf4_hold, pf4_outputQ],
        po_w = [pass_empty_token(), pass_empty_token(), pass_key_outputQ_token()],
    )

    tf4_36 = Transition(
        id = "f4_36", 
        delay_func = con_delay(4+2*10),
        pi = [pf4_S_STRING_GETPTR, pf4_hold,  pf4_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf4_S_STRING_LOADDATA],
        po_w = [pass_token(pf4_units, 1)],
    )

    tf4_37 = Transition(
        id = "f4_37", 
        delay_func = all_bytes_delay(pf4_S_STRING_LOADDATA),
        pi = [pf4_S_STRING_LOADDATA],
        pi_w = [take_1_token()],
        po = [pf4_outputQ, pf4_S_STRING_WRITE_KEY],
        po_w = [pass_all_bytes_outputQ_token(pf4_S_STRING_LOADDATA), pass_empty_token()],
    )

    tf4_40 = Transition(
        id = "f4_40", 
        delay_func = con_delay(1),
        pi = [pf4_S_STRING_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf4_finished, pf4_outputQ, pf4_hold],
        po_w = [pass_empty_token(), pass_key_outputQ_token(), pass_empty_token() ],
    )

    tf4_44 = Transition(
        id = "f4_44", 
        delay_func = con_delay(3+10),
        pi = [pf4_S_UNPACKED_REP_GETPTR],
        pi_w = [take_1_token()],
        po = [pf4_S_SCALAR_DISPATCH_REQ, pf4_S_STRING_GETPTR],
        po_w = [pass_repeated_array_token(pf4_S_UNPACKED_REP_GETPTR, CstStr.SCALAR), pass_repeated_array_token(pf4_S_UNPACKED_REP_GETPTR, CstStr.NONSCALAR)],
    )

    tf4_memconnect = Transition(
        id = "f4_memconnect", 
        delay_func = mem_read_delay(),
        pi = [pf4_memreadReq],
        pi_w = [take_1_token()],
        po = [pf4_memreadResp],
        po_w = [pass_empty_token()],
        pip = con_delay(1)
    )

    tf4_write_req_out = Transition(
        id = "f4_write_req_out", 
        delay_func = field_end_cond_delay(pf4_outputQ),
        pi = [pf4_outputQ, pwrite_index_holder_f4],
        pi_w = [take_1_token(), take_1_token()],
        po = [pwrites_input_IF_Q, pwrite_hold, pwrite_index_holder_f4],
        po_w = [pass_non_field_end_token(pf4_outputQ, 1), pass_write_hold_cond(pf4_outputQ),  pass_write_index_holder_cond(pf4_outputQ, pwrite_index_holder_f4)],
        )

    return [tdispatch_f4,tf4_25, tf4_26, tf4_28, tf4_30, tf4_31, tf4_36, tf4_37, tf4_40, tf4_44, tf4_memconnect, tf4_write_req_out, tf4_resume, tf4_eom, tf4_dist]
