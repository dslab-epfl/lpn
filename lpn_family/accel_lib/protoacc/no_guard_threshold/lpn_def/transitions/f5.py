from lpnlang import Place, Transition
from lpn_def.funcs.funcs import *
from lpn_def.places.places import *

def f5_ts():

    tdispatch_f5 = Transition(
        id = "dispatch_f5", 
        delay_func = con_delay(1),
        pi = [ptofieldhandler_dispatcher, pdispatch_index_holder_f5, pfields],
        pi_w = [take_1_token(), take_1_token(), take_num_field_tokens(ptofieldhandler_dispatcher)],
        po = [pdispatch_hold, pops_in_f5, pf5_units, pf5_num_units, pfields],
        po_w = [pass_empty_token(), pass_token(ptofieldhandler_dispatcher, 1), pass_field_token(ptofieldhandler_dispatcher, pfields), pass_num_field_token(ptofieldhandler_dispatcher), pass_field_token(ptofieldhandler_dispatcher, pfields)], # return to pfields after fetch
        )

    tf5_resume = Transition(
        id = "f5_resume",
        delay_func = con_delay(0),
        pi = [pf5_num_units, pf5_finished],
        pi_w = [take_1_token(), take_resume_token(pf5_num_units)],
        po = [pf5_S_WAIT_CMD, pf5_outputQ],
        po_w = [pass_empty_token(), pass_field_end_token()],
        )
    

    tf5_dist = Transition(
        id = "f5_dist", 
        delay_func = con_delay(0),
        pi = [pops_in_f5, pf5_dist_hold],
        pi_w = [take_1_token(), take_1_token()],
        po = [pops_in_f5_eom, pops_in_f5_scalar, pops_in_f5_non_scalar, pops_in_f5_repeated],
        po_w = [pass_eom(pops_in_f5), pass_scalar(pops_in_f5), pass_non_scalar(pops_in_f5), pass_repeated(pops_in_f5)],
    )

    tf5_eom = Transition(
        id = "f5_eom", 
        delay_func = con_delay(2),
        pi = [pops_in_f5_eom, pf5_S_WAIT_CMD, pf5_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf5_outputQ, pf5_finished, pf5_dist_hold],
        po_w = [pass_key_outputQ_end_of_toplevel_token(pops_in_f5_eom), pass_empty_token(), pass_empty_token()],
    )

    tf5_25 = Transition(
        id = "f5_25", 
        delay_func = con_delay(1),
        pi = [pops_in_f5_scalar, pf5_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf5_S_SCALAR_DISPATCH_REQ, pf5_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf5_26 = Transition(
        id = "f5_26", 
        delay_func = con_delay(1),
        pi = [pops_in_f5_non_scalar, pf5_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf5_S_STRING_GETPTR, pf5_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf5_28 = Transition(
        id = "f5_28", 
        delay_func = con_delay(1),
        pi = [pops_in_f5_repeated, pf5_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf5_S_UNPACKED_REP_GETPTR, pf5_dist_hold],
        po_w = [pass_token(pops_in_f5_repeated, 1), pass_empty_token()],
    )

    tf5_30 = Transition(
        id = "f5_30", 
        delay_func = con_delay(2+10),
        pi = [pf5_S_SCALAR_DISPATCH_REQ, pf5_hold, pf5_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf5_outputQ, pf5_S_WRITE_KEY],
        po_w = [pass_scalar_outputQ_token(pf5_units), pass_empty_token()],
    )

    tf5_31 = Transition(
        id = "f5_31", 
        delay_func = con_delay(1),
        pi = [pf5_S_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf5_finished, pf5_hold, pf5_outputQ],
        po_w = [pass_empty_token(), pass_empty_token(), pass_key_outputQ_token()],
    )

    tf5_36 = Transition(
        id = "f5_36", 
        delay_func = con_delay(4+2*10),
        pi = [pf5_S_STRING_GETPTR, pf5_hold,  pf5_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf5_S_STRING_LOADDATA],
        po_w = [pass_token(pf5_units, 1)],
    )

    tf5_37 = Transition(
        id = "f5_37", 
        delay_func = all_bytes_delay(pf5_S_STRING_LOADDATA),
        pi = [pf5_S_STRING_LOADDATA],
        pi_w = [take_1_token()],
        po = [pf5_outputQ, pf5_S_STRING_WRITE_KEY],
        po_w = [pass_all_bytes_outputQ_token(pf5_S_STRING_LOADDATA), pass_empty_token()],
    )

    tf5_40 = Transition(
        id = "f5_40", 
        delay_func = con_delay(1),
        pi = [pf5_S_STRING_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf5_finished, pf5_outputQ, pf5_hold],
        po_w = [pass_empty_token(), pass_key_outputQ_token(), pass_empty_token() ],
    )

    tf5_44 = Transition(
        id = "f5_44", 
        delay_func = con_delay(3+10),
        pi = [pf5_S_UNPACKED_REP_GETPTR],
        pi_w = [take_1_token()],
        po = [pf5_S_SCALAR_DISPATCH_REQ, pf5_S_STRING_GETPTR],
        po_w = [pass_repeated_array_token(pf5_S_UNPACKED_REP_GETPTR, CstStr.SCALAR), pass_repeated_array_token(pf5_S_UNPACKED_REP_GETPTR, CstStr.NONSCALAR)],
    )

    tf5_memconnect = Transition(
        id = "f5_memconnect", 
        delay_func = mem_read_delay(),
        pi = [pf5_memreadReq],
        pi_w = [take_1_token()],
        po = [pf5_memreadResp],
        po_w = [pass_empty_token()],
        pip = con_delay(1)
    )

    tf5_write_req_out = Transition(
        id = "f5_write_req_out", 
        delay_func = field_end_cond_delay(pf5_outputQ),
        pi = [pf5_outputQ, pwrite_index_holder_f5],
        pi_w = [take_1_token(), take_1_token()],
        po = [pwrites_input_IF_Q, pwrite_hold, pwrite_index_holder_f5],
        po_w = [pass_non_field_end_token(pf5_outputQ, 1), pass_write_hold_cond(pf5_outputQ),  pass_write_index_holder_cond(pf5_outputQ, pwrite_index_holder_f5)],
        )

    return [tdispatch_f5,tf5_25, tf5_26, tf5_28, tf5_30, tf5_31, tf5_36, tf5_37, tf5_40, tf5_44, tf5_memconnect, tf5_write_req_out, tf5_resume, tf5_eom, tf5_dist]
