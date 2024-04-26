#include <assert.h>
#include "place_transition.hh"
#include "lpn_funcs.hh"  
#include "places.hh"
#include "transitions.hh"
//#include "setup.hh"
#include "lpn_init.hh"
#define T_SIZE 46  
#define LOOP_TS(func) for(int i=0;i < T_SIZE; i++){ \
        Transition* t = t_list[i]; \
        func; \
    }  

int main(int argc, char* argv[]){
    Transition* t_list[T_SIZE] = { &troot_tmpbuf_0_2, &troot_tmpbuf_2_0, &root_tmpbuf_to_sendbuf_0_arbiter, &root_send_0, &root_tmpbuf_to_sendbuf_2_arbiter, &root_send_2, &ts1_tmpbuf_0_5, &ts1_tmpbuf_0_6, &ts1_tmpbuf_5_0, &ts1_tmpbuf_5_6, &ts1_tmpbuf_6_0, &ts1_tmpbuf_6_5, &s1_tmpbuf_to_sendbuf_0_arbiter, &s1_send_0, &s1_tmpbuf_to_sendbuf_5_arbiter, &s1_send_5, &s1_tmpbuf_to_sendbuf_6_arbiter, &s1_send_6, &d1_send, &d1_proc, &d1_send_readcmpl, &d1_arbiter, &d2_send, &d2_proc, &d2_send_readcmpl, &d2_arbiter, &d3_send, &d3_proc, &d3_send_readcmpl, &d3_arbiter, &s1_P2P_d3_transfer, &s1_P2P_d3_merge, &d3_P2P_s1_transfer, &d3_P2P_s1_merge, &s1_P2P_d1_transfer, &s1_P2P_d1_merge, &d1_P2P_s1_transfer, &d1_P2P_s1_merge, &root_P2P_d2_transfer, &root_P2P_d2_merge, &d2_P2P_root_transfer, &d2_P2P_root_merge, &root_P2P_s1_transfer, &root_P2P_s1_merge, &s1_P2P_root_transfer, &s1_P2P_root_merge };;
    lpn_init();
//    setup(argc, argv);
    int time = 0; 
    int total = 10000000000; 
    int prev_time = 0; 
    while(time < total){
        LOOP_TS(trigger(t));
        time = min_time_g(t_list, T_SIZE);
        if(time == lpn::LARGE){
           break;
        }
        prev_time = time;
        LOOP_TS(sync(t, time));
    }
    printf("latency %d\n", prev_time);
    return 0;
}
