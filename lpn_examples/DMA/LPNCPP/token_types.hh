
#ifndef __TOKEN_TYPES__
#define __TOKEN_TYPES__
#include "place_transition.hh"
CREATE_TOKEN_TYPE(
token_class_riasbr,
int ref;
int id;
int addr;
int size;
int buffer;
int rw;
std::map<std::string, int>* asDictionary() override{
    std::map<std::string, int>* dict = new std::map<std::string, int>;
    dict->operator[]("ref")=ref;
    dict->operator[]("id")=id;
    dict->operator[]("addr")=addr;
    dict->operator[]("size")=size;
    dict->operator[]("buffer")=buffer;
    dict->operator[]("rw")=rw; 
    return dict; 
})

CREATE_TOKEN_TYPE(
token_class_idx,
int idx;
std::map<std::string, int>* asDictionary() override{
    std::map<std::string, int>* dict = new std::map<std::string, int>;
    dict->operator[]("idx")=idx; 
    return dict; 
})

#endif