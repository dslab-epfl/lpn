from lpnlang import Place, Transition
from lpn_def.funcs.funcs import *
from lpn_def.places.places import *

def f6_ts():

    tdispatch_f6 = Transition(
        id = "dispatch_f6", 
        delay_func = con_delay(1),
        pi = [ptofieldhandler_dispatcher, pdispatch_index_holder_f6, pfields],
        pi_w = [take_1_token(), take_1_token(), take_num_field_tokens(ptofieldhandler_dispatcher)],
        po = [pdispatch_hold, pops_in_f6, pf6_units, pf6_num_units, pfields],
        po_w = [pass_empty_token(), pass_token(ptofieldhandler_dispatcher, 1), pass_field_token(ptofieldhandler_dispatcher, pfields), pass_num_field_token(ptofieldhandler_dispatcher), pass_field_token(ptofieldhandler_dispatcher, pfields)], # return to pfields after fetch
        )

    tf6_resume = Transition(
        id = "f6_resume",
        delay_func = con_delay(0),
        pi = [pf6_num_units, pf6_finished],
        pi_w = [take_1_token(), take_resume_token(pf6_num_units)],
        po = [pf6_S_WAIT_CMD, pf6_outputQ],
        po_w = [pass_empty_token(), pass_field_end_token()],
        )
    

    tf6_dist = Transition(
        id = "f6_dist", 
        delay_func = con_delay(0),
        pi = [pops_in_f6, pf6_dist_hold],
        pi_w = [take_1_token(), take_1_token()],
        po = [pops_in_f6_eom, pops_in_f6_scalar, pops_in_f6_non_scalar, pops_in_f6_repeated],
        po_w = [pass_eom(pops_in_f6), pass_scalar(pops_in_f6), pass_non_scalar(pops_in_f6), pass_repeated(pops_in_f6)],
    )

    tf6_eom = Transition(
        id = "f6_eom", 
        delay_func = con_delay(2),
        pi = [pops_in_f6_eom, pf6_S_WAIT_CMD, pf6_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf6_outputQ, pf6_finished, pf6_dist_hold],
        po_w = [pass_key_outputQ_end_of_toplevel_token(pops_in_f6_eom), pass_empty_token(), pass_empty_token()],
    )

    tf6_25 = Transition(
        id = "f6_25", 
        delay_func = con_delay(1),
        pi = [pops_in_f6_scalar, pf6_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf6_S_SCALAR_DISPATCH_REQ, pf6_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf6_26 = Transition(
        id = "f6_26", 
        delay_func = con_delay(1),
        pi = [pops_in_f6_non_scalar, pf6_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf6_S_STRING_GETPTR, pf6_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf6_28 = Transition(
        id = "f6_28", 
        delay_func = con_delay(1),
        pi = [pops_in_f6_repeated, pf6_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf6_S_UNPACKED_REP_GETPTR, pf6_dist_hold],
        po_w = [pass_token(pops_in_f6_repeated, 1), pass_empty_token()],
    )

    tf6_30 = Transition(
        id = "f6_30", 
        delay_func = con_delay(2+10),
        pi = [pf6_S_SCALAR_DISPATCH_REQ, pf6_hold, pf6_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf6_outputQ, pf6_S_WRITE_KEY],
        po_w = [pass_scalar_outputQ_token(pf6_units), pass_empty_token()],
    )

    tf6_31 = Transition(
        id = "f6_31", 
        delay_func = con_delay(1),
        pi = [pf6_S_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf6_finished, pf6_hold, pf6_outputQ],
        po_w = [pass_empty_token(), pass_empty_token(), pass_key_outputQ_token()],
    )

    tf6_36 = Transition(
        id = "f6_36", 
        delay_func = con_delay(4+2*10),
        pi = [pf6_S_STRING_GETPTR, pf6_hold,  pf6_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf6_S_STRING_LOADDATA],
        po_w = [pass_token(pf6_units, 1)],
    )

    tf6_37 = Transition(
        id = "f6_37", 
        delay_func = all_bytes_delay(pf6_S_STRING_LOADDATA),
        pi = [pf6_S_STRING_LOADDATA],
        pi_w = [take_1_token()],
        po = [pf6_outputQ, pf6_S_STRING_WRITE_KEY],
        po_w = [pass_all_bytes_outputQ_token(pf6_S_STRING_LOADDATA), pass_empty_token()],
    )

    tf6_40 = Transition(
        id = "f6_40", 
        delay_func = con_delay(1),
        pi = [pf6_S_STRING_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf6_finished, pf6_outputQ, pf6_hold],
        po_w = [pass_empty_token(), pass_key_outputQ_token(), pass_empty_token() ],
    )

    tf6_44 = Transition(
        id = "f6_44", 
        delay_func = con_delay(3+10),
        pi = [pf6_S_UNPACKED_REP_GETPTR],
        pi_w = [take_1_token()],
        po = [pf6_S_SCALAR_DISPATCH_REQ, pf6_S_STRING_GETPTR],
        po_w = [pass_repeated_array_token(pf6_S_UNPACKED_REP_GETPTR, CstStr.SCALAR), pass_repeated_array_token(pf6_S_UNPACKED_REP_GETPTR, CstStr.NONSCALAR)],
    )

    tf6_memconnect = Transition(
        id = "f6_memconnect", 
        delay_func = mem_read_delay(),
        pi = [pf6_memreadReq],
        pi_w = [take_1_token()],
        po = [pf6_memreadResp],
        po_w = [pass_empty_token()],
        pip = con_delay(1)
    )

    tf6_write_req_out = Transition(
        id = "f6_write_req_out", 
        delay_func = field_end_cond_delay(pf6_outputQ),
        pi = [pf6_outputQ, pwrite_index_holder_f6],
        pi_w = [take_1_token(), take_1_token()],
        po = [pwrites_input_IF_Q, pwrite_hold, pwrite_index_holder_f6],
        po_w = [pass_non_field_end_token(pf6_outputQ, 1), pass_write_hold_cond(pf6_outputQ),  pass_write_index_holder_cond(pf6_outputQ, pwrite_index_holder_f6)],
        )

    return [tdispatch_f6,tf6_25, tf6_26, tf6_28, tf6_30, tf6_31, tf6_36, tf6_37, tf6_40, tf6_44, tf6_memconnect, tf6_write_req_out, tf6_resume, tf6_eom, tf6_dist]
