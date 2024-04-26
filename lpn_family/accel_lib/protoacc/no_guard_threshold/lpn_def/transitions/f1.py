from lpnlang import Place, Transition
from lpn_def.funcs.funcs import *
from lpn_def.places.places import *

def f1_ts():

    tdispatch_f1 = Transition(
        id = "dispatch_f1", 
        delay_func = con_delay(1),
        pi = [ptofieldhandler_dispatcher, pdispatch_index_holder_f1, pfields],
        pi_w = [take_1_token(), take_1_token(), take_num_field_tokens(ptofieldhandler_dispatcher)],
        po = [pdispatch_hold, pops_in_f1, pf1_units, pf1_num_units, pfields],
        po_w = [pass_empty_token(), pass_token(ptofieldhandler_dispatcher, 1), pass_field_token(ptofieldhandler_dispatcher, pfields), pass_num_field_token(ptofieldhandler_dispatcher), pass_field_token(ptofieldhandler_dispatcher, pfields)], # return to pfields after fetch
        )

    tf1_resume = Transition(
        id = "f1_resume",
        delay_func = con_delay(0),
        pi = [pf1_num_units, pf1_finished],
        pi_w = [take_1_token(), take_resume_token(pf1_num_units)],
        po = [pf1_S_WAIT_CMD, pf1_outputQ],
        po_w = [pass_empty_token(), pass_field_end_token()],
        )
    

    tf1_dist = Transition(
        id = "f1_dist", 
        delay_func = con_delay(0),
        pi = [pops_in_f1, pf1_dist_hold],
        pi_w = [take_1_token(), take_1_token()],
        po = [pops_in_f1_eom, pops_in_f1_scalar, pops_in_f1_non_scalar, pops_in_f1_repeated],
        po_w = [pass_eom(pops_in_f1), pass_scalar(pops_in_f1), pass_non_scalar(pops_in_f1), pass_repeated(pops_in_f1)],
    )

    tf1_eom = Transition(
        id = "f1_eom", 
        delay_func = con_delay(2),
        pi = [pops_in_f1_eom, pf1_S_WAIT_CMD, pf1_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf1_outputQ, pf1_finished, pf1_dist_hold],
        po_w = [pass_key_outputQ_end_of_toplevel_token(pops_in_f1_eom), pass_empty_token(), pass_empty_token()],
    )

    tf1_25 = Transition(
        id = "f1_25", 
        delay_func = con_delay(1),
        pi = [pops_in_f1_scalar, pf1_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf1_S_SCALAR_DISPATCH_REQ, pf1_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf1_26 = Transition(
        id = "f1_26", 
        delay_func = con_delay(1),
        pi = [pops_in_f1_non_scalar, pf1_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf1_S_STRING_GETPTR, pf1_dist_hold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    tf1_28 = Transition(
        id = "f1_28", 
        delay_func = con_delay(1),
        pi = [pops_in_f1_repeated, pf1_S_WAIT_CMD],
        pi_w = [take_1_token(), take_1_token()],
        po = [pf1_S_UNPACKED_REP_GETPTR, pf1_dist_hold],
        po_w = [pass_token(pops_in_f1_repeated, 1), pass_empty_token()],
    )

    tf1_30 = Transition(
        id = "f1_30", 
        delay_func = con_delay(2+10),
        pi = [pf1_S_SCALAR_DISPATCH_REQ, pf1_hold, pf1_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf1_outputQ, pf1_S_WRITE_KEY],
        po_w = [pass_scalar_outputQ_token(pf1_units), pass_empty_token()],
    )

    tf1_31 = Transition(
        id = "f1_31", 
        delay_func = con_delay(1),
        pi = [pf1_S_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf1_finished, pf1_hold, pf1_outputQ],
        po_w = [pass_empty_token(), pass_empty_token(), pass_key_outputQ_token()],
    )

    tf1_36 = Transition(
        id = "f1_36", 
        delay_func = con_delay(4+2*10),
        pi = [pf1_S_STRING_GETPTR, pf1_hold,  pf1_units],
        pi_w = [take_1_token(), take_1_token(), take_1_token()],
        po = [pf1_S_STRING_LOADDATA],
        po_w = [pass_token(pf1_units, 1)],
    )

    tf1_37 = Transition(
        id = "f1_37", 
        delay_func = all_bytes_delay(pf1_S_STRING_LOADDATA),
        pi = [pf1_S_STRING_LOADDATA],
        pi_w = [take_1_token()],
        po = [pf1_outputQ, pf1_S_STRING_WRITE_KEY],
        po_w = [pass_all_bytes_outputQ_token(pf1_S_STRING_LOADDATA), pass_empty_token()],
    )

    tf1_40 = Transition(
        id = "f1_40", 
        delay_func = con_delay(1),
        pi = [pf1_S_STRING_WRITE_KEY],
        pi_w = [take_1_token()],
        po = [pf1_finished, pf1_outputQ, pf1_hold],
        po_w = [pass_empty_token(), pass_key_outputQ_token(), pass_empty_token() ],
    )

    tf1_44 = Transition(
        id = "f1_44", 
        delay_func = con_delay(3+10),
        pi = [pf1_S_UNPACKED_REP_GETPTR],
        pi_w = [take_1_token()],
        po = [pf1_S_SCALAR_DISPATCH_REQ, pf1_S_STRING_GETPTR],
        po_w = [pass_repeated_array_token(pf1_S_UNPACKED_REP_GETPTR, CstStr.SCALAR), pass_repeated_array_token(pf1_S_UNPACKED_REP_GETPTR, CstStr.NONSCALAR)],
    )

    tf1_memconnect = Transition(
        id = "f1_memconnect", 
        delay_func = mem_read_delay(),
        pi = [pf1_memreadReq],
        pi_w = [take_1_token()],
        po = [pf1_memreadResp],
        po_w = [pass_empty_token()],
        pip = con_delay(1)
    )

    tf1_write_req_out = Transition(
        id = "f1_write_req_out", 
        delay_func = field_end_cond_delay(pf1_outputQ),
        pi = [pf1_outputQ, pwrite_index_holder_f1],
        pi_w = [take_1_token(), take_1_token()],
        po = [pwrites_input_IF_Q, pwrite_hold, pwrite_index_holder_f1],
        po_w = [pass_non_field_end_token(pf1_outputQ, 1), pass_write_hold_cond(pf1_outputQ),  pass_write_index_holder_cond(pf1_outputQ, pwrite_index_holder_f1)],
        )

    return [tdispatch_f1,tf1_25, tf1_26, tf1_28, tf1_30, tf1_31, tf1_36, tf1_37, tf1_40, tf1_44, tf1_memconnect, tf1_write_req_out, tf1_resume, tf1_eom, tf1_dist]
