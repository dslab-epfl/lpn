#ifndef __LPN_FUNCS_HH__
#define __LPN_FUNCS_HH__
#include <stdlib.h>
#include <functional>
#include <math.h>
#include <algorithm>
#include "place_transition.hh"
#include "places.hh"

enum class CstStr {
    D0=0,
    D1=1,
    D2=2,
    D3=3,
    D4=4,
    D5=5,
    D6=6,
    D7=7,
    D8=8,
    D9=9,
    D10=10,
    D11=11,
    D12=12,
    D13=13,
    D14=14,
    D15=15,
    D16=16,
    D17=17,
    D18=18,
    CMPL=20,
    POST=21,
    NONPOST=22,
};

std::function<int()> con_edge(int number) {
    auto inp_weight = [&, number]() -> int {
        return number;
    };
    return inp_weight;
};
std::function<int()> take_some_token(int num) {
    auto inp_weight = [&, num]() -> int {
        return num;
    };
    return inp_weight;
};
std::function<int()> take_1_token() {
    auto inp_weight = [&]() -> int {
        return 1;
    };
    return inp_weight;
};
template<typename T, typename U>
std::function<int()> arbiterhelper_take_0_or_1(int my_idx, std::vector<Place<T>*>& list_of_buf, Place<U>* pidx) {
    auto inp_weight = [&, my_idx ,pidx]() -> int {
        auto total = list_of_buf.size();
        std::vector<int>  tk_status ;
        for (auto p : list_of_buf) {
            tk_status.push_back(p->tokensLen());
        }
        auto cur_turn = pidx->tokens[0]->idx;
        std::vector<int>  _l ;
        for (int i = cur_turn; i < total; ++i) {
            _l.push_back(i);
        }
        for (int i = 0; i < cur_turn; ++i) {
            _l.push_back(i);
        }
        auto earliest_enabled_idx = (-1);
        for (auto i : _l) {
            if (tk_status[i] > 0) {
                earliest_enabled_idx = i;
                break;
            }
        }
        if (earliest_enabled_idx == (-1)) {
            if (cur_turn == my_idx) {
                return 1;
            }
            else {
                return 0;
            }
        }
        else {
            if (earliest_enabled_idx == my_idx) {
                return 1;
            }
            else {
                return 0;
            }
        }
    };
    return inp_weight;
};
template<typename T>
std::function<int()> take_credit_token(Place<T>* from_place, int unit) {
    auto inp_weight = [&, from_place ,unit]() -> int {
        auto num_credit = std::max(1, (int)ceil((from_place->tokens[0]->cmpl /(double) unit)));
        return num_credit;
    };
    return inp_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_atomic_smaller_token(int tlp_size, Place<T>* from_place) {
    auto out_weight = [&, tlp_size ,from_place](BasePlace* output_place) -> void {
        auto num_atomic = (int)ceil((from_place->tokens[0]->cmpl /(double) tlp_size));
        auto remain = from_place->tokens[0]->cmpl;
        for (int i = 0; i < num_atomic; ++i) {
            auto this_size =     std::min(tlp_size, remain);
            remain = (remain - this_size);
            auto token = NEW_TOKEN_WO_DECL(token_class_drcf);
            token->device = from_place->tokens[i]->device;
            token->req = from_place->tokens[i]->req;
            token->cmpl = this_size;
            token->from = from_place->tokens[i]->from;
            output_place->pushToken(token);
        }
    };
    return out_weight;
};
template<typename T, typename U>
std::function<void(BasePlace*)> arbiterhelper_update_cur_turn(Place<T>* pidx, std::vector<Place<U>*>& list_of_buf) {
    auto out_weight = [&, pidx](BasePlace* output_place) -> void {
        auto total = list_of_buf.size();
        std::vector<int>  tk_status ;
        for (auto p : list_of_buf) {
            tk_status.push_back(p->tokensLen());
        }
        auto cur_turn = pidx->tokens[0]->idx;
        auto next_turn = cur_turn;
        std::vector<int>  _l ;
        for (int i = cur_turn; i < total; ++i) {
            _l.push_back(i);
        }
        for (int i = 0; i < cur_turn; ++i) {
            _l.push_back(i);
        }
        for (auto i : _l) {
            if (tk_status[i] > 0) {
                next_turn = ((i + 1) % total);
                break;
            }
        }
        NEW_TOKEN(token_class_idx, new_token);
        new_token->idx = next_turn;
        output_place->pushToken(new_token);
    };
    return out_weight;
};
template<typename T, typename U>
std::function<void(BasePlace*)> arbiterhelpernocapwport_pass_turn_token(Place<T>* pidx, std::vector<Place<U>*>& list_of_buf, std::vector<int>& in_post_list) {
    auto out_weight = [&, pidx](BasePlace* output_place) -> void {
        auto total = list_of_buf.size();
        std::vector<int>  tk_status ;
        for (auto p : list_of_buf) {
            tk_status.push_back(p->tokensLen());
        }
        auto cur_turn = pidx->tokens[0]->idx;
        std::vector<int>  _l ;
        for (int i = cur_turn; i < total; ++i) {
            _l.push_back(i);
        }
        for (int i = 0; i < cur_turn; ++i) {
            _l.push_back(i);
        }
        auto cur_buf = list_of_buf[0];
        auto cur_port = 0;
        for (auto i : _l) {
            if (tk_status[i] > 0) {
                cur_buf = list_of_buf[i];
                cur_port = in_post_list[i];
                break;
            }
        }
        auto token = NEW_TOKEN_WO_DECL(token_class_drcfp);
        token->device = cur_buf->tokens[0]->device;
        token->req = cur_buf->tokens[0]->req;
        token->cmpl = cur_buf->tokens[0]->cmpl;
        token->from = cur_buf->tokens[0]->from;
        token->port = cur_port;
        output_place->pushToken(token);
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> increase_credit(Place<T>* send_buf, int this_port, int unit) {
    auto out_weight = [&, send_buf ,this_port ,unit](BasePlace* output_place) -> void {
        if (send_buf->tokens[0]->port == this_port) {
            auto num_credit =     std::max(1, (int)ceil((send_buf->tokens[0]->cmpl /(double) unit)));
            for (int i = 0; i < num_credit; ++i) {
                NEW_TOKEN(EmptyToken, new_token);
                output_place->pushToken(new_token);
            }
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_credit_with_header_token(Place<T>* from_place, int header_bytes, int unit) {
    auto out_weight = [&, from_place ,header_bytes ,unit](BasePlace* output_place) -> void {
        auto num_credit = std::max(1, (int)ceil(((from_place->tokens[0]->cmpl + header_bytes) /(double) unit)));
        for (int i = 0; i < num_credit; ++i) {
            NEW_TOKEN(EmptyToken, new_token);
            output_place->pushToken(new_token);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_add_header_token(Place<T>* from_place, int num, int header_bytes) {
    auto out_weight = [&, from_place ,num ,header_bytes](BasePlace* output_place) -> void {
        for (int i = 0; i < num; ++i) {
            auto token = NEW_TOKEN_WO_DECL(token_class_drcf);
            token->device = from_place->tokens[i]->device;
            token->req = from_place->tokens[i]->req;
            token->cmpl = (from_place->tokens[i]->cmpl + header_bytes);
            token->from = from_place->tokens[i]->from;
            output_place->pushToken(token);
        }
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
std::function<void(BasePlace*)> pass_empty_token(int num) {
    auto out_weight = [&, num](BasePlace* output_place) -> void {
        for (int i = 0; i < num; ++i) {
            NEW_TOKEN(EmptyToken, new_token);
            output_place->pushToken(new_token);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> store_readcomp_1byte(Place<T>* buf_place) {
    auto out_weight = [&, buf_place](BasePlace* output_place) -> void {
        auto is_req = buf_place->tokens[0]->req;
        auto num_cmpl = buf_place->tokens[0]->cmpl;
        if (is_req == 0) {
            for (int i = 0; i < num_cmpl; ++i) {
                auto token = NEW_TOKEN_WO_DECL(token_class_drcf);
                token->device = buf_place->tokens[0]->device;
                token->req = buf_place->tokens[0]->req;
                token->cmpl = 1;
                token->from = buf_place->tokens[0]->from;
                output_place->pushToken(token);
            }
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> store_request(int ori_device, Place<T>* buf_place, int mps) {
    auto out_weight = [&, ori_device ,buf_place ,mps](BasePlace* output_place) -> void {
        auto req_data = buf_place->tokens[0]->req;
        if (req_data != 0) {
            auto remain = req_data;
            auto req_from = buf_place->tokens[0]->from;
            auto transfer_count = (int)ceil((req_data /(double) mps));
            for (int i = 0; i < transfer_count; ++i) {
                auto this_size =         std::min(mps, remain);
                remain = (remain - this_size);
                NEW_TOKEN(token_class_drcf, new_token);
                new_token->device = req_from;
                new_token->req = 0;
                new_token->cmpl = this_size;
                new_token->from = ori_device;
                output_place->pushToken(new_token);
            }
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> increase_credit_wc(Place<T>* send_buf, int unit) {
    auto out_weight = [&, send_buf ,unit](BasePlace* output_place) -> void {
        auto num_credit = std::max(1, (int)ceil((send_buf->tokens[0]->cmpl /(double) unit)));
        for (int i = 0; i < num_credit; ++i) {
            NEW_TOKEN(EmptyToken, new_token);
            output_place->pushToken(new_token);
        }
    };
    return out_weight;
};
template<typename T, typename U>
std::function<void(BasePlace*)> arbiterhelper_pass_turn_token(Place<T>* pidx, std::vector<Place<U>*>& list_of_buf) {
    auto out_weight = [&, pidx](BasePlace* output_place) -> void {
        auto total = list_of_buf.size();
        std::vector<int>  tk_status ;
        for (auto p : list_of_buf) {
            tk_status.push_back(p->tokensLen());
        }
        auto cur_turn = pidx->tokens[0]->idx;
        std::vector<int>  _l ;
        for (int i = cur_turn; i < total; ++i) {
            _l.push_back(i);
        }
        for (int i = 0; i < cur_turn; ++i) {
            _l.push_back(i);
        }
        auto cur_buf = list_of_buf[0];
        for (auto i : _l) {
            if (tk_status[i] > 0) {
                cur_buf = list_of_buf[i];
                break;
            }
        }
        auto token = cur_buf->tokens[0];
        output_place->pushToken(token);
    };
    return out_weight;
};
template<typename T, typename U>
std::function<void(BasePlace*)> arbiterhelper_pass_turn_empty_token(Place<T>* pidx, int idx, std::vector<Place<U>*>& list_of_buf) {
    auto out_weight = [&, pidx ,idx](BasePlace* output_place) -> void {
        auto total = list_of_buf.size();
        std::vector<int>  tk_status ;
        for (auto p : list_of_buf) {
            tk_status.push_back(p->tokensLen());
        }
        auto cur_turn = pidx->tokens[0]->idx;
        std::vector<int>  _l ;
        for (int i = cur_turn; i < total; ++i) {
            _l.push_back(i);
        }
        for (int i = 0; i < cur_turn; ++i) {
            _l.push_back(i);
        }
        auto earliest_enabled_idx = (-1);
        for (auto i : _l) {
            if (tk_status[i] > 0) {
                earliest_enabled_idx = i;
                break;
            }
        }
        if (earliest_enabled_idx == idx) {
            NEW_TOKEN(EmptyToken, new_token);
            output_place->pushToken(new_token);
        }
    };
    return out_weight;
};
template<typename T>
std::function<void(BasePlace*)> pass_rm_header_token(Place<T>* from_place, int num, int header_bytes) {
    auto out_weight = [&, from_place ,num ,header_bytes](BasePlace* output_place) -> void {
        for (int i = 0; i < num; ++i) {
            auto token = NEW_TOKEN_WO_DECL(token_class_drcf);
            token->device = from_place->tokens[i]->device;
            token->req = from_place->tokens[i]->req;
            token->cmpl = (from_place->tokens[i]->cmpl - header_bytes);
            token->from = from_place->tokens[i]->from;
            output_place->pushToken(token);
        }
    };
    return out_weight;
};
std::function<int()> empty_threshold() {
    auto threshold = [&]() -> int {
        return 0;
    };
    return threshold;
};
template<typename T>
std::function<bool()> take_out_port(Place<T>* from_place, std::map<int, int>& routinfo, int this_port) {
    auto guard = [&, from_place ,this_port]() -> bool {
        auto dst = from_place->tokens[0]->device;
        auto out_port = routinfo[dst];
        if (out_port == this_port) {
            return true;
        }
        else {
            return false;
        }
    };
    return guard;
};
std::function<bool()> empty_guard() {
    auto guard = [&]() -> bool {
        return true;
    };
    return guard;
};
std::function<uint64_t()> con_delay(int scale) {
    auto delay = [&, scale]() -> uint64_t {
        return scale;
    };
    return delay;
};
template<typename T>
std::function<uint64_t()> var_tlp_process_delay(Place<T>* from_place, int base) {
    auto delay = [&, from_place ,base]() -> uint64_t {
        auto cmpl = from_place->tokens[0]->cmpl;
        return (((int)ceil((cmpl /(double) 16)) * 2) + base);
    };
    return delay;
};
template<typename T>
std::function<uint64_t()> mem_delay(Place<T>* from_place, int const_delay) {
    auto delay = [&, from_place ,const_delay]() -> uint64_t {
        auto req_data = from_place->tokens[0]->req;
        if (req_data > 0) {
            return 10;
        }
        else {
            auto cmpl_data = from_place->tokens[0]->cmpl;
            return ((int)ceil((cmpl_data /(double) 64)) + const_delay);
        }
    };
    return delay;
};
template<typename T>
std::function<uint64_t()> merge_delay(Place<T>* from_place) {
    auto delay = [&, from_place]() -> uint64_t {
        auto cmpl = from_place->tokens[0]->cmpl;
        return (int)ceil((cmpl /(double) 64));
    };
    return delay;
};
#endif