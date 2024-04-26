#include "place_transition.hh"
#include <bits/stdint-uintn.h>
#include <sys/types.h>
#include <iostream>

uint64_t lpn::CLK = 0;

int check_token_requirement(BasePlace* self, int num){
   if (num == -2)
     return self->tokensLen() == 0;
   return self->tokensLen() >= num;
}

void fire(BasePlace* self, int num){
   for(int i=0; i<num; i++){
      self->popToken();
   }
}

int able_to_fire_t(Transition* self, uint64_t& enabled_ts){
  //std::cerr << " ===== check fire condition "<< self->id << std::endl;
  int input_size= self->p_input.size(); 
  uint64_t max_ts = self->time;
  
  for(int i = 0; i< input_size; i++){ 
     BasePlace* p = self->p_input[i]; 
     int consume_num_tokens_real = self->pi_w[i](); 
     int consume_num_tokens_threshold = consume_num_tokens_real; 

     if(self->pi_w_threshold[i] != NULL){
        if(self->pi_w_threshold[i]() != 0){
          consume_num_tokens_threshold = self->pi_w_threshold[i](); 
        }
     }
     self->consume_tokens.push_back(consume_num_tokens_real);
     if (! check_token_requirement(p, consume_num_tokens_threshold) ){ 
        self->consume_tokens.clear();
        return 0; 
     }
      
    if (consume_num_tokens_threshold > 0){
      max_ts = std::max(max_ts, p->tsAt(consume_num_tokens_threshold-1)); 
    }
    
    if (self->pi_guard[i] == NULL) continue; 
    int grant = self->pi_guard[i](); 
    if (grant == 0) { 
      self->consume_tokens.clear();
      return 0; 
    } 
  }
  enabled_ts = max_ts;
  //std::cerr << "=== can fire end "<< std::endl;
  return 1;
} 

void fire_t(Transition* self){
  
   int input_size= self->p_input.size(); 
   for(int i=0; i < input_size; i++){ 
     BasePlace* p = self->p_input[i]; 
     int consume_num_tokens = self->consume_tokens.front();
     self->consume_tokens.pop_front(); 
     fire(p, consume_num_tokens); 
   }

  self->consume_tokens.clear();

}

void accept_t(Transition* self){
  int output_size = self->p_output.size(); 
  for(int i=0; i < output_size; i++){ 
     BasePlace* p = self->p_output[i];
     int ori_size = p->tokensLen(); 
     self->po_w[i](p); 
     int new_size = p->tokensLen();
     for(int i=ori_size; i<new_size; i++){
       p->setTokenTs(i, self->delay_event);
     }
  }
}

uint64_t delay(Transition* self){
  return self->delay_f();
}

int trigger(Transition* self){
  ////std::cerr << "trigger " << self->id << std::endl;
  if(self->delay_event != lpn::LARGE) return 1;
  if(self->disable) return 0;
  uint64_t enabled = 0;
  int can_fire = able_to_fire_t(self, enabled);
  ////std::cerr << "trigger able to fire " << can_fire << std::endl;
  if(self->delay_event == lpn::LARGE && can_fire){
     uint64_t delay_time = delay(self);
     //disabled when the delay is largest
     if (delay_time == lpn::LARGE) return 0;

     uint64_t enable_time = std::max(enabled, self->pip_ts);
     uint64_t mature_time = enable_time + delay_time; 
     if (self->pip != NULL) {
        self->pip_ts = enable_time+self->pip();
     }else{
        self->pip_ts = mature_time;
     }
     self->delay_event = mature_time;
    //  self->count += 1;
  }
  ////std::cerr << "trigger done " << self->id << std::endl;
  return can_fire;
}

uint64_t min_time(Transition* self){

   if(self->delay_event != lpn::LARGE) 
     return self->delay_event;
   return lpn::LARGE;
}

uint64_t min_time_g(Transition** all_ts, int size){

  uint64_t min = lpn::LARGE;
  Transition* min_t = NULL;
  for(int i=0; i<size; i++){
    uint64_t _t = min_time(all_ts[i]);
    if (min > _t){
      min = _t;
      min_t = all_ts[i];
    }
  }
  // if (min_t != NULL){
  //   std::cerr << "min time transition: " << min_t->id << std::endl;
  // }
  return min;
}

std::vector<Transition*>* min_time_t(Transition** all_ts, uint64_t min_t, int size){
  std::vector<Transition*>* min_ts = new std::vector<Transition*>;
   for(int i=0; i<size; i++){
    uint64_t _t = min_time(all_ts[i]);
    if (min_t == _t){
        min_ts->push_back(all_ts[i]);
    }
  }
  return min_ts;
}


int sync(Transition* self, uint64_t time){

   if (self->delay_event == lpn::LARGE){
      self->time = time;
      return 1;
   }
   
   if(time >= self->delay_event){
    //  printf("commit lpn trans: %s at cycles %lu \n", self->id.c_str(), time);
    // reordered the two
    //  std::cerr <<  "commit=" << self->id << " at ps=" << time << std::endl;
     self->count ++;
     accept_t(self);
     fire_t(self);
     self->delay_event = lpn::LARGE;
     ////std::cerr <<  "commit " << self->id << "finishes " << std::endl;
   }
   return 0;
}


int trigger_for_path(Transition* self){

  return trigger(self);
  uint64_t enabled_ts = 0;
  int can_fire = able_to_fire_t(self, enabled_ts);
  return can_fire;

}

int sync_for_path(Transition* self){
  
  self->count += 1;
  // cout << self->id << endl;
  accept_t(self);
  fire_t(self);
  self->delay_event = lpn::LARGE;
  
  return 0;
}

void detect_conflicting_Transition_groups(Transition** t_list, int size, std::set<BasePlace*>& p_list, int* conflict_free){
  std::map<BasePlace*, std::vector<int>> potential_conflict;
  for(auto& p : p_list){
    for(int i=0; i<size; i++){
      for(auto& outp : t_list[i]->p_output){
        if(p == outp){
          potential_conflict[p].push_back(i);
          break;
        }
      }
    }
  }
  for(auto& pair: potential_conflict){
    std::vector<int>& transitions = pair.second;
    if(transitions.size() > 1){
      for(auto& ti : transitions){
        conflict_free[ti] = 0;
      }
    }
  }

}
