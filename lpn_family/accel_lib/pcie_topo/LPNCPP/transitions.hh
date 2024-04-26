#ifndef __TRANSITIONS__
#define __TRANSITIONS__
#include <stdlib.h>
#include <functional>
#include "place_transition.hh"
#include "places.hh"
#include "lpn_funcs.hh"
std::vector<Place<token_class_drcf>*> list_0 = {&root_tmpbuf_2_0};
std::vector<Place<token_class_drcf>*> list_1 = {&root_tmpbuf_2_0};
std::vector<Place<token_class_drcf>*> list_2 = {&root_tmpbuf_2_0};
std::vector<int> list_3 = {2};
std::vector<Place<token_class_drcf>*> list_4 = {&root_tmpbuf_0_2};
std::vector<Place<token_class_drcf>*> list_5 = {&root_tmpbuf_0_2};
std::vector<Place<token_class_drcf>*> list_6 = {&root_tmpbuf_0_2};
std::vector<int> list_7 = {0};
std::vector<Place<token_class_drcf>*> list_8 = {&s1_tmpbuf_5_0, &s1_tmpbuf_6_0};
std::vector<Place<token_class_drcf>*> list_9 = {&s1_tmpbuf_5_0, &s1_tmpbuf_6_0};
std::vector<Place<token_class_drcf>*> list_10 = {&s1_tmpbuf_5_0, &s1_tmpbuf_6_0};
std::vector<Place<token_class_drcf>*> list_11 = {&s1_tmpbuf_5_0, &s1_tmpbuf_6_0};
std::vector<int> list_12 = {5, 6};
std::vector<Place<token_class_drcf>*> list_13 = {&s1_tmpbuf_0_5, &s1_tmpbuf_6_5};
std::vector<Place<token_class_drcf>*> list_14 = {&s1_tmpbuf_0_5, &s1_tmpbuf_6_5};
std::vector<Place<token_class_drcf>*> list_15 = {&s1_tmpbuf_0_5, &s1_tmpbuf_6_5};
std::vector<Place<token_class_drcf>*> list_16 = {&s1_tmpbuf_0_5, &s1_tmpbuf_6_5};
std::vector<int> list_17 = {0, 6};
std::vector<Place<token_class_drcf>*> list_18 = {&s1_tmpbuf_0_6, &s1_tmpbuf_5_6};
std::vector<Place<token_class_drcf>*> list_19 = {&s1_tmpbuf_0_6, &s1_tmpbuf_5_6};
std::vector<Place<token_class_drcf>*> list_20 = {&s1_tmpbuf_0_6, &s1_tmpbuf_5_6};
std::vector<Place<token_class_drcf>*> list_21 = {&s1_tmpbuf_0_6, &s1_tmpbuf_5_6};
std::vector<int> list_22 = {0, 5};
std::vector<Place<token_class_drcf>*> list_23 = {&d1_reqbuf_nonpost, &d1_reqbuf_post, &d1_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_24 = {&d1_reqbuf_nonpost, &d1_reqbuf_post, &d1_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_25 = {&d1_reqbuf_nonpost, &d1_reqbuf_post, &d1_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_26 = {&d1_reqbuf_nonpost, &d1_reqbuf_post, &d1_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_27 = {&d1_reqbuf_nonpost, &d1_reqbuf_post, &d1_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_28 = {&d1_reqbuf_nonpost, &d1_reqbuf_post, &d1_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_29 = {&d1_reqbuf_nonpost, &d1_reqbuf_post, &d1_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_30 = {&d1_reqbuf_nonpost, &d1_reqbuf_post, &d1_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_31 = {&d2_reqbuf_nonpost, &d2_reqbuf_post, &d2_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_32 = {&d2_reqbuf_nonpost, &d2_reqbuf_post, &d2_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_33 = {&d2_reqbuf_nonpost, &d2_reqbuf_post, &d2_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_34 = {&d2_reqbuf_nonpost, &d2_reqbuf_post, &d2_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_35 = {&d2_reqbuf_nonpost, &d2_reqbuf_post, &d2_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_36 = {&d2_reqbuf_nonpost, &d2_reqbuf_post, &d2_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_37 = {&d2_reqbuf_nonpost, &d2_reqbuf_post, &d2_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_38 = {&d2_reqbuf_nonpost, &d2_reqbuf_post, &d2_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_39 = {&d3_reqbuf_nonpost, &d3_reqbuf_post, &d3_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_40 = {&d3_reqbuf_nonpost, &d3_reqbuf_post, &d3_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_41 = {&d3_reqbuf_nonpost, &d3_reqbuf_post, &d3_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_42 = {&d3_reqbuf_nonpost, &d3_reqbuf_post, &d3_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_43 = {&d3_reqbuf_nonpost, &d3_reqbuf_post, &d3_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_44 = {&d3_reqbuf_nonpost, &d3_reqbuf_post, &d3_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_45 = {&d3_reqbuf_nonpost, &d3_reqbuf_post, &d3_reqbuf_cmpl};
std::vector<Place<token_class_drcf>*> list_46 = {&d3_reqbuf_nonpost, &d3_reqbuf_post, &d3_reqbuf_cmpl};
std::map<int, int> dict_0 = {
{1, 2}, 
{2, 0}, 
{3, 2}, 
};
std::map<int, int> dict_1 = {
{1, 2}, 
{2, 0}, 
{3, 2}, 
};
std::map<int, int> dict_2 = {
{1, 5}, 
{2, 0}, 
{3, 6}, 
};
std::map<int, int> dict_3 = {
{1, 5}, 
{2, 0}, 
{3, 6}, 
};
std::map<int, int> dict_4 = {
{1, 5}, 
{2, 0}, 
{3, 6}, 
};
std::map<int, int> dict_5 = {
{1, 5}, 
{2, 0}, 
{3, 6}, 
};
std::map<int, int> dict_6 = {
{1, 5}, 
{2, 0}, 
{3, 6}, 
};
std::map<int, int> dict_7 = {
{1, 5}, 
{2, 0}, 
{3, 6}, 
};
Transition troot_tmpbuf_0_2 = {
    .id = "troot_tmpbuf_0_2",
    .delay_f = con_delay(1),
    .p_input = {&root_recv_0,&s1_recvcap_0},
    .p_output = {&root_tmpbuf_0_2},  
    .pi_w = {con_edge(1),take_some_token(0)},
    .po_w = {pass_atomic_smaller_token(256, &root_recv_0)},
    .pi_w_threshold = {empty_threshold(), take_credit_token(&root_recv_0, 16)},
    .pi_guard = {take_out_port(&root_recv_0, dict_0, 2), empty_guard()},
    .pip = NULL
};
Transition troot_tmpbuf_2_0 = {
    .id = "troot_tmpbuf_2_0",
    .delay_f = con_delay(1),
    .p_input = {&root_recv_2,&d2_recvcap},
    .p_output = {&root_tmpbuf_2_0},  
    .pi_w = {con_edge(1),take_some_token(0)},
    .po_w = {pass_atomic_smaller_token(256, &root_recv_2)},
    .pi_w_threshold = {empty_threshold(), take_credit_token(&root_recv_2, 16)},
    .pi_guard = {take_out_port(&root_recv_2, dict_1, 0), empty_guard()},
    .pip = NULL
};
Transition root_tmpbuf_to_sendbuf_0_arbiter = {
    .id = "root_tmpbuf_to_sendbuf_0_arbiter",
    .delay_f = con_delay(0),
    .p_input = {&root_tmpbuf_to_sendbuf_0_pidx,&root_tmpbuf_2_0},
    .p_output = {&root_tmpbuf_to_sendbuf_0_pidx,&root_sendbuf_0},  
    .pi_w = {take_1_token(),arbiterhelper_take_0_or_1(0, list_0, &root_tmpbuf_to_sendbuf_0_pidx)},
    .po_w = {arbiterhelper_update_cur_turn(&root_tmpbuf_to_sendbuf_0_pidx, list_1),arbiterhelpernocapwport_pass_turn_token(&root_tmpbuf_to_sendbuf_0_pidx, list_2, list_3)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition root_send_0 = {
    .id = "root_send_0",
    .delay_f = var_tlp_process_delay(&root_sendbuf_0, 7),
    .p_input = {&root_sendbuf_0,&d2_recvcap},
    .p_output = {&root_recvcap_2,&root_P2P_d2_linkbuf,&root_P2P_d2_tlp},  
    .pi_w = {take_1_token(),take_credit_token(&root_sendbuf_0, 16)},
    .po_w = {increase_credit(&root_sendbuf_0, 2, 16),pass_credit_with_header_token(&root_sendbuf_0, 30, 16),pass_add_header_token(&root_sendbuf_0, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition root_tmpbuf_to_sendbuf_2_arbiter = {
    .id = "root_tmpbuf_to_sendbuf_2_arbiter",
    .delay_f = con_delay(0),
    .p_input = {&root_tmpbuf_to_sendbuf_2_pidx,&root_tmpbuf_0_2},
    .p_output = {&root_tmpbuf_to_sendbuf_2_pidx,&root_sendbuf_2},  
    .pi_w = {take_1_token(),arbiterhelper_take_0_or_1(0, list_4, &root_tmpbuf_to_sendbuf_2_pidx)},
    .po_w = {arbiterhelper_update_cur_turn(&root_tmpbuf_to_sendbuf_2_pidx, list_5),arbiterhelpernocapwport_pass_turn_token(&root_tmpbuf_to_sendbuf_2_pidx, list_6, list_7)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition root_send_2 = {
    .id = "root_send_2",
    .delay_f = var_tlp_process_delay(&root_sendbuf_2, 7),
    .p_input = {&root_sendbuf_2,&s1_recvcap_0},
    .p_output = {&root_recvcap_0,&root_P2P_s1_linkbuf,&root_P2P_s1_tlp},  
    .pi_w = {take_1_token(),take_credit_token(&root_sendbuf_2, 16)},
    .po_w = {increase_credit(&root_sendbuf_2, 0, 16),pass_credit_with_header_token(&root_sendbuf_2, 30, 16),pass_add_header_token(&root_sendbuf_2, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition ts1_tmpbuf_0_5 = {
    .id = "ts1_tmpbuf_0_5",
    .delay_f = con_delay(1),
    .p_input = {&s1_recv_0,&d1_recvcap},
    .p_output = {&s1_tmpbuf_0_5},  
    .pi_w = {con_edge(1),take_some_token(0)},
    .po_w = {pass_token(&s1_recv_0, 1)},
    .pi_w_threshold = {empty_threshold(), take_credit_token(&s1_recv_0, 16)},
    .pi_guard = {take_out_port(&s1_recv_0, dict_2, 5), empty_guard()},
    .pip = NULL
};
Transition ts1_tmpbuf_0_6 = {
    .id = "ts1_tmpbuf_0_6",
    .delay_f = con_delay(1),
    .p_input = {&s1_recv_0,&d3_recvcap},
    .p_output = {&s1_tmpbuf_0_6},  
    .pi_w = {con_edge(1),take_some_token(0)},
    .po_w = {pass_token(&s1_recv_0, 1)},
    .pi_w_threshold = {empty_threshold(), take_credit_token(&s1_recv_0, 16)},
    .pi_guard = {take_out_port(&s1_recv_0, dict_3, 6), empty_guard()},
    .pip = NULL
};
Transition ts1_tmpbuf_5_0 = {
    .id = "ts1_tmpbuf_5_0",
    .delay_f = con_delay(1),
    .p_input = {&s1_recv_5,&root_recvcap_2},
    .p_output = {&s1_tmpbuf_5_0},  
    .pi_w = {con_edge(1),take_some_token(0)},
    .po_w = {pass_token(&s1_recv_5, 1)},
    .pi_w_threshold = {empty_threshold(), take_credit_token(&s1_recv_5, 16)},
    .pi_guard = {take_out_port(&s1_recv_5, dict_4, 0), empty_guard()},
    .pip = NULL
};
Transition ts1_tmpbuf_5_6 = {
    .id = "ts1_tmpbuf_5_6",
    .delay_f = con_delay(1),
    .p_input = {&s1_recv_5,&d3_recvcap},
    .p_output = {&s1_tmpbuf_5_6},  
    .pi_w = {con_edge(1),take_some_token(0)},
    .po_w = {pass_token(&s1_recv_5, 1)},
    .pi_w_threshold = {empty_threshold(), take_credit_token(&s1_recv_5, 16)},
    .pi_guard = {take_out_port(&s1_recv_5, dict_5, 6), empty_guard()},
    .pip = NULL
};
Transition ts1_tmpbuf_6_0 = {
    .id = "ts1_tmpbuf_6_0",
    .delay_f = con_delay(1),
    .p_input = {&s1_recv_6,&root_recvcap_2},
    .p_output = {&s1_tmpbuf_6_0},  
    .pi_w = {con_edge(1),take_some_token(0)},
    .po_w = {pass_token(&s1_recv_6, 1)},
    .pi_w_threshold = {empty_threshold(), take_credit_token(&s1_recv_6, 16)},
    .pi_guard = {take_out_port(&s1_recv_6, dict_6, 0), empty_guard()},
    .pip = NULL
};
Transition ts1_tmpbuf_6_5 = {
    .id = "ts1_tmpbuf_6_5",
    .delay_f = con_delay(1),
    .p_input = {&s1_recv_6,&d1_recvcap},
    .p_output = {&s1_tmpbuf_6_5},  
    .pi_w = {con_edge(1),take_some_token(0)},
    .po_w = {pass_token(&s1_recv_6, 1)},
    .pi_w_threshold = {empty_threshold(), take_credit_token(&s1_recv_6, 16)},
    .pi_guard = {take_out_port(&s1_recv_6, dict_7, 5), empty_guard()},
    .pip = NULL
};
Transition s1_tmpbuf_to_sendbuf_0_arbiter = {
    .id = "s1_tmpbuf_to_sendbuf_0_arbiter",
    .delay_f = con_delay(0),
    .p_input = {&s1_tmpbuf_to_sendbuf_0_pidx,&s1_tmpbuf_5_0,&s1_tmpbuf_6_0},
    .p_output = {&s1_tmpbuf_to_sendbuf_0_pidx,&s1_sendbuf_0},  
    .pi_w = {take_1_token(),arbiterhelper_take_0_or_1(0, list_8, &s1_tmpbuf_to_sendbuf_0_pidx),arbiterhelper_take_0_or_1(1, list_9, &s1_tmpbuf_to_sendbuf_0_pidx)},
    .po_w = {arbiterhelper_update_cur_turn(&s1_tmpbuf_to_sendbuf_0_pidx, list_10),arbiterhelpernocapwport_pass_turn_token(&s1_tmpbuf_to_sendbuf_0_pidx, list_11, list_12)},
    .pi_w_threshold = {NULL, NULL, NULL},
    .pi_guard = {NULL, NULL, NULL},
    .pip = NULL
};
Transition s1_send_0 = {
    .id = "s1_send_0",
    .delay_f = var_tlp_process_delay(&s1_sendbuf_0, 7),
    .p_input = {&s1_sendbuf_0,&root_recvcap_2},
    .p_output = {&s1_recvcap_5,&s1_recvcap_6,&s1_P2P_root_linkbuf,&s1_P2P_root_tlp},  
    .pi_w = {take_1_token(),take_credit_token(&s1_sendbuf_0, 16)},
    .po_w = {increase_credit(&s1_sendbuf_0, 5, 16),increase_credit(&s1_sendbuf_0, 6, 16),pass_credit_with_header_token(&s1_sendbuf_0, 30, 16),pass_add_header_token(&s1_sendbuf_0, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition s1_tmpbuf_to_sendbuf_5_arbiter = {
    .id = "s1_tmpbuf_to_sendbuf_5_arbiter",
    .delay_f = con_delay(0),
    .p_input = {&s1_tmpbuf_to_sendbuf_5_pidx,&s1_tmpbuf_0_5,&s1_tmpbuf_6_5},
    .p_output = {&s1_tmpbuf_to_sendbuf_5_pidx,&s1_sendbuf_5},  
    .pi_w = {take_1_token(),arbiterhelper_take_0_or_1(0, list_13, &s1_tmpbuf_to_sendbuf_5_pidx),arbiterhelper_take_0_or_1(1, list_14, &s1_tmpbuf_to_sendbuf_5_pidx)},
    .po_w = {arbiterhelper_update_cur_turn(&s1_tmpbuf_to_sendbuf_5_pidx, list_15),arbiterhelpernocapwport_pass_turn_token(&s1_tmpbuf_to_sendbuf_5_pidx, list_16, list_17)},
    .pi_w_threshold = {NULL, NULL, NULL},
    .pi_guard = {NULL, NULL, NULL},
    .pip = NULL
};
Transition s1_send_5 = {
    .id = "s1_send_5",
    .delay_f = var_tlp_process_delay(&s1_sendbuf_5, 7),
    .p_input = {&s1_sendbuf_5,&d1_recvcap},
    .p_output = {&s1_recvcap_0,&s1_recvcap_6,&s1_P2P_d1_linkbuf,&s1_P2P_d1_tlp},  
    .pi_w = {take_1_token(),take_credit_token(&s1_sendbuf_5, 16)},
    .po_w = {increase_credit(&s1_sendbuf_5, 0, 16),increase_credit(&s1_sendbuf_5, 6, 16),pass_credit_with_header_token(&s1_sendbuf_5, 30, 16),pass_add_header_token(&s1_sendbuf_5, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition s1_tmpbuf_to_sendbuf_6_arbiter = {
    .id = "s1_tmpbuf_to_sendbuf_6_arbiter",
    .delay_f = con_delay(0),
    .p_input = {&s1_tmpbuf_to_sendbuf_6_pidx,&s1_tmpbuf_0_6,&s1_tmpbuf_5_6},
    .p_output = {&s1_tmpbuf_to_sendbuf_6_pidx,&s1_sendbuf_6},  
    .pi_w = {take_1_token(),arbiterhelper_take_0_or_1(0, list_18, &s1_tmpbuf_to_sendbuf_6_pidx),arbiterhelper_take_0_or_1(1, list_19, &s1_tmpbuf_to_sendbuf_6_pidx)},
    .po_w = {arbiterhelper_update_cur_turn(&s1_tmpbuf_to_sendbuf_6_pidx, list_20),arbiterhelpernocapwport_pass_turn_token(&s1_tmpbuf_to_sendbuf_6_pidx, list_21, list_22)},
    .pi_w_threshold = {NULL, NULL, NULL},
    .pi_guard = {NULL, NULL, NULL},
    .pip = NULL
};
Transition s1_send_6 = {
    .id = "s1_send_6",
    .delay_f = var_tlp_process_delay(&s1_sendbuf_6, 7),
    .p_input = {&s1_sendbuf_6,&d3_recvcap},
    .p_output = {&s1_recvcap_0,&s1_recvcap_5,&s1_P2P_d3_linkbuf,&s1_P2P_d3_tlp},  
    .pi_w = {take_1_token(),take_credit_token(&s1_sendbuf_6, 16)},
    .po_w = {increase_credit(&s1_sendbuf_6, 0, 16),increase_credit(&s1_sendbuf_6, 5, 16),pass_credit_with_header_token(&s1_sendbuf_6, 30, 16),pass_add_header_token(&s1_sendbuf_6, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition d1_send = {
    .id = "d1_send",
    .delay_f = var_tlp_process_delay(&d1_reqbuf, 7),
    .p_input = {&d1_reqbuf,&s1_recvcap_5},
    .p_output = {&d1_reqbuf_cap,&d1_P2P_s1_tlp,&d1_P2P_s1_linkbuf},  
    .pi_w = {take_1_token(),take_credit_token(&d1_reqbuf, 16)},
    .po_w = {pass_empty_token(1),pass_add_header_token(&d1_reqbuf, 1, 30),pass_credit_with_header_token(&d1_reqbuf, 30, 16)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition d1_proc = {
    .id = "d1_proc",
    .delay_f = con_delay(0),
    .p_input = {&d1_recv},
    .p_output = {&d1_recvcomp,&d1_recvreq,&d1_recvcap},  
    .pi_w = {take_1_token()},
    .po_w = {store_readcomp_1byte(&d1_recv),store_request(1, &d1_recv, 512),increase_credit_wc(&d1_recv, 16)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition d1_send_readcmpl = {
    .id = "d1_send_readcmpl",
    .delay_f = mem_delay(&d1_recvreq, 90),
    .p_input = {&d1_recvreq,&d1_reqbuf_cmpl_cap},
    .p_output = {&d1_reqbuf_cmpl},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_token(&d1_recvreq, 1)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = con_delay(1)
};
Transition d1_arbiter = {
    .id = "d1_arbiter",
    .delay_f = con_delay(0),
    .p_input = {&d1_pidx,&d1_reqbuf_cap,&d1_reqbuf_nonpost,&d1_reqbuf_post,&d1_reqbuf_cmpl},
    .p_output = {&d1_pidx,&d1_reqbuf,&d1_reqbuf_nonpost_cap,&d1_reqbuf_post_cap,&d1_reqbuf_cmpl_cap},  
    .pi_w = {take_1_token(),take_1_token(),arbiterhelper_take_0_or_1(0, list_23, &d1_pidx),arbiterhelper_take_0_or_1(1, list_24, &d1_pidx),arbiterhelper_take_0_or_1(2, list_25, &d1_pidx)},
    .po_w = {arbiterhelper_update_cur_turn(&d1_pidx, list_26),arbiterhelper_pass_turn_token(&d1_pidx, list_27),arbiterhelper_pass_turn_empty_token(&d1_pidx, 0, list_28),arbiterhelper_pass_turn_empty_token(&d1_pidx, 1, list_29),arbiterhelper_pass_turn_empty_token(&d1_pidx, 2, list_30)},
    .pi_w_threshold = {NULL, NULL, NULL, NULL, NULL},
    .pi_guard = {NULL, NULL, NULL, NULL, NULL},
    .pip = NULL
};
Transition d2_send = {
    .id = "d2_send",
    .delay_f = var_tlp_process_delay(&d2_reqbuf, 7),
    .p_input = {&d2_reqbuf,&root_recvcap_0},
    .p_output = {&d2_reqbuf_cap,&d2_P2P_root_tlp,&d2_P2P_root_linkbuf},  
    .pi_w = {take_1_token(),take_credit_token(&d2_reqbuf, 16)},
    .po_w = {pass_empty_token(1),pass_add_header_token(&d2_reqbuf, 1, 30),pass_credit_with_header_token(&d2_reqbuf, 30, 16)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition d2_proc = {
    .id = "d2_proc",
    .delay_f = con_delay(0),
    .p_input = {&d2_recv},
    .p_output = {&d2_recvcomp,&d2_recvreq,&d2_recvcap},  
    .pi_w = {take_1_token()},
    .po_w = {store_readcomp_1byte(&d2_recv),store_request(2, &d2_recv, 512),increase_credit_wc(&d2_recv, 16)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition d2_send_readcmpl = {
    .id = "d2_send_readcmpl",
    .delay_f = mem_delay(&d2_recvreq, 90),
    .p_input = {&d2_recvreq,&d2_reqbuf_cmpl_cap},
    .p_output = {&d2_reqbuf_cmpl},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_token(&d2_recvreq, 1)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = con_delay(1)
};
Transition d2_arbiter = {
    .id = "d2_arbiter",
    .delay_f = con_delay(0),
    .p_input = {&d2_pidx,&d2_reqbuf_cap,&d2_reqbuf_nonpost,&d2_reqbuf_post,&d2_reqbuf_cmpl},
    .p_output = {&d2_pidx,&d2_reqbuf,&d2_reqbuf_nonpost_cap,&d2_reqbuf_post_cap,&d2_reqbuf_cmpl_cap},  
    .pi_w = {take_1_token(),take_1_token(),arbiterhelper_take_0_or_1(0, list_31, &d2_pidx),arbiterhelper_take_0_or_1(1, list_32, &d2_pidx),arbiterhelper_take_0_or_1(2, list_33, &d2_pidx)},
    .po_w = {arbiterhelper_update_cur_turn(&d2_pidx, list_34),arbiterhelper_pass_turn_token(&d2_pidx, list_35),arbiterhelper_pass_turn_empty_token(&d2_pidx, 0, list_36),arbiterhelper_pass_turn_empty_token(&d2_pidx, 1, list_37),arbiterhelper_pass_turn_empty_token(&d2_pidx, 2, list_38)},
    .pi_w_threshold = {NULL, NULL, NULL, NULL, NULL},
    .pi_guard = {NULL, NULL, NULL, NULL, NULL},
    .pip = NULL
};
Transition d3_send = {
    .id = "d3_send",
    .delay_f = var_tlp_process_delay(&d3_reqbuf, 7),
    .p_input = {&d3_reqbuf,&s1_recvcap_6},
    .p_output = {&d3_reqbuf_cap,&d3_P2P_s1_tlp,&d3_P2P_s1_linkbuf},  
    .pi_w = {take_1_token(),take_credit_token(&d3_reqbuf, 16)},
    .po_w = {pass_empty_token(1),pass_add_header_token(&d3_reqbuf, 1, 30),pass_credit_with_header_token(&d3_reqbuf, 30, 16)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition d3_proc = {
    .id = "d3_proc",
    .delay_f = con_delay(0),
    .p_input = {&d3_recv},
    .p_output = {&d3_recvcomp,&d3_recvreq,&d3_recvcap},  
    .pi_w = {take_1_token()},
    .po_w = {store_readcomp_1byte(&d3_recv),store_request(3, &d3_recv, 512),increase_credit_wc(&d3_recv, 16)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition d3_send_readcmpl = {
    .id = "d3_send_readcmpl",
    .delay_f = mem_delay(&d3_recvreq, 90),
    .p_input = {&d3_recvreq,&d3_reqbuf_cmpl_cap},
    .p_output = {&d3_reqbuf_cmpl},  
    .pi_w = {take_1_token(),take_1_token()},
    .po_w = {pass_token(&d3_recvreq, 1)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = con_delay(1)
};
Transition d3_arbiter = {
    .id = "d3_arbiter",
    .delay_f = con_delay(0),
    .p_input = {&d3_pidx,&d3_reqbuf_cap,&d3_reqbuf_nonpost,&d3_reqbuf_post,&d3_reqbuf_cmpl},
    .p_output = {&d3_pidx,&d3_reqbuf,&d3_reqbuf_nonpost_cap,&d3_reqbuf_post_cap,&d3_reqbuf_cmpl_cap},  
    .pi_w = {take_1_token(),take_1_token(),arbiterhelper_take_0_or_1(0, list_39, &d3_pidx),arbiterhelper_take_0_or_1(1, list_40, &d3_pidx),arbiterhelper_take_0_or_1(2, list_41, &d3_pidx)},
    .po_w = {arbiterhelper_update_cur_turn(&d3_pidx, list_42),arbiterhelper_pass_turn_token(&d3_pidx, list_43),arbiterhelper_pass_turn_empty_token(&d3_pidx, 0, list_44),arbiterhelper_pass_turn_empty_token(&d3_pidx, 1, list_45),arbiterhelper_pass_turn_empty_token(&d3_pidx, 2, list_46)},
    .pi_w_threshold = {NULL, NULL, NULL, NULL, NULL},
    .pi_guard = {NULL, NULL, NULL, NULL, NULL},
    .pip = NULL
};
Transition s1_P2P_d3_transfer = {
    .id = "s1_P2P_d3_transfer",
    .delay_f = con_delay(405),
    .p_input = {&s1_P2P_d3_linkbuf},
    .p_output = {&s1_P2P_d3_outbuf},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(1)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = con_delay(1)
};
Transition s1_P2P_d3_merge = {
    .id = "s1_P2P_d3_merge",
    .delay_f = merge_delay(&s1_P2P_d3_tlp),
    .p_input = {&s1_P2P_d3_tlp,&s1_P2P_d3_outbuf},
    .p_output = {&d3_recv},  
    .pi_w = {take_1_token(),take_credit_token(&s1_P2P_d3_tlp, 16)},
    .po_w = {pass_rm_header_token(&s1_P2P_d3_tlp, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition d3_P2P_s1_transfer = {
    .id = "d3_P2P_s1_transfer",
    .delay_f = con_delay(405),
    .p_input = {&d3_P2P_s1_linkbuf},
    .p_output = {&d3_P2P_s1_outbuf},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(1)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = con_delay(1)
};
Transition d3_P2P_s1_merge = {
    .id = "d3_P2P_s1_merge",
    .delay_f = merge_delay(&d3_P2P_s1_tlp),
    .p_input = {&d3_P2P_s1_tlp,&d3_P2P_s1_outbuf},
    .p_output = {&s1_recv_6},  
    .pi_w = {take_1_token(),take_credit_token(&d3_P2P_s1_tlp, 16)},
    .po_w = {pass_rm_header_token(&d3_P2P_s1_tlp, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition s1_P2P_d1_transfer = {
    .id = "s1_P2P_d1_transfer",
    .delay_f = con_delay(405),
    .p_input = {&s1_P2P_d1_linkbuf},
    .p_output = {&s1_P2P_d1_outbuf},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(1)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = con_delay(1)
};
Transition s1_P2P_d1_merge = {
    .id = "s1_P2P_d1_merge",
    .delay_f = merge_delay(&s1_P2P_d1_tlp),
    .p_input = {&s1_P2P_d1_tlp,&s1_P2P_d1_outbuf},
    .p_output = {&d1_recv},  
    .pi_w = {take_1_token(),take_credit_token(&s1_P2P_d1_tlp, 16)},
    .po_w = {pass_rm_header_token(&s1_P2P_d1_tlp, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition d1_P2P_s1_transfer = {
    .id = "d1_P2P_s1_transfer",
    .delay_f = con_delay(405),
    .p_input = {&d1_P2P_s1_linkbuf},
    .p_output = {&d1_P2P_s1_outbuf},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(1)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = con_delay(1)
};
Transition d1_P2P_s1_merge = {
    .id = "d1_P2P_s1_merge",
    .delay_f = merge_delay(&d1_P2P_s1_tlp),
    .p_input = {&d1_P2P_s1_tlp,&d1_P2P_s1_outbuf},
    .p_output = {&s1_recv_5},  
    .pi_w = {take_1_token(),take_credit_token(&d1_P2P_s1_tlp, 16)},
    .po_w = {pass_rm_header_token(&d1_P2P_s1_tlp, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition root_P2P_d2_transfer = {
    .id = "root_P2P_d2_transfer",
    .delay_f = con_delay(405),
    .p_input = {&root_P2P_d2_linkbuf},
    .p_output = {&root_P2P_d2_outbuf},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(1)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = con_delay(1)
};
Transition root_P2P_d2_merge = {
    .id = "root_P2P_d2_merge",
    .delay_f = merge_delay(&root_P2P_d2_tlp),
    .p_input = {&root_P2P_d2_tlp,&root_P2P_d2_outbuf},
    .p_output = {&d2_recv},  
    .pi_w = {take_1_token(),take_credit_token(&root_P2P_d2_tlp, 16)},
    .po_w = {pass_rm_header_token(&root_P2P_d2_tlp, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition d2_P2P_root_transfer = {
    .id = "d2_P2P_root_transfer",
    .delay_f = con_delay(405),
    .p_input = {&d2_P2P_root_linkbuf},
    .p_output = {&d2_P2P_root_outbuf},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(1)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = con_delay(1)
};
Transition d2_P2P_root_merge = {
    .id = "d2_P2P_root_merge",
    .delay_f = merge_delay(&d2_P2P_root_tlp),
    .p_input = {&d2_P2P_root_tlp,&d2_P2P_root_outbuf},
    .p_output = {&root_recv_0},  
    .pi_w = {take_1_token(),take_credit_token(&d2_P2P_root_tlp, 16)},
    .po_w = {pass_rm_header_token(&d2_P2P_root_tlp, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition root_P2P_s1_transfer = {
    .id = "root_P2P_s1_transfer",
    .delay_f = con_delay(405),
    .p_input = {&root_P2P_s1_linkbuf},
    .p_output = {&root_P2P_s1_outbuf},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(1)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = con_delay(1)
};
Transition root_P2P_s1_merge = {
    .id = "root_P2P_s1_merge",
    .delay_f = merge_delay(&root_P2P_s1_tlp),
    .p_input = {&root_P2P_s1_tlp,&root_P2P_s1_outbuf},
    .p_output = {&s1_recv_0},  
    .pi_w = {take_1_token(),take_credit_token(&root_P2P_s1_tlp, 16)},
    .po_w = {pass_rm_header_token(&root_P2P_s1_tlp, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition s1_P2P_root_transfer = {
    .id = "s1_P2P_root_transfer",
    .delay_f = con_delay(405),
    .p_input = {&s1_P2P_root_linkbuf},
    .p_output = {&s1_P2P_root_outbuf},  
    .pi_w = {take_1_token()},
    .po_w = {pass_empty_token(1)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = con_delay(1)
};
Transition s1_P2P_root_merge = {
    .id = "s1_P2P_root_merge",
    .delay_f = merge_delay(&s1_P2P_root_tlp),
    .p_input = {&s1_P2P_root_tlp,&s1_P2P_root_outbuf},
    .p_output = {&root_recv_2},  
    .pi_w = {take_1_token(),take_credit_token(&s1_P2P_root_tlp, 16)},
    .po_w = {pass_rm_header_token(&s1_P2P_root_tlp, 1, 30)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
#endif