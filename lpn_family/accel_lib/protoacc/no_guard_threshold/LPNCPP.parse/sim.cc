#include <assert.h>
#include <chrono>
#include "place_transition.hh"
#include "lpn_funcs.hh"  
#include "places.hh"
#include "transitions.hh"
//#include "setup.hh"
#include "lpn_init.hh"
#define T_SIZE 31  
#define LOOP_TS(func) for(int i=0;i < T_SIZE; i++){ \
        Transition* t = t_list[i]; \
        func; \
    }  

int main(int argc, char* argv[]){
    auto start = std::chrono::high_resolution_clock::now();
    Transition* t_list[T_SIZE] = { &t2, &tadvance_ok, &t1, &t3, &t5, &t7, &t8, &t10, &t9, &t19, &t23, &t24, &tinject_write_dist, &tdispatch_dist, &twrite_dist, &split_msg, &dispatch_f1, &f1_25, &f1_26, &f1_28, &f1_30, &f1_31, &f1_36, &f1_37, &f1_40, &f1_44, &f1_memconnect, &f1_write_req_out, &f1_resume, &f1_eom, &f1_dist };;
    lpn_init(argc, argv);
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
    auto stop = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(stop - start);
    printf("time_elapsed %ld microseconds\n", duration.count());
    return 0;
}
