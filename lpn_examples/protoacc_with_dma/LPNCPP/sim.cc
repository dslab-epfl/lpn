#include <assert.h>
#include "place_transition.hh"
#include "lpn_funcs.hh"  
#include "places.hh"
#include "transitions.hh"
//#include "setup.hh"
#include "lpn_init.hh"
#define T_SIZE 139  
#define LOOP_TS(func) for(int i=0;i < T_SIZE; i++){ \
        Transition* t = t_list[i]; \
        func; \
    }  

int main(int argc, char* argv[]){
    Transition* t_list[T_SIZE] = { &t1, &t2, &t19, &tinject_write_dist, &t24, &tdispatch_dist, &twrite_dist, &t3_pre, &t3_post, &t10, &t9_pre, &t9_post, &split_msg, &tload_field_addr, &tload_field_addr_post, &t23_pre, &t23_post, &f1_resume, &f1_dist, &f1_eom, &f1_25, &f1_26, &f1_28, &f1_31, &f1_40, &f1_30_pre, &f1_30_post, &f1_36_pre, &f1_36_post, &f1_44_pre, &f1_44_post, &f1_37_pre, &f1_37_post, &f1_37_post2, &f1_dispatch, &f1_write_req_out, &f2_resume, &f2_dist, &f2_eom, &f2_25, &f2_26, &f2_28, &f2_31, &f2_40, &f2_30_pre, &f2_30_post, &f2_36_pre, &f2_36_post, &f2_44_pre, &f2_44_post, &f2_37_pre, &f2_37_post, &f2_37_post2, &f2_dispatch, &f2_write_req_out, &f3_resume, &f3_dist, &f3_eom, &f3_25, &f3_26, &f3_28, &f3_31, &f3_40, &f3_30_pre, &f3_30_post, &f3_36_pre, &f3_36_post, &f3_44_pre, &f3_44_post, &f3_37_pre, &f3_37_post, &f3_37_post2, &f3_dispatch, &f3_write_req_out, &f4_resume, &f4_dist, &f4_eom, &f4_25, &f4_26, &f4_28, &f4_31, &f4_40, &f4_30_pre, &f4_30_post, &f4_36_pre, &f4_36_post, &f4_44_pre, &f4_44_post, &f4_37_pre, &f4_37_post, &f4_37_post2, &f4_dispatch, &f4_write_req_out, &f5_resume, &f5_dist, &f5_eom, &f5_25, &f5_26, &f5_28, &f5_31, &f5_40, &f5_30_pre, &f5_30_post, &f5_36_pre, &f5_36_post, &f5_44_pre, &f5_44_post, &f5_37_pre, &f5_37_post, &f5_37_post2, &f5_dispatch, &f5_write_req_out, &f6_resume, &f6_dist, &f6_eom, &f6_25, &f6_26, &f6_28, &f6_31, &f6_40, &f6_30_pre, &f6_30_post, &f6_36_pre, &f6_36_post, &f6_44_pre, &f6_44_post, &f6_37_pre, &f6_37_post, &f6_37_post2, &f6_dispatch, &f6_write_req_out, &dma_read_port_arbiter, &dma_read_port_mem_get, &dma_read_port_recv_from_mem, &dma_read_port_mem_put, &dma_write_port_arbiter, &dma_write_port_mem_get, &dma_write_port_recv_from_mem, &dma_write_port_mem_put };;
    lpn_init();
//    setup(argc, argv);
    uint64_t time = 0; 
    uint64_t total = lpn::LARGE; 
    uint64_t prev_time = 0; 
    while(time < total){
        LOOP_TS(trigger(t));
        time = min_time_g(t_list, T_SIZE);
        if(time == lpn::LARGE){
           break;
        }
        prev_time = time;
        LOOP_TS(sync(t, time));
    }
    printf("latency %lu\n", prev_time);
    return 0;
}
