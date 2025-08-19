#ifndef __TRANSITIONS__
#define __TRANSITIONS__
#include <stdlib.h>
#include <functional>
#include "place_transition.hh"
#include "places.hh"
#include "lpn_funcs.hh"
std::vector<Place<token_class_riasbr>*> list_0 = {&dma_read_port_req_put_0, &dma_read_port_req_put_1, &dma_read_port_req_put_2, &dma_read_port_req_put_3, &dma_read_port_req_put_4, &dma_read_port_req_put_5, &dma_read_port_req_put_6, &dma_read_port_req_put_7};
std::vector<Place<token_class_riasbr>*> list_1 = {&dma_write_port_req_put_0};
Transition dma_read_port_arbiter = {
    .id = "dma_read_port_arbiter",
    .delay_f = con_delay(0),
    .p_input = {&dma_read_port_fifo_order,&dma_read_port_req_put_0,&dma_read_port_req_put_1,&dma_read_port_req_put_2,&dma_read_port_req_put_3,&dma_read_port_req_put_4,&dma_read_port_req_put_5,&dma_read_port_req_put_6,&dma_read_port_req_put_7},
    .p_output = {&dma_read_port_mem_put_buf},  
    .pi_w = {take_1_token(),arbiterhelperord_take_0_or_1(0, &dma_read_port_fifo_order),arbiterhelperord_take_0_or_1(1, &dma_read_port_fifo_order),arbiterhelperord_take_0_or_1(2, &dma_read_port_fifo_order),arbiterhelperord_take_0_or_1(3, &dma_read_port_fifo_order),arbiterhelperord_take_0_or_1(4, &dma_read_port_fifo_order),arbiterhelperord_take_0_or_1(5, &dma_read_port_fifo_order),arbiterhelperord_take_0_or_1(6, &dma_read_port_fifo_order),arbiterhelperord_take_0_or_1(7, &dma_read_port_fifo_order)},
    .po_w = {arbiterhelperord_pass_turn_token(&dma_read_port_fifo_order, list_0)},
    .pi_w_threshold = {NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL},
    .pi_guard = {NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL},
    .pip = NULL
};
Transition dma_read_port_mem_get = {
    .id = "dma_read_port_mem_get",
    .delay_f = con_delay(0),
    .p_input = {&dma_read_port_recv_buf},
    .p_output = {&dma_read_port_req_get_0,&dma_read_port_req_get_1,&dma_read_port_req_get_2,&dma_read_port_req_get_3,&dma_read_port_req_get_4,&dma_read_port_req_get_5,&dma_read_port_req_get_6,&dma_read_port_req_get_7},  
    .pi_w = {take_1_token()},
    .po_w = {pass_token_match_port(&dma_read_port_recv_buf, 0),pass_token_match_port(&dma_read_port_recv_buf, 1),pass_token_match_port(&dma_read_port_recv_buf, 2),pass_token_match_port(&dma_read_port_recv_buf, 3),pass_token_match_port(&dma_read_port_recv_buf, 4),pass_token_match_port(&dma_read_port_recv_buf, 5),pass_token_match_port(&dma_read_port_recv_buf, 6),pass_token_match_port(&dma_read_port_recv_buf, 7)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition dma_read_port_recv_from_mem = {
    .id = "dma_read_port_recv_from_mem",
    .delay_f = delay_0_if_resp_ready(0),
    .p_input = {},
    .p_output = {&dma_read_port_recv_buf},  
    .pi_w = {},
    .po_w = {call_get_mem(0)},
    .pi_w_threshold = {},
    .pi_guard = {},
    .pip = NULL
};
Transition dma_read_port_mem_put = {
    .id = "dma_read_port_mem_put",
    .delay_f = con_delay(0),
    .p_input = {&dma_read_port_mem_put_buf},
    .p_output = {&dma_read_port_SINK},  
    .pi_w = {take_1_token()},
    .po_w = {call_put_mem(&dma_read_port_mem_put_buf, 0)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition dma_write_port_arbiter = {
    .id = "dma_write_port_arbiter",
    .delay_f = con_delay(0),
    .p_input = {&dma_write_port_fifo_order,&dma_write_port_req_put_0},
    .p_output = {&dma_write_port_mem_put_buf},  
    .pi_w = {take_1_token(),arbiterhelperord_take_0_or_1(0, &dma_write_port_fifo_order)},
    .po_w = {arbiterhelperord_pass_turn_token(&dma_write_port_fifo_order, list_1)},
    .pi_w_threshold = {NULL, NULL},
    .pi_guard = {NULL, NULL},
    .pip = NULL
};
Transition dma_write_port_mem_get = {
    .id = "dma_write_port_mem_get",
    .delay_f = con_delay(0),
    .p_input = {&dma_write_port_recv_buf},
    .p_output = {&dma_write_port_req_get_0},  
    .pi_w = {take_1_token()},
    .po_w = {pass_token_match_port(&dma_write_port_recv_buf, 0)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
Transition dma_write_port_recv_from_mem = {
    .id = "dma_write_port_recv_from_mem",
    .delay_f = delay_0_if_resp_ready(1),
    .p_input = {},
    .p_output = {&dma_write_port_recv_buf},  
    .pi_w = {},
    .po_w = {call_get_mem(1)},
    .pi_w_threshold = {},
    .pi_guard = {},
    .pip = NULL
};
Transition dma_write_port_mem_put = {
    .id = "dma_write_port_mem_put",
    .delay_f = con_delay(0),
    .p_input = {&dma_write_port_mem_put_buf},
    .p_output = {&dma_write_port_SINK},  
    .pi_w = {take_1_token()},
    .po_w = {call_put_mem(&dma_write_port_mem_put_buf, 1)},
    .pi_w_threshold = {NULL},
    .pi_guard = {NULL},
    .pip = NULL
};
#endif