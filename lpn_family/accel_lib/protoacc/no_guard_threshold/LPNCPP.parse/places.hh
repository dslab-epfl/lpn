
#ifndef __PLACE__
#define __PLACE__
#include "place_transition.hh"
#include "token_types.hh"
extern Place<token_class_bytes> pfields;
extern Place<token_class_type_control_range> pmessage_tasks;
extern Place<> ps_hasBitsLoader_IsSubmessageLoad;
extern Place<> ps_hasBitsLoader_HasBitsLoad;
extern Place<token_class_bytes_end_of_field_end_of_top_level> pwrites_input_IF_Q;
extern Place<token_class_field_index> pdispatch_index_holder_f1;
extern Place<> pl2helperUser1Req;
extern Place<token_class_bytes_end_of_field_end_of_top_level> pwrites_inject_Q;
extern Place<> pf1_S_WAIT_CMD;
extern Place<> pl2helperUser1Resp;
extern Place<> pf1_S_SCALAR_DISPATCH_REQ;
extern Place<> pf1_S_STRING_GETPTR;
extern Place<> pwrite_mem_resp;
extern Place<token_class_bytes_end_of_field_end_of_top_level> pwrites_inject_Q_non_top;
extern Place<> pwrite_hold;
extern Place<token_class_field_index> pwrite_index_holder;
extern Place<token_class_field_index> pwrite_index_holder_f1;
extern Place<> pisnot_submessage_value_resp;
extern Place<token_class_bytes> pf1_S_STRING_LOADDATA;
extern Place<token_class_bytes_end_of_field_end_of_top_level> pwrites_inject_Q_top;
extern Place<token_class_type_num> pops_in_f1;
extern Place<> pAdvance_OK;
extern Place<> phold;
extern Place<> pf1_S_STRING_WRITE_KEY;
extern Place<token_class_type_control_range> pdescr_request_Q;
extern Place<> pf1_dist_hold;
extern Place<token_class_type_num> pf1_S_UNPACKED_REP_GETPTR;
extern Place<> psWaitForRequest;
extern Place<token_class_type_num> pops_in_f1_eom;
extern Place<token_class_type_num> pops_in_f1_scalar;
extern Place<token_class_type_control_range> p10_descr;
extern Place<token_class_type_num> pops_in_f1_non_scalar;
extern Place<> pholder_split_msg;
extern Place<token_class_type_num> pops_in_f1_repeated;
extern Place<token_class_type_control_range> p9_descr;
extern Place<> pf1_S_WRITE_KEY;
extern Place<token_class_bytes_end_of_field_end_of_top_level> pf1_outputQ;
extern Place<> pl2helperUser2Req;
extern Place<> pf1_finished;
extern Place<> pl2helperUser2Resp;
extern Place<token_class_num> pf1_num_units;
extern Place<token_class_bytes> pf1_units;
extern Place<token_class_type_num> ptofieldhandler_dispatcher;
extern Place<> pf1_hold;
extern Place<token_class_type_control_range> pcollect;
extern Place<token_class_field_index> pdispatch_index_holder;
extern Place<> pdispatch_hold;
extern Place<token_class_type_num> pfields_meta;
extern Place<token_class_type_control_range> pcontrol_prime;
extern Place<> pf1_memreadReq;
extern Place<token_class_type_control_range> pcontrol;
extern Place<> pf1_memreadResp;
#endif