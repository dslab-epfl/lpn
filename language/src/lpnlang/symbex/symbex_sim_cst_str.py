NEW_SYMBOLIC_INT="""
{indent}int {name};
{indent}klee_make_symbolic(&{name}, sizeof({name}), "{name}");
{indent}klee_assume({name} >= {min});
{indent}klee_assume({name} <= {max});
"""

SETUP_PLACE_HH_INCLUDE="""
#ifndef __SETUP_PLACE__
#define __SETUP_PLACE__
#include <klee/klee.h>
#include "places.hh"
"""

SYMBEX_SIM_CC="""
#include <assert.h> 
#include <set>
#include "place_transition.hh" 
#include "places.hh" 
#include "transitions.hh" 
#include "lpn_funcs.hh" 
#include "lpn_init.hh" 
#include "toposort.hh"
#include "log_classes.hh"
#define T_SIZE {T_SIZE}  
#define LOOP_TS(func) for(int i=0;i < T_SIZE; i++){{ \\
        Transition* t = t_list[i]; \\
        func; \\
    }}  

int main(int argc, char* argv[]){{
    int enabled_ts[T_SIZE] = {{0}}; 
    {t_list_def};
    std::vector<std::string> fire_sequence;
    lpn_init();
    std::set<BasePlace*> p_list;
    for(int i = 0; i < T_SIZE; i++){{
        for(auto &p : (t_list[i])->p_input){{
            p_list.insert(p);
        }}
        for(auto &p : (t_list[i])->p_output){{
            p_list.insert(p);
        }}
    }}
    for(auto& p: p_list){{
        if(p->tokensLen() > 0){{
            p->copyToInit();
        }}
    }}
    std::vector<BasePlace*> p_list_vec;
    std::vector<Transition*> t_list_vec;
    std::map<Transition*, int> t_list_map;
    for(auto& p : p_list){{
        p_list_vec.push_back(p);
    }}
    for(int i = 0; i < T_SIZE; i++){{
        t_list_vec.push_back(t_list[i]);
        t_list_map[t_list[i]] = i;
    }}
    auto scc_ordered_trans = topoSCCTransSort(t_list_vec, p_list_vec);
    // put all transitions that are in conflict with any in a large group (represented by NOT conflict_free). 
    // and synchronously does their commits for transitions in this group.
    // even though transitoin A and B are not in conflict with each other, they still commit synchronously,
    // because they can potentially influence each other. 
    // transitions in this group only commit once (the earliest commit), if no transitions outside of this group can commit.
    int conflict_free[T_SIZE];
    for(int i = 0; i<T_SIZE; i++){{
        conflict_free[i] = 1;
    }}
    detect_conflicting_transition_groups(t_list, T_SIZE, p_list, conflict_free);
    for(int i = 0; i<T_SIZE; i++){{
        if(conflict_free[i] == 0){{
            printf("In conflict %s \\n", t_list[i]->id.c_str());
        }}
    }}
    std::vector<int> ordered_conflict_trans_pos;
    for(auto t_group : *scc_ordered_trans){{
        int group_size = 0;
        for(auto t : t_group){{
            int pos = t_list_map[t];
            if(!conflict_free[pos]){{
                ordered_conflict_trans_pos.push_back(pos);
                group_size++;
            }}
        }}
        // -1 denotes starts another topologically sorted scc group
        if(group_size>0){{
            ordered_conflict_trans_pos.push_back(-1);
        }}
    }}

    uint64_t time = 0;
    uint64_t total = 10000000000;
    uint64_t prev_time = 0;
    int activated = 0;
    int sccs_size = scc_ordered_trans->size();
    int commit_group = 0; //max is scc_ordered_trans->size()
    while(1){{
        // cout << "log" << endl;
        int conflict_free_activated = 0;
        for(int i=0;i < T_SIZE; i++){{
            Transition* t = t_list[i];
            if (conflict_free[i] == 0) continue;
            enabled_ts[i] = trigger_for_path(t);
            conflict_free_activated = conflict_free_activated | enabled_ts[i];
        }}
        
        int conflict_activated = 0;
        if (!conflict_free_activated){{
            // no other transitions is activated;
            // activate conflict transitions
            for(int i=0;i < T_SIZE; i++){{
                Transition* t = t_list[i];
                if (conflict_free[i] == 1) continue;
                enabled_ts[i] = trigger_for_path(t);
                conflict_activated = conflict_activated | enabled_ts[i];
            }}   
        }}
        activated = conflict_activated | conflict_free_activated;
        // if all not activated, then break;
        if(!activated) break;

        // all activated conflict free transition is guaranteed to commit here
        for(int i=0;i < T_SIZE; i++){{
            Transition* t = t_list[i];
            if (conflict_free[i] == 0) continue;
            if(enabled_ts[i] == 1) {{ 
                fire_sequence.push_back(t->id);
                sync_for_path(t);
            }}
        }}
        
        // no other conflict free transition is activated
        // some conflict transition is activated
        if(conflict_activated){{
            int group_size = 0;
            Transition* to_sync_list[T_SIZE] = {{}};
            for(auto& pos : ordered_conflict_trans_pos){{
                if(pos == -1 && group_size > 0) break;
                if(pos == -1) continue;
                if(enabled_ts[pos]){{
                    Transition* t = t_list[pos];
                    to_sync_list[group_size++] = t;
                }}
            }}
            if(group_size != 0){{
                //for conflict transitions inside one scc group, commit in sync
                int min_t = min_time_g(to_sync_list, group_size);
                //commit all at min_ts, they are the minimum already
                vector<Transition*>* min_ts = min_time_t(to_sync_list, min_t, group_size);
                for(auto& t : *min_ts){{
                    fire_sequence.push_back(t->id);
                    sync_for_path(t);
                }}
            }}
        }}
    }}
    log_classes(t_list, T_SIZE, fire_sequence);
    // wellformedness
    for(int i = 0; i < T_SIZE; i++){{
        printf("%d\\n", t_list[i]->count);
    }}
    
    printf("latency %lu\\n", prev_time);
    return 0;
}}
"""