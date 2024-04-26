#ifndef __VTA_SETUP_HH__
#define __VTA_SETUP_HH__
#include <assert.h>
#include <fstream>
#include <iostream>
#include <string>
#include <regex>
#include <vector>
#include "place_transition.hh"
#include "lpn_funcs.hh"
#include "places.hh"
#include "transitions.hh"
#include "token_types.hh"

using namespace std;

void create_empty_queue(QT_type(EmptyToken*)* tokens, int num ){
  for(int i=0;i<num;i++){
    NEW_TOKEN(EmptyToken, x)
    tokens->push_back(x);
  }
}

int translate(map<string, int>& name_dict, string key, int type){
    if (type==1) {
        if (name_dict.find(key) == name_dict.end()) {
            printf("name not found ! %s\n", key.c_str());
            assert(0);
        }else 
            return name_dict[key];
    }else{
        return atoi(key.c_str());
    }
}

void collect_insns(QT_type(token_class_ostxyuullupppp*)* tokens, string file){


    map<string, int> name_dict;
    name_dict["compute"] = static_cast<int>(CstStr::COMPUTE);
    name_dict["load"] = static_cast<int>(CstStr::LOAD);
    name_dict["store"] = static_cast<int>(CstStr::STORE);
    name_dict["inp"] = static_cast<int>(CstStr::INP);
    name_dict["wgt"] = static_cast<int>(CstStr::WGT);
    name_dict["gemm"] = static_cast<int>(CstStr::GEMM);
    name_dict["empty"] = static_cast<int>(CstStr::EMPTY);
    name_dict["alu"] = static_cast<int>(CstStr::ALU);
    name_dict["sync"] = static_cast<int>(CstStr::SYNC);
    name_dict["finish"] = static_cast<int>(CstStr::FINISH);
    name_dict["loadUop"] = static_cast<int>(CstStr::LOADUOP);
    name_dict["loadAcc"] = static_cast<int>(CstStr::LOADACC);
    
    ifstream fin(file);
    string s;
    while(getline(fin,s)){
        vector<string> dict;
        string compact = std::regex_replace(s, std::regex(" "), "");
        // printf("%s \n", compact.c_str());
        size_t last = 0; size_t next = 0; 
        while ((next = compact.find(",", last)) != string::npos) {
            dict.push_back(compact.substr(last, next-last));
            last = next + 1;
        }
        dict.push_back(compact.substr(last, last+1));
        NEW_TOKEN(token_class_ostxyuullupppp, new_token);
        new_token->opcode = translate(name_dict, dict[1], 1);
        new_token->subopcode = translate(name_dict, dict[2], 1);
        new_token->tstype = translate(name_dict, dict[3], 1);
        new_token->xsize = translate(name_dict, dict[4], 0);
        new_token->ysize = translate(name_dict, dict[5], 0);
        new_token->uop_begin = translate(name_dict, dict[6], 0);
        new_token->uop_end = translate(name_dict, dict[7], 0);
        new_token->lp_1 = translate(name_dict, dict[8], 0);
        new_token->lp_0 = translate(name_dict, dict[9], 0);
        new_token->use_alu_imm = translate(name_dict, dict[10], 0);
        new_token->pop_prev = translate(name_dict, dict[11], 0);
        new_token->pop_next = translate(name_dict, dict[12], 0);
        new_token->push_prev = translate(name_dict, dict[13], 0);
        new_token->push_next = translate(name_dict, dict[14], 0);
        tokens->push_back(new_token);
    }

    fin.close();
    return ;
}

void setup(int arg, char* argv[]){

  create_empty_queue(&(pcompute_cap.tokens), 512);  
  create_empty_queue(&(pload_cap.tokens), 512);  
  create_empty_queue(&(pstore_cap.tokens), 512);  

  // string benchmark = "/home/jiacma/npc/tvm/3rdparty/vta-hw/src/tsim/small_petri_net/petri_sim.insns";
  string benchmark = argv[1];

  collect_insns(&(pnumInsn.tokens), benchmark);

  NEW_TOKEN(token_class_total_insn, numInstToken);
  numInstToken->total_insn = pnumInsn.tokens.size();
  int total_insn = pnumInsn.tokens.size();
  plaunch.tokens.push_back(numInstToken);

  create_empty_queue(&(pcontrol.tokens), 1);  
}

#endif