// A C++ program to print topological sorting of a DAG

#pragma once
#include <cassert>
#include <unordered_map>
#include <algorithm>
#include <queue>
#include <iostream>
#include <list>
#include <stack>
#include <memory>
#include "place_transition.hh"
#include "graph.hh"
using namespace std;
 
// std::vector<Transition*>* topoSCCTransSort(std::vector<Transition*>&t_list, std::vector<BasePlace*>&p_list) {
std::unique_ptr<std::vector<std::vector<Transition*>>>
topoSCCTransSort(std::vector<Transition*>&t_list, std::vector<BasePlace*>&p_list) {
    // std::map<Transition*, int>* sortInfo = new std::map<Transition*, int>();
    int eff_p_size = p_list.size();
    for(auto& p : p_list){
        if(p->is_breakpoint)
            eff_p_size+=1;
    }
    auto g = std::make_unique<Graph>(t_list.size()+eff_p_size);
    for(auto& t : t_list){
        g->declTransWithStrId(t->id, t);
    }
    for(auto& p : p_list){
        if(p->is_breakpoint){
            g->declPlaceWithStrId(p->id+"out", p);
            g->declPlaceWithStrId(p->id+"in", p);
        }else{
            g->declPlaceWithStrId(p->id, p);
        }
    }
    for(auto& t : t_list){
        for(auto& p : t->p_input){
            if(p->is_breakpoint){
                g->addEdge(g->strToIntId(p->id+"out"), g->strToIntId(t->id));
            }else{
                g->addEdge(g->strToIntId(p->id), g->strToIntId(t->id));
            }
        }
        for(auto& p : t->p_output){
            if(p->is_breakpoint){
                g->addEdge(g->strToIntId(t->id), g->strToIntId(p->id+"in"));
            }else{
                g->addEdge(g->strToIntId(t->id), g->strToIntId(p->id));
            }
        }
    }
    //find SCC 
    // nodeToSCCIndex contains mapping
    std::vector<int> node_to_SCC_node_id(g->getSize(), -1);
    auto sccg = g->buildSCCGraph(node_to_SCC_node_id);
    std::unique_ptr<stack<int>> sortedsccg = sccg->topologicalSort();
    std::stack<int> stack = *sortedsccg;
    std::vector<std::vector<Transition*>> sorted_trans;
    int ord = 0;
    while(!stack.empty()){
        int sccId = stack.top();
        std::vector<Transition*> one_group;
        for(auto t: t_list){
            if(node_to_SCC_node_id[g->strToIntId(t->id)] == ord){
                one_group.push_back(t);
            }
        }
        ord++;
        sorted_trans.push_back(one_group);
        stack.pop();
    }
    return std::make_unique<std::vector<std::vector<Transition*>>>(sorted_trans);

    // std::unique_ptr<stack<int>> stack_ptr = g->topologicalSort();
    // if (!stack_ptr){
    //     return nullptr;
    // }
    // std::stack<int> stack = *stack_ptr;
    // std::vector<Transition*>* ordered = new std::vector<Transition*>();
    // int order_cnt = 0;
    // while(!stack.empty()){
    //     int id = stack.top();
    //     if(!g->isPlaceId(id)){
    //         ordered->push_back(g->intIdToTransObj(id));
    //     }
    //     stack.pop();
    // }
    // return ordered;
}
