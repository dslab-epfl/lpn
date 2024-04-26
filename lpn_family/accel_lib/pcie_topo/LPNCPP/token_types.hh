
#ifndef __TOKEN_TYPES__
#define __TOKEN_TYPES__
#include "place_transition.hh"
CREATE_TOKEN_TYPE(
token_class_drcf,
int device;
int req;
int cmpl;
int from;
std::map<std::string, int>* asDictionary() override{
    std::map<std::string, int>* dict = new std::map<std::string, int>;
    dict->operator[]("device")=device;
    dict->operator[]("req")=req;
    dict->operator[]("cmpl")=cmpl;
    dict->operator[]("from")=from; 
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

CREATE_TOKEN_TYPE(
token_class_drcfp,
int device;
int req;
int cmpl;
int from;
int port;
std::map<std::string, int>* asDictionary() override{
    std::map<std::string, int>* dict = new std::map<std::string, int>;
    dict->operator[]("device")=device;
    dict->operator[]("req")=req;
    dict->operator[]("cmpl")=cmpl;
    dict->operator[]("from")=from;
    dict->operator[]("port")=port; 
    return dict; 
})

#endif