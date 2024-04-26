#ifndef __LOG_CLASSES__
#define __LOG_CLASSES__
#include <klee/klee.h>
#include <set>
#include <map>
#include <sstream>
#include "place_transition.hh"
void log_classes(Transition* t_list[], int size, std::vector<std::string>& fire_sequence){
  std::set<BasePlace*> p_list;
  for(int i = 0; i < size; i++){
    for(auto &p : (t_list[i])->p_input){
        p_list.insert(p);
    }
    for(auto &p : (t_list[i])->p_output){
        p_list.insert(p);
    }
  }   
  int random = klee_random_int();
  std::string filepath = "classes/class."+std::to_string(random);
  std::string start = "=== start-all-tokens\n";
  std::string end = "=== end-all-tokens\n";
  // fileStream << "string";
  klee_log_string(filepath.c_str(), start.c_str());
  for(auto &p : p_list){
    if (! p->hasInit()){
        continue;
    }
    std::stringstream ss;
    ss << "== " << p->id << std::endl;
    std::string place_id_str = ss.str();
    klee_log_string(filepath.c_str(), place_id_str.c_str());
    int init_size = p->initSize();
    for(int i=0; i<init_size; i++){
        BaseToken* token = p->initAt(i);    
        std::string ith_token = "= token " + std::to_string(i) +"\n";
        klee_log_string(filepath.c_str(), ith_token.c_str());
        std::map<std::string, int>* dir = token->asDictionary();
        if (!dir) continue;
        for (const auto& pair : *(dir) ) {
            klee_print_range(pair.first.c_str(), pair.second);
            klee_log_expr(filepath.c_str(), pair.first.c_str(), pair.second);
        }
    }
  }
  klee_log_string(filepath.c_str(), end.c_str());
  std::string seq_filepath = "classes/seq."+std::to_string(random);
  for (int i = 0; i < fire_sequence.size(); i++){
      std::string seq = fire_sequence[i] + "\n";
      klee_log_string(seq_filepath.c_str(), seq.c_str());
  }
  // fileStream.close();
} 
  
#endif