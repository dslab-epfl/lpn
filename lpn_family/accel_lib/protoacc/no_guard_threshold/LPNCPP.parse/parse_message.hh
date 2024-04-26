
#include <fstream>
#include <iostream>
#include <string>
#include <regex>
#include <vector>
#include "nlohmann/json.hpp"
#include "place_transition.hh"
#include "places.hh"
#include "lpn_funcs.hh"
using namespace std;
using json = nlohmann::ordered_json;

deque<token_class_type_control_range*> control_tokens;
deque<token_class_type_num*> fields_meta_tokens;
deque<token_class_bytes*> unit_tokens;

int COUNT = 0;

void clear_message_trace() {
    control_tokens.clear();
    fields_meta_tokens.clear();
    unit_tokens.clear();
    COUNT = 0;
}

void parse_control_tokens_per_message(json&, int, int);
void parse_control_tokens(json& messages, int control_count = 0) {
    if (messages.is_array()) {
        // If messages is an array, iterate over each element
        for (auto& message : messages) {
            parse_control_tokens_per_message(message, control_count, 0);
        }
    } else {
        // If messages is a single object, process it directly
        parse_control_tokens_per_message(messages, control_count, 0);
    }
}

void parse_control_tokens_per_message(json& message, int control_count = 0, int depth = -1) {
    int continuous_fields_count = 0;
    std::string type_info = depth == 0 ? "end_of_message_top_level" : "end_of_message";

    json field_info = {
        {"type", type_info},
        {"is_repeated", false},
        {"data", {1}}
    };
    // Assuming `message` is a non-const json object
    message["f0"] = field_info;
    
    for (auto& [field, field_info] : message.items()) {
        string field_type = field_info["type"];
        if (field_type == "submessage") {
            // Close any previous continuous field tokens
            if (continuous_fields_count > 0){
                while (continuous_fields_count > 0) {
                    int token_range = min(continuous_fields_count, 32);
                    NEW_TOKEN(token_class_type_control_range, token);
                    token->type = (int)CstStr::NONSUBMESSAGE;
                    token->control_range = token_range;
                    control_tokens.push_back(token);
                    
                    continuous_fields_count -= token_range;
                }
            }

            // Add submessage token
            NEW_TOKEN(token_class_type_control_range, token);
            token->type = (int)CstStr::SUBMESSAGE;
            token->control_range = 0;
            control_tokens.push_back(token);

            // Recursive call for submessage
            parse_control_tokens_per_message(field_info["data"]);
        } else {
            // Increment the continuous field counter
            continuous_fields_count += 1;
        }
    }

    // Handle remaining continuous fields
    while (continuous_fields_count > 0) {
        int token_range = std::min(continuous_fields_count, 32);
        NEW_TOKEN(token_class_type_control_range, token);
        token->type = (int)CstStr::NONSUBMESSAGE;
        token->control_range = token_range;
        control_tokens.push_back(token);
        continuous_fields_count -= token_range;
    }
}

void parse_fields_and_units_per_message(json&, int);
void parse_fields_and_units(json& messages) {
    if (messages.is_array()) {
        for (auto& message : messages) {
            parse_fields_and_units_per_message(message, 0);
        }
    } else {
        parse_fields_and_units_per_message(messages, 0);
    }
}

CstStr translate(string type){
    if(type == "scalar"){
        return CstStr::SCALAR;
    }else if(type == "nonscalar")
        return CstStr::NONSCALAR;
    else if(type == "end_of_message_top_level"){
        return CstStr::END_OF_MESSAGE_TOP_LEVEL;
    }else if(type == "end_of_message")
        return CstStr::END_OF_MESSAGE;
    else{
        cout << type << endl;
        assert(0);
    }
}
void parse_fields_and_units_per_message(json& message, int depth = -1) {
    std::string type_info = depth == 0 ? "end_of_message_top_level" : "end_of_message";
    json field_info = {{"type", type_info}, {"is_repeated", false}, {"data", {1}}};
    json modified_message = message;  // Make a copy to modify
    modified_message["f0"] = field_info;
    
    for (auto& [field, field_info] : modified_message.items()) {
        if (field_info["type"] == "submessage") {
            // Recursive call for submessage
            parse_fields_and_units_per_message(field_info["data"]);
        } else {
            // Populate fields_meta_tokens
            NEW_TOKEN(token_class_type_num, token);
            token->type = (int)translate(field_info["type"]);
            token->num = static_cast<int>(field_info["data"].size());
            fields_meta_tokens.push_back(token);
            
            // Populate unit_tokens
            for (const auto& v : field_info["data"]) {
                NEW_TOKEN(token_class_bytes, token);
                token->bytes = v.get<int>();
                unit_tokens.push_back(token);
            }
        }
    }
}

json load_json(string& file_path) {
    std::ifstream file(file_path);
    json j;
    file >> j;
    return j;
}

void setup_LPN(string& file_path){
    json messages = load_json(file_path);
    parse_control_tokens(messages, 0); 
    parse_fields_and_units(messages);

    cout << control_tokens.size() << endl;
    cout << fields_meta_tokens.size() << endl;
    cout << unit_tokens.size() << endl;

  for (auto& _token : control_tokens){
    pmessage_tasks.tokens.push_back(_token);
  }

  for (auto& _token : unit_tokens){
    pfields.tokens.push_back(_token);
  }

  for (auto& _token : fields_meta_tokens){
    pfields_meta.tokens.push_back(_token);
  }
}
