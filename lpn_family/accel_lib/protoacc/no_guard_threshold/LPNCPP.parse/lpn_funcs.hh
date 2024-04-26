#ifndef __LPN_FUNCS_HH__
#define __LPN_FUNCS_HH__
#include <stdlib.h>
#include <functional>
#include <math.h>
#include <algorithm>
#include "place_transition.hh"
#include "places.hh"

enum class CstStr {
    END_OF_MESSAGE=0,
    NONSCALAR=1,
    END_OF_MESSAGE_TOP_LEVEL=2,
    SCALAR=3,
    SUBMESSAGE=4,
    NONSUBMESSAGE=5,
};

std::function<int()> take_1_token() {
    auto inp_weight = [&]() -> int {
        return 1;
    };
    return inp_weight;
};
template<typename T>
std::function<int()> take_num_field_as_control(Place<T>* num_place) {
    auto inp_weight = [&, num_place]() -> int {
        return num_place->tokens[0]->control_range;
    };
    return inp_weight;
};
template<typename T>
std::function<int()> take_num_field_tokens(Place<T>* num_place) {
    auto inp_weight = [&, num_place]() -> int {
        return num_place->tokens[0]->num;
    };
    return inp_weight;
};
template<typename T>
std::function<int()> take_resume_token(Place<T>* num_place) {
    auto inp_weight = [&, num_place]() -> int {
        return num_place->tokens[0]->num;
    };
    return inp_weight;
};
std::function<void(BasePlace*)> pass_empty_token() {
    auto out_weight = [&](BasePlace* output_place) -> void {
        NEW_TOKEN(EmptyToken, new_token);
        output_place->pushToken(new_token);
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_token(Place<T>* from_place, int num) {
    auto out_weight = [&, from_place ,num](BasePlace* output_place) -> void {
        for (int i = 0; i < num; ++i) {
            auto token = from_place->tokens[i];
            output_place->pushToken(token);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_not_submessage(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        if (!(from_place->tokens[0]->type == (int)CstStr::SUBMESSAGE)) {
            NEW_TOKEN(EmptyToken, new_token);
            output_place->pushToken(new_token);
        }
    };
    return out_weight;
};
template<typename T, typename U>
std::function<void(BasePlace*)> pass_fields_meta_token(Place<T>* num_place, Place<U>* from_place) {
    auto out_weight = [&, num_place ,from_place](BasePlace* output_place) -> void {
        auto num = num_place->tokens[0]->control_range;
        for (int i = 0; i < num; ++i) {
            auto tk = from_place->tokens[i];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_non_top_token(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        auto is_top = from_place->tokens[0]->end_of_top_level == 1;
        if (!(is_top)) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_top_token(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        auto is_top = from_place->tokens[0]->end_of_top_level == 1;
        if (is_top) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_field_index_add_one(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        auto cur_idx = from_place->tokens[0]->field_index;
        NEW_TOKEN(token_class_field_index, new_token);
        new_token->field_index = 1;
        output_place->pushToken(new_token);
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_field_index_token(Place<T>* from_place, int index) {
    auto out_weight = [&, from_place ,index](BasePlace* output_place) -> void {
        if (from_place->tokens[0]->field_index == index) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_non_message_token(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        auto is_msg = from_place->tokens[0]->type == (int)CstStr::SUBMESSAGE;
        if (!(is_msg)) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_message_token(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        auto is_msg = from_place->tokens[0]->type == (int)CstStr::SUBMESSAGE;
        if (is_msg) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T, typename U>
std::function<void(BasePlace*)> pass_field_token(Place<T>* num_place, Place<U>* from_place) {
    auto out_weight = [&, num_place ,from_place](BasePlace* output_place) -> void {
        auto num = num_place->tokens[0]->num;
        for (int i = 0; i < num; ++i) {
            auto tk = from_place->tokens[i];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_num_field_token(Place<T>* num_place) {
    auto out_weight = [&, num_place](BasePlace* output_place) -> void {
        auto num = num_place->tokens[0]->num;
        NEW_TOKEN(token_class_num, new_token);
        new_token->num = num;
        output_place->pushToken(new_token);
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_scalar_outputQ_token(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        auto token = NEW_TOKEN_WO_DECL(token_class_bytes_end_of_field_end_of_top_level);
        token->bytes = from_place->tokens[0]->bytes;
        token->end_of_field = 0;
        token->end_of_top_level = 0;
        output_place->pushToken(token);
    };
    return out_weight;
};
std::function<void(BasePlace*)> pass_key_outputQ_token() {
    auto out_weight = [&](BasePlace* output_place) -> void {
        NEW_TOKEN(token_class_bytes_end_of_field_end_of_top_level, new_token);
        new_token->bytes = 1;
        new_token->end_of_field = 0;
        new_token->end_of_top_level = 0;
        output_place->pushToken(new_token);
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_all_bytes_outputQ_token(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        auto bytes = from_place->tokens[0]->bytes;
        NEW_TOKEN(token_class_bytes_end_of_field_end_of_top_level, new_token);
        new_token->bytes = bytes;
        new_token->end_of_field = 0;
        new_token->end_of_top_level = 0;
        output_place->pushToken(new_token);
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_repeated_array_token(Place<T>* from_place, int branch) {
    auto out_weight = [&, from_place ,branch](BasePlace* output_place) -> void {
        if (from_place->tokens[0]->type == branch) {
            auto num = from_place->tokens[0]->num;
            for (int i = 0; i < num; ++i) {
                NEW_TOKEN(EmptyToken, new_token);
                output_place->pushToken(new_token);
            }
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_non_field_end_token(Place<T>* from_place, int num) {
    auto out_weight = [&, from_place ,num](BasePlace* output_place) -> void {
        auto end_of_field = from_place->tokens[0]->end_of_field;
        if (end_of_field == 0) {
            for (int i = 0; i < num; ++i) {
                auto token = from_place->tokens[i];
                output_place->pushToken(token);
            }
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_write_hold_cond(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        auto end_of_field = from_place->tokens[0]->end_of_field;
        if (!(end_of_field == 0)) {
            NEW_TOKEN(EmptyToken, new_token);
            output_place->pushToken(new_token);
        }
    };
    return out_weight;
};
template<typename T, typename U>
std::function<void(BasePlace*)> pass_write_index_holder_cond(Place<T>* from_place, Place<U>* pass_token_place) {
    auto out_weight = [&, from_place ,pass_token_place](BasePlace* output_place) -> void {
        auto end_of_field = from_place->tokens[0]->end_of_field;
        if (end_of_field == 0) {
            auto tk = pass_token_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
std::function<void(BasePlace*)> pass_field_end_token() {
    auto out_weight = [&](BasePlace* output_place) -> void {
        NEW_TOKEN(token_class_bytes_end_of_field_end_of_top_level, new_token);
        new_token->bytes = 0;
        new_token->end_of_field = 1;
        new_token->end_of_top_level = 0;
        output_place->pushToken(new_token);
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_key_outputQ_end_of_toplevel_token(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        NEW_TOKEN(token_class_bytes_end_of_field_end_of_top_level, new_token);
        new_token->bytes = 1;
        new_token->end_of_field = 0;
        new_token->end_of_top_level = 0;
        output_place->pushToken(new_token);
        if (from_place->tokens[0]->type == (int)CstStr::END_OF_MESSAGE_TOP_LEVEL) {
            NEW_TOKEN(token_class_bytes_end_of_field_end_of_top_level, new_token);
            new_token->bytes = 1;
            new_token->end_of_field = 0;
            new_token->end_of_top_level = 1;
            output_place->pushToken(new_token);
        }
        else {
            assert(from_place->tokens[0]->type == (int)CstStr::END_OF_MESSAGE);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_eom(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        if ((((int)CstStr::END_OF_MESSAGE == from_place->tokens[0]->type || (int)CstStr::END_OF_MESSAGE_TOP_LEVEL == from_place->tokens[0]->type) && from_place->tokens[0]->num == 1)) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_scalar(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        if ((from_place->tokens[0]->type == (int)CstStr::SCALAR && from_place->tokens[0]->num == 1)) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_non_scalar(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        if (((int)CstStr::NONSCALAR == from_place->tokens[0]->type && from_place->tokens[0]->num == 1)) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_repeated(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        if (from_place->tokens[0]->num > 1) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
std::function<uint64_t()> con_delay(int scale) {
    auto delay = [&, scale]() -> uint64_t {
        return scale;
    };
    return delay;
};
template<typename T>
std::function<uint64_t()> write_out_delay(Place<T>* from_place) {
    auto delay = [&, from_place]() -> uint64_t {
        auto bytes = from_place->tokens[0]->bytes;
        auto mem_delay = 1;
        auto d = (int((bytes /(double) 16)) + mem_delay);
        return d;
    };
    return delay;
};
template<typename T>
std::function<uint64_t()> all_bytes_delay(Place<T>* from_place) {
    auto delay = [&, from_place]() -> uint64_t {
        auto bytes = from_place->tokens[0]->bytes;
        return 10;
    };
    return delay;
};
std::function<uint64_t()> mem_read_delay() {
    auto delay = [&]() -> uint64_t {
        return 10;
    };
    return delay;
};
template<typename T>
std::function<uint64_t()> field_end_cond_delay(Place<T>* from_place) {
    auto delay = [&, from_place]() -> uint64_t {
        auto end_of_field = from_place->tokens[0]->end_of_field;
        auto end_of_top_level = from_place->tokens[0]->end_of_top_level;
        if ((end_of_field == 0 && end_of_top_level == 0)) {
            return 1;
        }
        else {
            return 0;
        }
    };
    return delay;
};
#endif