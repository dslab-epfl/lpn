from lpnlang import Place, Transition
from lpn_def.funcs.funcs import *
from lpn_def.places.places import *

def f2_ts():

    tdispatch_f2 = Transition(
        id = "dispatch_f2", 
        delay_func = con_delay(1),
        pi = [ptofieldhandler_dispatcher, pdispatch_index_holder_f2, pfields],
        pi_w = [take_1_token(), take_1_token(), take_num_field_tokens(ptofieldhandler_dispatcher)],
        po = [pdispatch_hold, pops_in_f2, pf2_units, pf2_num_units, pfields],
        po_w = [pass_empty_token(), pass_token(ptofieldhandler_dispatcher, 1), pass_field_token(ptofieldhandler_dispatcher, pfields), pass_num_field_token(ptofieldhandler_dispatcher), pass_field_token(ptofieldhandler_dispatcher, pfields)], # return to pfields after fetch
        )

    tf2_resume = Transition(
        id = "f2_resume",
        delay_func = con_delay(0),
        pi = [pf2_num_units, pf2_finished],
        pi_w = [take_1_token(), take_resume_token(pf2_num_units)],
        po = [pf2_S_WAIT_CMD, pf2_outputQ],
        po_w = [pass_empty_token(), pass_field_end_token()],
        )
    

    tf2_dist = Transition(
        id = "f2_dist", 
        delay_func = con_delay(0),
        pi = [pops_in_f2, pf2_dist_hold],
        pi_w = [take_1_token(), take_1_token()],
        po = [pops_in_f2_eom, pops_in_f2_scalar, pops_in_f2_non_scalar, pops_in_f2_repeated],
        po_w = [pass_eom(pops_in_f2), pass_scalar(pops_in_f2), pass_non_scalar(pops_in_f2), pass_repeated(pops_in_f2)],
    )

    tf2_eom = Transition(
        id = "f2_eom", 
        delay_func = con_delay(2),
        pi = [pops_in_f2_eom, pf2_S_WAIT_CMD, pf2_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf2_outputQ, pf2_finished, pf2_dist_hold],
        po_w = [pass_key_outputQ_end_of_toplevel_token(pops_in_f2_eom), pass_empty_token(), pass_empty_token()],
    )

    tf2_25 = Transition(
        id = "f2_25", 
        delay_func = con_delay(1),
        pi = [pops_in_f2_scalar, pf2_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf2_S_SCALAR_DISPATCH_REQ, pf2_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf2_26 = Transition(
        id = "f2_26", 
        delay_func = con_delay(1),
        pi = [pops_in_f2_non_scalar, pf2_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf2_S_STRING_GETPTR, pf2_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf2_28 = Transition(
        id = "f2_28", 
        delay_func = con_delay(1),
        pi = [pops_in_f2_repeated, pf2_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf2_S_UNPACKED_REP_GETPTR, pf2_dist_hold],
        po_w = [pass_token(pops_in_f2_repeated, 1), pass_empty_token()],
    )

    tf2_30 = Transition(
        id = "f2_30", 
        delay_func = con_delay(2+10),
        pi = [pf2_S_SCALAR_DISPATCH_REQ, pf2_hold, pf2_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf2_outputQ, pf2_S_WRITE_KEY],
        po_w = [pass_scalar_outputQ_token(pf2_units), pass_empty_token()],
    )

    tf2_31 = Transition(
        id = "f2_31", 
        delay_func = con_delay(1),
        pi = [pf2_S_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf2_finished, pf2_hold, pf2_outputQ],
        po_w = [pass_empty_token(), pass_empty_token(), pass_key_outputQ_token()],
    )

    tf2_36 = Transition(
        id = "f2_36", 
        delay_func = con_delay(4+2*10),
        pi = [pf2_S_STRING_GETPTR, pf2_hold,  pf2_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf2_S_STRING_LOADDATA],
        po_w = [pass_token(pf2_units, 1)],
    )

    tf2_37 = Transition(
        id = "f2_37", 
        delay_func = all_bytes_delay(pf2_S_STRING_LOADDATA),
        pi = [pf2_S_STRING_LOADDATA],
        pi_w = [take_1_token()],
        po = [pf2_outputQ, pf2_S_STRING_WRITE_KEY],
        po_w = [pass_all_bytes_outputQ_token(pf2_S_STRING_LOADDATA), pass_empty_token()],
    )

    tf2_40 = Transition(
        id = "f2_40", 
        delay_func = con_delay(1),
        pi = [pf2_S_STRING_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf2_finished, pf2_outputQ, pf2_hold],
        po_w = [pass_empty_token(), pass_key_outputQ_token(), pass_empty_token() ],
    )

    tf2_44 = Transition(
        id = "f2_44", 
        delay_func = con_delay(3+10),
        pi = [pf2_S_UNPACKED_REP_GETPTR],
        pi_w = [take_1_token()],
        po = [pf2_S_SCALAR_DISPATCH_REQ, pf2_S_STRING_GETPTR],
        po_w = [pass_repeated_array_token(pf2_S_UNPACKED_REP_GETPTR, CstStr.SCALAR), pass_repeated_array_token(pf2_S_UNPACKED_REP_GETPTR, CstStr.NONSCALAR)],
    )

    tf2_memconnect = Transition(
        id = "f2_memconnect", 
        delay_func = mem_read_delay(),
        pi = [pf2_memreadReq],
        pi_w = [take_1_token()],
        po = [pf2_memreadResp],
        po_w = [pass_empty_token()],
        pip = con_delay(1)
    )

    tf2_write_req_out = Transition(
        id = "f2_write_req_out", 
        delay_func = field_end_cond_delay(pf2_outputQ),
        pi = [pf2_outputQ, pwrite_index_holder_f2],
        pi_w = [take_1_token(), take_1_token()],
        po = [pwrites_input_IF_Q, pwrite_hold, pwrite_index_holder_f2],
        po_w = [pass_non_field_end_token(pf2_outputQ, 1), pass_write_hold_cond(pf2_outputQ),  pass_write_index_holder_cond(pf2_outputQ, pwrite_index_holder_f2)],
        )

    return [tdispatch_f2,tf2_25, tf2_26, tf2_28, tf2_30, tf2_31, tf2_36, tf2_37, tf2_40, tf2_44, tf2_memconnect, tf2_write_req_out, tf2_resume, tf2_eom, tf2_dist]
