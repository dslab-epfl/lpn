
AS_DICTIONARY="""std::map<std::string, int>* asDictionary() override{{\n\
    std::map<std::string, int>* dict = new std::map<std::string, int>;\n\
{dict} \n\
    return dict; \n\
}}"""

DEF_TRANS="""\
Transition {t_id} = {{
    .id = "{t_id}",
    .delay_f = {delay_f},
    .p_input = {p_input},
    .p_output = {p_output},  
    .pi_w = {pi_w},
    .po_w = {po_w},
    .pi_w_threshold = {pi_w_threshold},
    .pi_guard = {pi_guard},
    .pip = {pip}
}};\n\
"""

TRANS_HH_INCLUDE = """#include <stdlib.h>\n#include <functional>\n#include "place_transition.hh"\n#include "places.hh"\n#include "lpn_funcs.hh"\n"""

FUNCS_HH_INCLUDE = """\
#ifndef __LPN_FUNCS_HH__
#define __LPN_FUNCS_HH__
#include <stdlib.h>
#include <functional>
#include <math.h>
#include <algorithm>
#include "place_transition.hh"
#include "places.hh"
"""

TOKEN_TYPE_HH_INCLUDE = """
#ifndef __TOKEN_TYPES__
#define __TOKEN_TYPES__
#include "place_transition.hh"
"""

PLACE_HH_INCLUDE="""
#ifndef __PLACE__
#define __PLACE__
#include "place_transition.hh"
#include "token_types.hh"
"""

SETUP_PLACE_HH_INCLUDE="""
#ifndef __SETUP_PLACE__
#define __SETUP_PLACE__
#include "places.hh"
"""

SIM_CC="""\
#include <assert.h>
#include "place_transition.hh"
#include "lpn_funcs.hh"  
#include "places.hh"
#include "transitions.hh"
//#include "setup.hh"
#include "lpn_init.hh"
#define T_SIZE {T_SIZE}  
#define LOOP_TS(func) for(int i=0;i < T_SIZE; i++){{ \\
        Transition* t = t_list[i]; \\
        func; \\
    }}  

int main(int argc, char* argv[]){{
{indent}{t_list_def};
{indent}lpn_init();
//{indent}setup(argc, argv);
{indent}uint64_t time = 0; 
{indent}uint64_t total = lpn::LARGE; 
{indent}uint64_t prev_time = 0; 
{indent}while(time < total){{
{indent}    LOOP_TS(trigger(t));
{indent}    time = min_time_g(t_list, T_SIZE);
{indent}    if(time == lpn::LARGE){{
{indent}       break;
{indent}    }}
{indent}    prev_time = time;
{indent}    LOOP_TS(sync(t, time));
{indent}}}
{indent}printf("latency %lu\\n", prev_time);
{indent}return 0;
}}
"""

# print(DEF_TRANS.format(t_id=1, delay_f=1, p_input=1, p_output=1, pi_w=1, po_w=1, pi_threshold=1, pi_guard=1, pip=1))