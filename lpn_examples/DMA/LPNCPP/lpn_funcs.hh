#ifndef __LPN_FUNCS_HH__
#define __LPN_FUNCS_HH__
#include <stdlib.h>
#include <functional>
#include <math.h>
#include <algorithm>
#include "place_transition.hh"
#include "places.hh"
std::function<int()> take_1_token() {
    auto inp_weight = [&]() -> int {
        return 1;
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
        NEW_TOKEN(EmptyToken, new_token);
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
std::function<uint64_t()> con_delay(int scale) {
    auto delay = [&, scale]() -> uint64_t {
        return scale;
    };
    return delay;
};
std::function<uint64_t()> delay_0_if_resp_ready(int type) {
    auto delay = [&, type]() -> uint64_t {
        return np.Inf;
    };
    return delay;
};
#endif