from lpnlang import Place, Transition
from lpn_def.funcs.funcs import *
from lpn_def.places.places import *

MemDelay = 10

def common_ts():

    t2 = Transition(
            id = "t2",
            delay_func = con_delay(1), 
            pi=[ps_hasBitsLoader_IsSubmessageLoad, pmessage_tasks], 
            pi_w=[take_1_token(), take_1_token()], 
            po=[ps_hasBitsLoader_HasBitsLoad, pl2helperUser1Req, pcontrol, pcollect],
            po_w=[pass_empty_token(), pass_empty_token(), pass_token(pmessage_tasks, 1), pass_token(pmessage_tasks, 1)],
        )

    tadvance_ok = Transition(
        id = "tadvance_ok", 
        delay_func = con_delay(1),
        pi = [pAdvance_OK],
        pi_w = [take_1_token()],
        po = [ps_hasBitsLoader_IsSubmessageLoad],
        po_w = [pass_empty_token()]
    )

    t1 = Transition(
        id = "t1", 
        delay_func = con_delay(MemDelay),
        pi = [pcontrol],
        pi_w = [take_1_token()],
        po = [pcontrol_prime, pisnot_submessage_value_resp],
        po_w = [pass_token(pcontrol, 1), pass_not_submessage(pcontrol)],
    )

    t3 = Transition(
        id = "t3", 
        delay_func = con_delay(1),
        pi = [pisnot_submessage_value_resp],
        pi_w = [take_1_token()],
        po = [pAdvance_OK],
        po_w = [pass_empty_token()]
    )

    t8 = Transition(
        id = "t8", 
        delay_func = con_delay(0),
        pi = [pcontrol_prime],
        pi_w = [take_1_token()],
        po = [pdescr_request_Q],
        po_w = [pass_token(pcontrol_prime, 1)],
    )

    # t10 = Transition("10", con_delay(2+mem_read_delay()()),

    tsplit_msg = Transition(
        id = "split_msg",
        delay_func = con_delay(0),
        pi = [pdescr_request_Q, pholder_split_msg],
        pi_w = [take_1_token(), take_1_token()],
        po = [p10_descr, p9_descr],
        po_w = [pass_non_message_token(pdescr_request_Q), pass_message_token(pdescr_request_Q)],
    )

    t10 = Transition(
        id = "t10",
        delay_func = con_delay(2),
        pi = [p10_descr, pfields_meta],
        pi_w = [take_1_token(), take_num_field_as_control(p10_descr)],
        po = [ptofieldhandler_dispatcher, pfields_meta, pholder_split_msg],
        po_w = [pass_fields_meta_token(p10_descr, pfields_meta), pass_fields_meta_token(p10_descr, pfields_meta), pass_empty_token()],
    )

    t9 = Transition(
        id = "t9", 
        delay_func = con_delay(MemDelay+2),
        pi = [p9_descr, psWaitForRequest],
        pi_w = [take_1_token(), take_1_token()],
        po = [psWaitForRequest, pAdvance_OK, pholder_split_msg],
        po_w = [pass_empty_token(), pass_empty_token(), pass_empty_token()]
    )

    t5 = Transition(
        id = "t5", 
        delay_func = con_delay(MemDelay),
        pi = [pl2helperUser1Req],
        pi_w = [take_1_token()],
        po = [pl2helperUser1Resp],
        po_w = [pass_empty_token()],
        pip = con_delay(1)
    )

    t7 = Transition(
        id = "t7",
        delay_func = con_delay(MemDelay),
        pi = [pl2helperUser2Req],
        pi_w = [take_1_token()],
        po = [pl2helperUser2Resp],
        po_w = [pass_empty_token()],
        pip = con_delay(1)
    )

    t19 = Transition(
        id = "t19", 
        delay_func = con_delay(1),
        pi = [pwrites_input_IF_Q],
        pi_w = [take_1_token()],
        po = [pwrites_inject_Q],
        po_w = [pass_token(pwrites_input_IF_Q, 1)],
    )
    
    tdist = Transition(
        id = "tinject_write_dist", 
        delay_func = con_delay(0),
        pi = [pwrites_inject_Q, phold],
        pi_w = [take_1_token(), take_1_token()],
        po = [pwrites_inject_Q_non_top, pwrites_inject_Q_top],
        po_w = [pass_non_top_token(pwrites_inject_Q), pass_top_token(pwrites_inject_Q)],
    )

    t23 = Transition(
        id = "t23", 
        delay_func = write_out_delay(pwrites_inject_Q_non_top),
        pi = [pwrites_inject_Q_non_top],
        pi_w = [take_1_token()],
        # pi_guard = [take_non_top_level(pwrites_inject_Q)],
        po = [pwrite_mem_resp, phold],
        po_w = [pass_empty_token(), pass_empty_token()],
    )

    t24 = Transition(
        id = "t24", 
        delay_func = con_delay(4),
        pi = [pwrites_inject_Q_top],
        pi_w = [take_1_token()],
        po = [pwrite_mem_resp, phold],
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
        pi = [pdispatch_index_holder, pdispatch_hold],
        pi_w = [take_1_token(), take_1_token()],
        po = [pdispatch_index_holder, pdispatch_index_holder_f1, pdispatch_index_holder_f2, pdispatch_index_holder_f3, pdispatch_index_holder_f4, pdispatch_index_holder_f5, pdispatch_index_holder_f6],
        po_w = [pass_field_index_add_one(pdispatch_index_holder), pass_field_index_token(pdispatch_index_holder, 1), pass_field_index_token(pdispatch_index_holder, 2),pass_field_index_token(pdispatch_index_holder, 3),pass_field_index_token(pdispatch_index_holder, 4), pass_field_index_token(pdispatch_index_holder, 5),pass_field_index_token(pdispatch_index_holder, 6)],
    )

    twrite_dist = Transition(
        id = "twrite_dist", 
        delay_func = con_delay(0),
        pi = [pwrite_index_holder, pwrite_hold],
        pi_w = [take_1_token(), take_1_token()],
        po = [pwrite_index_holder, pwrite_index_holder_f1, pwrite_index_holder_f2, pwrite_index_holder_f3, pwrite_index_holder_f4, pwrite_index_holder_f5, pwrite_index_holder_f6],
        po_w = [pass_field_index_add_one(pwrite_index_holder), pass_field_index_token(pwrite_index_holder, 1), pass_field_index_token(pwrite_index_holder, 2),pass_field_index_token(pwrite_index_holder, 3),pass_field_index_token(pwrite_index_holder, 4), pass_field_index_token(pwrite_index_holder, 5),pass_field_index_token(pwrite_index_holder, 6)],
    )

    return [t2, tadvance_ok, t1, t3, t5, t7, t8, t10, t9, t19, t23, t24, tdist, tdispatch_dist, twrite_dist, tsplit_msg]
