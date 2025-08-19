#pragma once
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
    SCALAR_DISPATCH_REQ=0,
    STRING_GETPTR_REQ=1,
    STRING_LOADDATA_REQ=2,
    UNPACKED_REP_GETPTR_REQ=3,
    LOAD_NEW_SUBMESSAGE=4,
    LOAD_HASBITS_AND_IS_SUBMESSAGE=5,
    LOAD_EACH_FIELD=6,
    WRITE_OUT=7,
    READ=0,
    WRITE=1,
};

std::function<int()> take_1_token() {
    auto inp_weight = [&]() -> int {
        return 1;
    };
    return inp_weight;
};
std::function<int()> take_some_token(int num) {
    auto inp_weight = [&, num]() -> int {
        return num;
    };
    return inp_weight;
};
template<typename T>
std::function<int()> take_all_tokens(Place<T>* from_place) {
    auto inp_weight = [&, from_place]() -> int {
        return from_place->tokens[0]->num;
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
std::function<int()> take_resume_token(Place<T>* num_place) {
    auto inp_weight = [&, num_place]() -> int {
        return num_place->tokens[0]->num;
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
std::function<int()> arbiterhelperord_take_0_or_1(int my_idx, Place<T>* porder_keeper) {
    auto inp_weight = [&, my_idx ,porder_keeper]() -> int {
        auto cur_turn = porder_keeper->tokens[0]->idx;
        if (cur_turn == my_idx) {
            return 1;
        }
        else {
            return 0;
        }
    };
    return inp_weight;
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
std::function<void(BasePlace*)> pass_empty_token() {
    auto out_weight = [&](BasePlace* output_place) -> void {
        NEW_TOKEN(EmptyToken, new_token);
        output_place->pushToken(new_token);
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_field_index_add_one(Place<T>* from_place, int num_handlers) {
    auto out_weight = [&, from_place ,num_handlers](BasePlace* output_place) -> void {
        auto cur_idx = from_place->tokens[0]->field_index;
        print(cur_idx, ((cur_idx % num_handlers) + 1));
        NEW_TOKEN(token_class_field_index, new_token);
        new_token->field_index = ((cur_idx % num_handlers) + 1);
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
std::function<void(BasePlace*)> push_request_order(int port, int num) {
    auto out_weight = [&, port ,num](BasePlace* output_place) -> void {
        for (int i = 0; i < num; ++i) {
            NEW_TOKEN(token_class_idx, new_token);
            new_token->idx = port;
            output_place->pushToken(new_token);
        }
    };
    return out_weight;
};
std::function<void(BasePlace*)> mem_request(int port, int id, int num) {
    auto out_weight = [&, port ,id ,num](BasePlace* output_place) -> void {
        for (int i = 0; i < num; ++i) {
            auto tk = NEW_TOKEN_WO_DECL(token_class_iasbrr);
            tk->id = id;
            tk->addr = 0;
            tk->size = 0;
            tk->buffer = 0;
            tk->rw = 0;
            tk->ref = port;
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
template<typename T>
std::function<void(BasePlace*)> anonymous_func_1_pass_token(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        auto control_range = from_place->tokens[0]->control_range;
        NEW_TOKEN(token_class_num, new_token);
        new_token->num = control_range;
        output_place->pushToken(new_token);
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
std::function<void(BasePlace*)> mem_request_v3(int port, int id, Place<T>* from_place) {
    auto out_weight = [&, port ,id ,from_place](BasePlace* output_place) -> void {
        auto num = from_place->tokens[0]->control_range;
        print(num);
        for (int i = 0; i < num; ++i) {
            auto tk = NEW_TOKEN_WO_DECL(token_class_iasbrr);
            tk->id = id;
            tk->addr = 0;
            tk->size = 0;
            tk->buffer = 0;
            tk->rw = 0;
            tk->ref = port;
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> push_request_order_v3(int port, Place<T>* from_place) {
    auto out_weight = [&, port ,from_place](BasePlace* output_place) -> void {
        auto num = from_place->tokens[0]->control_range;
        for (int i = 0; i < num; ++i) {
            NEW_TOKEN(token_class_idx, new_token);
            new_token->idx = port;
            output_place->pushToken(new_token);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> mem_request_write_v4(int port, int id, Place<T>* from_place) {
    auto out_weight = [&, port ,id ,from_place](BasePlace* output_place) -> void {
        auto bytes = from_place->tokens[0]->bytes;
        auto num = int((bytes /(double) 16));
        if ((bytes % 16) > 0) {
        num1}
        for (int i = 0; i < num; ++i) {
            auto tk = NEW_TOKEN_WO_DECL(token_class_iasbrr);
            tk->id = id;
            tk->addr = 0;
            tk->size = 16;
            tk->buffer = 0;
            tk->rw = 1;
            tk->ref = port;
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> push_write_request_order_v4(int port, Place<T>* from_place) {
    auto out_weight = [&, port ,from_place](BasePlace* output_place) -> void {
        auto bytes = from_place->tokens[0]->bytes;
        auto num = int((bytes /(double) 16));
        if ((bytes % 16) > 0) {
        num1}
        for (int i = 0; i < num; ++i) {
            NEW_TOKEN(token_class_idx, new_token);
            new_token->idx = port;
            output_place->pushToken(new_token);
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
std::function<void(BasePlace*)> pass_eom(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        if ((((int)CstStr::END_OF_MESSAGE == from_place->tokens[0]->type || (int)CstStr::END_OF_MESSAGE_TOP_LEVEL == from_place->tokens[0]->type) && from_place->tokens[0]->repeated == 0)) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_scalar(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        if ((from_place->tokens[0]->type == (int)CstStr::SCALAR && from_place->tokens[0]->repeated == 0)) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_non_scalar(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        if (((int)CstStr::NONSCALAR == from_place->tokens[0]->type && from_place->tokens[0]->repeated == 0)) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_repeated(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        if (from_place->tokens[0]->repeated == 1) {
            auto tk = from_place->tokens[0];
            output_place->pushToken(tk);
        }
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
std::function<void(BasePlace*)> pass_16_bytes_outputQ_token(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        auto bytes = from_place->tokens[0]->bytes;
        auto num = int((bytes /(double) 16));
        for (int i = 0; i < num; ++i) {
            NEW_TOKEN(token_class_bytes_end_of_field_end_of_top_level, new_token);
            new_token->bytes = 16;
            new_token->end_of_field = 0;
            new_token->end_of_top_level = 0;
            output_place->pushToken(new_token);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_bytes_token(Place<T>* from_place) {
    auto out_weight = [&, from_place](BasePlace* output_place) -> void {
        auto bytes = from_place->tokens[0]->bytes;
        auto num = int((bytes /(double) 16));
        NEW_TOKEN(token_class_num, new_token);
        new_token->num = num;
        output_place->pushToken(new_token);
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> mem_request_v2(int port, int id, Place<T>* from_place) {
    auto out_weight = [&, port ,id ,from_place](BasePlace* output_place) -> void {
        auto bytes = from_place->tokens[0]->bytes;
        auto num = int((bytes /(double) 16));
        for (int i = 0; i < num; ++i) {
            auto tk = NEW_TOKEN_WO_DECL(token_class_iasbrr);
            tk->id = id;
            tk->addr = 0;
            tk->size = 0;
            tk->buffer = 0;
            tk->rw = 0;
            tk->ref = port;
            output_place->pushToken(tk);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> push_request_order_v2(int port, Place<T>* from_place) {
    auto out_weight = [&, port ,from_place](BasePlace* output_place) -> void {
        auto bytes = from_place->tokens[0]->bytes;
        auto num = int((bytes /(double) 16));
        for (int i = 0; i < num; ++i) {
            NEW_TOKEN(token_class_idx, new_token);
            new_token->idx = port;
            output_place->pushToken(new_token);
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
template<typename T, typename U>
std::function<void(BasePlace*)> arbiterhelperord_pass_turn_token(Place<T>* porder_keeper, std::vector<Place<U>*>& list_of_buf) {
    auto out_weight = [&, porder_keeper](BasePlace* output_place) -> void {
        auto cur_turn = porder_keeper->tokens[0]->idx;
        auto cur_buf = list_of_buf[cur_turn];
        auto token = cur_buf->tokens[0];
        output_place->pushToken(token);
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_token_match_port(Place<T>* from_place, int match_port) {
    auto out_weight = [&, from_place ,match_port](BasePlace* output_place) -> void {
        auto ref = from_place->tokens[0]->ref;
        auto token = from_place->tokens[0];
        if (ref == match_port) {
            output_place->pushToken(token);
        }
    };
    return out_weight;
};
std::function<void(BasePlace*)> call_get_mem(int type) {
    auto out_weight = [&, type](BasePlace* output_place) -> void {
        NEW_TOKEN(token_class_iasbrr, new_token);
        new_token->id = 0;
        new_token->addr = 0;
        new_token->size = 0;
        new_token->buffer = 0;
        new_token->rw = 0;
        new_token->ref = 0;
        output_place->pushToken(new_token);
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> call_put_mem(Place<T>* from_place, int type) {
    auto out_weight = [&, from_place ,type](BasePlace* output_place) -> void {
        auto ref = from_place->tokens[0]->ref;
        auto id = from_place->tokens[0]->id;
        auto addr = from_place->tokens[0]->addr;
        auto size = from_place->tokens[0]->size;
        auto buffer = from_place->tokens[0]->buffer;
        auto rw = from_place->tokens[0]->rw;
    };
    return out_weight;
};
std::function<uint64_t()> con_delay_ns(int scale) {
    auto delay = [&, scale]() -> uint64_t {
        return scale;
    };
    return delay;
};
std::function<uint64_t()> con_delay(int scale) {
    auto delay = [&, scale]() -> uint64_t {
        return scale;
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
std::function<uint64_t()> delay_0_if_resp_ready(int type) {
    auto delay = [&, type]() -> uint64_t {
        return np.Inf;
    };
    return delay;
};
