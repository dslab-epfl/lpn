#ifndef __TRANSITIONS__
#define __TRANSITIONS__
#include <stdlib.h>
#include <functional>
#include "place_transition.hh"
#include "places.hh"
#include "lpn_funcs.hh"
Transition t2 = {
    .id = "t2",
    .delay_f = con_delay(1),
    .p_input = {&ps_hasBitsLoader_IsSubmessageLoad,&pmessage_tasks},
    .p_output = {&ps_hasBitsLoader_HasBitsLoad,&pl2helperUser1Req,&pcontrol,&pcollect},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_empty_token(),pass_empty_token(),pass_token(&pmessage_tasks, 1),pass_token(&pmessage_tasks, 1)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition tadvance_ok = {
    .id = "tadvance_ok",
    .delay_f = con_delay(1),
    .p_input = {&pAdvance_OK},
    .p_output = {&ps_hasBitsLoader_IsSubmessageLoad},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token()},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition t1 = {
    .id = "t1",
    .delay_f = con_delay(10),
    .p_input = {&pcontrol},
    .p_output = {&pcontrol_prime,&pisnot_submessage_value_resp},  
    .pi_w = {take_1_token()},
    .po_w = {pass_token(&pcontrol, 1),pass_not_submessage(&pcontrol)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition t3 = {
    .id = "t3",
    .delay_f = con_delay(1),
    .p_input = {&pisnot_submessage_value_resp},
    .p_output = {&pAdvance_OK},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token()},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition t5 = {
    .id = "t5",
    .delay_f = con_delay(10),
    .p_input = {&pl2helperUser1Req},
    .p_output = {&pl2helperUser1Resp},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token()},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = con_delay(1)
};
Transition t7 = {
    .id = "t7",
    .delay_f = con_delay(10),
    .p_input = {&pl2helperUser2Req},
    .p_output = {&pl2helperUser2Resp},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token()},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = con_delay(1)
};
Transition t8 = {
    .id = "t8",
    .delay_f = con_delay(0),
    .p_input = {&pcontrol_prime},
    .p_output = {&pdescr_request_Q},  
    .pi_w = {take_1_token()},
    .po_w = {pass_token(&pcontrol_prime, 1)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition t10 = {
    .id = "t10",
    .delay_f = con_delay(2),
    .p_input = {&p10_descr,&pfields_meta},
    .p_output = {&ptofieldhandler_dispatcher,&pfields_meta,&pholder_split_msg},  
    .pi_w = {take_1_token(),take_num_field_as_control(&p10_descr)},
    .po_w = {pass_fields_meta_token(&p10_descr, &pfields_meta),pass_fields_meta_token(&p10_descr, &pfields_meta),pass_empty_token()},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition t9 = {
    .id = "t9",
    .delay_f = con_delay(12),
    .p_input = {&p9_descr,&psWaitForRequest},
    .p_output = {&psWaitForRequest,&pAdvance_OK,&pholder_split_msg},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_empty_token(),pass_empty_token(),pass_empty_token()},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition t19 = {
    .id = "t19",
    .delay_f = con_delay(1),
    .p_input = {&pwrites_input_IF_Q},
    .p_output = {&pwrites_inject_Q},  
    .pi_w = {take_1_token()},
    .po_w = {pass_token(&pwrites_input_IF_Q, 1)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition t23 = {
    .id = "t23",
    .delay_f = write_out_delay(&pwrites_inject_Q_non_top),
    .p_input = {&pwrites_inject_Q_non_top},
    .p_output = {&pwrite_mem_resp,&phold},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(),pass_empty_token()},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition t24 = {
    .id = "t24",
    .delay_f = con_delay(4),
    .p_input = {&pwrites_inject_Q_top},
    .p_output = {&pwrite_mem_resp,&phold},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(),pass_empty_token()},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition tinject_write_dist = {
    .id = "tinject_write_dist",
    .delay_f = con_delay(0),
    .p_input = {&pwrites_inject_Q,&phold},
    .p_output = {&pwrites_inject_Q_non_top,&pwrites_inject_Q_top},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_non_top_token(&pwrites_inject_Q),pass_top_token(&pwrites_inject_Q)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition tdispatch_dist = {
    .id = "tdispatch_dist",
    .delay_f = con_delay(0),
    .p_input = {&pdispatch_index_holder,&pdispatch_hold},
    .p_output = {&pdispatch_index_holder,&pdispatch_index_holder_f1},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_field_index_add_one(&pdispatch_index_holder),pass_field_index_token(&pdispatch_index_holder, 1)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition twrite_dist = {
    .id = "twrite_dist",
    .delay_f = con_delay(0),
    .p_input = {&pwrite_index_holder,&pwrite_hold},
    .p_output = {&pwrite_index_holder,&pwrite_index_holder_f1},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_field_index_add_one(&pwrite_index_holder),pass_field_index_token(&pwrite_index_holder, 1)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition split_msg = {
    .id = "split_msg",
    .delay_f = con_delay(0),
    .p_input = {&pdescr_request_Q,&pholder_split_msg},
    .p_output = {&p10_descr,&p9_descr},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_non_message_token(&pdescr_request_Q),pass_message_token(&pdescr_request_Q)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition dispatch_f1 = {
    .id = "dispatch_f1",
    .delay_f = con_delay(1),
    .p_input = {&ptofieldhandler_dispatcher,&pdispatch_index_holder_f1,&pfields},
    .p_output = {&pdispatch_hold,&pops_in_f1,&pf1_units,&pf1_num_units,&pfields},  
    .pi_w = {take_1_token(),take_1_token(),take_num_field_tokens(&ptofieldhandler_dispatcher)},
    .po_w = {pass_empty_token(),pass_token(&ptofieldhandler_dispatcher, 1),pass_field_token(&ptofieldhandler_dispatcher, &pfields),pass_num_field_token(&ptofieldhandler_dispatcher),pass_field_token(&ptofieldhandler_dispatcher, &pfields)},
    .pi_w_threshold = {NULL, NULL, NULL},
    .pi_guard = {NULL, NULL, NULL},
    .pip = NULL
};
Transition f1_25 = {
    .id = "f1_25",
    .delay_f = con_delay(1),
    .p_input = {&pops_in_f1_scalar,&pf1_S_WAIT_CMD},
    .p_output = {&pf1_S_SCALAR_DISPATCH_REQ,&pf1_dist_hold},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_empty_token(),pass_empty_token()},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition f1_26 = {
    .id = "f1_26",
    .delay_f = con_delay(1),
    .p_input = {&pops_in_f1_non_scalar,&pf1_S_WAIT_CMD},
    .p_output = {&pf1_S_STRING_GETPTR,&pf1_dist_hold},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_empty_token(),pass_empty_token()},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition f1_28 = {
    .id = "f1_28",
    .delay_f = con_delay(1),
    .p_input = {&pops_in_f1_repeated,&pf1_S_WAIT_CMD},
    .p_output = {&pf1_S_UNPACKED_REP_GETPTR,&pf1_dist_hold},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_token(&pops_in_f1_repeated, 1),pass_empty_token()},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition f1_30 = {
    .id = "f1_30",
    .delay_f = con_delay(12),
    .p_input = {&pf1_S_SCALAR_DISPATCH_REQ,&pf1_hold,&pf1_units},
    .p_output = {&pf1_outputQ,&pf1_S_WRITE_KEY},  
    .pi_w = {take_1_token(),take_1_token(),take_1_token()},
    .po_w = {pass_scalar_outputQ_token(&pf1_units),pass_empty_token()},
    .pi_w_threshold = {NULL, NULL, NULL},
    .pi_guard = {NULL, NULL, NULL},
    .pip = NULL
};
Transition f1_31 = {
    .id = "f1_31",
    .delay_f = con_delay(1),
    .p_input = {&pf1_S_WRITE_KEY},
    .p_output = {&pf1_finished,&pf1_hold,&pf1_outputQ},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(),pass_empty_token(),pass_key_outputQ_token()},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition f1_36 = {
    .id = "f1_36",
    .delay_f = con_delay(24),
    .p_input = {&pf1_S_STRING_GETPTR,&pf1_hold,&pf1_units},
    .p_output = {&pf1_S_STRING_LOADDATA},  
    .pi_w = {take_1_token(),take_1_token(),take_1_token()},
    .po_w = {pass_token(&pf1_units, 1)},
    .pi_w_threshold = {NULL, NULL, NULL},
    .pi_guard = {NULL, NULL, NULL},
    .pip = NULL
};
Transition f1_37 = {
    .id = "f1_37",
    .delay_f = all_bytes_delay(&pf1_S_STRING_LOADDATA),
    .p_input = {&pf1_S_STRING_LOADDATA},
    .p_output = {&pf1_outputQ,&pf1_S_STRING_WRITE_KEY},  
    .pi_w = {take_1_token()},
    .po_w = {pass_all_bytes_outputQ_token(&pf1_S_STRING_LOADDATA),pass_empty_token()},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition f1_40 = {
    .id = "f1_40",
    .delay_f = con_delay(1),
    .p_input = {&pf1_S_STRING_WRITE_KEY},
    .p_output = {&pf1_finished,&pf1_outputQ,&pf1_hold},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(),pass_key_outputQ_token(),pass_empty_token()},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition f1_44 = {
    .id = "f1_44",
    .delay_f = con_delay(13),
    .p_input = {&pf1_S_UNPACKED_REP_GETPTR},
    .p_output = {&pf1_S_SCALAR_DISPATCH_REQ,&pf1_S_STRING_GETPTR},  
    .pi_w = {take_1_token()},
    .po_w = {pass_repeated_array_token(&pf1_S_UNPACKED_REP_GETPTR, (int)CstStr::SCALAR),pass_repeated_array_token(&pf1_S_UNPACKED_REP_GETPTR, (int)CstStr::NONSCALAR)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition f1_memconnect = {
    .id = "f1_memconnect",
    .delay_f = mem_read_delay(),
    .p_input = {&pf1_memreadReq},
    .p_output = {&pf1_memreadResp},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token()},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = con_delay(1)
};
Transition f1_write_req_out = {
    .id = "f1_write_req_out",
    .delay_f = field_end_cond_delay(&pf1_outputQ),
    .p_input = {&pf1_outputQ,&pwrite_index_holder_f1},
    .p_output = {&pwrites_input_IF_Q,&pwrite_hold,&pwrite_index_holder_f1},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_non_field_end_token(&pf1_outputQ, 1),pass_write_hold_cond(&pf1_outputQ),pass_write_index_holder_cond(&pf1_outputQ, &pwrite_index_holder_f1)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition f1_resume = {
    .id = "f1_resume",
    .delay_f = con_delay(0),
    .p_input = {&pf1_num_units,&pf1_finished},
    .p_output = {&pf1_S_WAIT_CMD,&pf1_outputQ},  
    .pi_w = {take_1_token(),take_resume_token(&pf1_num_units)},
    .po_w = {pass_empty_token(),pass_field_end_token()},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition f1_eom = {
    .id = "f1_eom",
    .delay_f = con_delay(2),
    .p_input = {&pops_in_f1_eom,&pf1_S_WAIT_CMD,&pf1_units},
    .p_output = {&pf1_outputQ,&pf1_finished,&pf1_dist_hold},  
    .pi_w = {take_1_token(),take_1_token(),take_1_token()},
    .po_w = {pass_key_outputQ_end_of_toplevel_token(&pops_in_f1_eom),pass_empty_token(),pass_empty_token()},
    .pi_w_threshold = {NULL, NULL, NULL},
    .pi_guard = {NULL, NULL, NULL},
    .pip = NULL
};
Transition f1_dist = {
    .id = "f1_dist",
    .delay_f = con_delay(0),
    .p_input = {&pops_in_f1,&pf1_dist_hold},
    .p_output = {&pops_in_f1_eom,&pops_in_f1_scalar,&pops_in_f1_non_scalar,&pops_in_f1_repeated},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_eom(&pops_in_f1),pass_scalar(&pops_in_f1),pass_non_scalar(&pops_in_f1),pass_repeated(&pops_in_f1)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
#endif