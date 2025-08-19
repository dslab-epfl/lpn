#include <assert.h>
#include "place_transition.hh"
#include "lpn_funcs.hh"  
#include "places.hh"
#include "transitions.hh"
//#include "setup.hh"
#include "lpn_init.hh"
#define T_SIZE 8  
#define LOOP_TS(func) for(int i=0;i < T_SIZE; i++){ \
        Transition* t = t_list[i]; \
        func; \
    }  

int main(int argc, char* argv[]){
    Transition* t_list[T_SIZE] = { &dma_read_port_arbiter, &dma_read_port_mem_get, &dma_read_port_recv_from_mem, &dma_read_port_mem_put, &dma_write_port_arbiter, &dma_write_port_mem_get, &dma_write_port_recv_from_mem, &dma_write_port_mem_put };;
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
