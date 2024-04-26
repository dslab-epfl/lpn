
#ifndef __TOKEN_TYPES__
#define __TOKEN_TYPES__
#include "place_transition.hh"
CREATE_TOKEN_TYPE(
token_class_bytes,
int bytes;
std::map<std::string, int>* asDictionary() override{
    std::map<std::string, int>* dict = new std::map<std::string, int>;
    dict->operator[]("bytes")=bytes; 
    return dict; 
})

CREATE_TOKEN_TYPE(
token_class_type_control_range,
int type;
int control_range;
std::map<std::string, int>* asDictionary() override{
    std::map<std::string, int>* dict = new std::map<std::string, int>;
    dict->operator[]("type")=type;
    dict->operator[]("control_range")=control_range; 
    return dict; 
})

CREATE_TOKEN_TYPE(
token_class_bytes_end_of_field_end_of_top_level,
int bytes;
int end_of_field;
int end_of_top_level;
std::map<std::string, int>* asDictionary() override{
    std::map<std::string, int>* dict = new std::map<std::string, int>;
    dict->operator[]("bytes")=bytes;
    dict->operator[]("end_of_field")=end_of_field;
    dict->operator[]("end_of_top_level")=end_of_top_level; 
    return dict; 
})

CREATE_TOKEN_TYPE(
token_class_field_index,
int field_index;
std::map<std::string, int>* asDictionary() override{
    std::map<std::string, int>* dict = new std::map<std::string, int>;
    dict->operator[]("field_index")=field_index; 
    return dict; 
})

CREATE_TOKEN_TYPE(
token_class_type_num,
int type;
int num;
std::map<std::string, int>* asDictionary() override{
    std::map<std::string, int>* dict = new std::map<std::string, int>;
    dict->operator[]("type")=type;
    dict->operator[]("num")=num; 
    return dict; 
})

CREATE_TOKEN_TYPE(
token_class_num,
int num;
std::map<std::string, int>* asDictionary() override{
    std::map<std::string, int>* dict = new std::map<std::string, int>;
    dict->operator[]("num")=num; 
    return dict; 
})

#endif