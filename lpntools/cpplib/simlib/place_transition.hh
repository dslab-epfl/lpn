#ifndef __LPN_PLACE_Transition__
#define __LPN_PLACE_Transition__
#include <bits/stdint-uintn.h>
#include <string>
#include <map>
#include <set>
#include <deque>
#include <utility>
#include <vector>
#include <iostream>
#include <functional>

#define QT_type(T) std::deque<T>
#define NEW_QT(T, x) QT_type(T)* x = new QT_type(T)
#define NEW_TOKEN(T, x) T* x = new T;
#define NEW_TOKEN_WO_DECL(T) new T;

namespace lpn {
  
const uint64_t LARGE = (1ULL << 63); 
extern uint64_t CLK;

}

class BaseToken {
public:
  uint64_t ts=0;
  virtual std::map<std::string, int>* asDictionary(){
    return nullptr;
  }
  virtual ~BaseToken() = default;
};

class EmptyToken: public BaseToken{
  std::map<std::string, int>* asDictionary() override{
    return nullptr;
  }
};

#define CREATE_TOKEN_TYPE(name, ...) \
class name: public BaseToken \
{ public: __VA_ARGS__  };

class BasePlace {
public:
    std::string id;
    explicit BasePlace(std::string asid) : id(std::move(asid)) {}
    
    virtual int tokensLen() const {
      return 0;
    }
    virtual uint64_t tsAt(int idx) const {
      return 0;
    }
    virtual void setTokenTs(int idx, uint64_t ts) {
    }
    virtual std::string getId() const {
      return "";
    }
    virtual void pushToken(BaseToken*){
      std::cout << "call default push token" << std::endl;
    }
    virtual void popToken() {
    }
    virtual void reset() {
    }
    virtual void copyToInit(){
    }
    virtual bool hasInit() const {
      return false;
    }
    virtual int initSize() const {
      return 0;
    }
    virtual BaseToken* initAt(int idx) const {
      return nullptr;
    }
    virtual ~BasePlace() = default;
};

template<typename TokenType = EmptyToken>
class Place : public BasePlace
{
  public:
  explicit Place(const std::string& asid) : BasePlace(asid) {}
  std::deque<TokenType*> tokens;
  std::deque<TokenType*> tokens_init;
  
  bool hasInit() const override{
    return tokens_init.size() > 0;
  }
  void copyToInit() override{
    for(auto& token: tokens){
      tokens_init.push_back(token);
    }
  }
  int initSize() const override{
    return tokens_init.size();
  }
  BaseToken* initAt(int idx) const override{
    return tokens_init[idx];
  }
  int tokensLen() const override {
    return tokens.size();
  }
  uint64_t tsAt(int idx) const override{
    return tokens[idx]->ts;
  } 
  void setTokenTs(int idx, uint64_t ts) override{
    tokens[idx]->ts = ts;
  }
  std::string getId() const override {
        return id;
  }
  void popToken() final{
    tokens.pop_front();
  }
  void pushToken(BaseToken* token) final{
    tokens.push_back(static_cast<TokenType*>(token));
  }
  void reset() override{
      tokens.clear();
  }
};

using Transition = struct Transition
{
  public:
    std::string id;
    // int (*delay_f)();
    std::function<uint64_t()> delay_f;  
    std::vector<BasePlace*> p_input; 
    std::vector<BasePlace*> p_output;
    std::vector<std::function<int()>> pi_w;
    std::vector<std::function<void(BasePlace*)>> po_w;
    std::vector<std::function<bool()>> pi_w_threshold;
    std::vector<std::function<bool()>> pi_guard;
    std::function<uint64_t()> pip;  
     
    std::deque<int> consume_tokens;
    
    uint64_t delay_event=lpn::LARGE; //-1 if no event
    int disable = 0;
    uint64_t pip_ts = 0;
    int count=0;
    uint64_t time=0;
};

int check_token_requirement(BasePlace* self, int num);
int able_to_fire_t(Transition* self, uint64_t& enabled_ts);
void fire(BasePlace* self, int num);
void fire_t(Transition* self);
void accept_t(Transition* self);
uint64_t delay(Transition* self);
int trigger(Transition* self);
uint64_t min_time(Transition* self);
uint64_t min_time_g(Transition** all_ts, int size);
std::vector<Transition*>* min_time_t(Transition** all_ts, uint64_t min_t, int size);
int sync(Transition* self, uint64_t time);
int trigger_for_path(Transition* self);
int sync_for_path(Transition* self);
void detect_conflicting_Transition_groups(Transition** t_list, int size, std::set<BasePlace*>& p_list, int* conflict_free);

#endif
