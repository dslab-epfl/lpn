
#ifndef __SETUP_PLACE__
#define __SETUP_PLACE__
#include "places.hh"
void lpn_init() {

    for (int i = 0; i < 15; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        s1_recvcap_0.pushToken(new_token);
    }

    for (int i = 0; i < 15; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d2_recvcap.pushToken(new_token);
    }

    NEW_TOKEN(token_class_idx, root_tmpbuf_to_sendbuf_0_pidx_0_tk);
    root_tmpbuf_to_sendbuf_0_pidx_0_tk->idx = 0;
    root_tmpbuf_to_sendbuf_0_pidx.pushToken(root_tmpbuf_to_sendbuf_0_pidx_0_tk);

    for (int i = 0; i < 15; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        root_recvcap_2.pushToken(new_token);
    }

    NEW_TOKEN(token_class_idx, root_tmpbuf_to_sendbuf_2_pidx_0_tk);
    root_tmpbuf_to_sendbuf_2_pidx_0_tk->idx = 0;
    root_tmpbuf_to_sendbuf_2_pidx.pushToken(root_tmpbuf_to_sendbuf_2_pidx_0_tk);

    for (int i = 0; i < 15; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        root_recvcap_0.pushToken(new_token);
    }

    for (int i = 0; i < 15; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d1_recvcap.pushToken(new_token);
    }

    for (int i = 0; i < 15; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d3_recvcap.pushToken(new_token);
    }

    NEW_TOKEN(token_class_idx, s1_tmpbuf_to_sendbuf_0_pidx_0_tk);
    s1_tmpbuf_to_sendbuf_0_pidx_0_tk->idx = 0;
    s1_tmpbuf_to_sendbuf_0_pidx.pushToken(s1_tmpbuf_to_sendbuf_0_pidx_0_tk);

    for (int i = 0; i < 15; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        s1_recvcap_5.pushToken(new_token);
    }

    for (int i = 0; i < 15; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        s1_recvcap_6.pushToken(new_token);
    }

    NEW_TOKEN(token_class_idx, s1_tmpbuf_to_sendbuf_5_pidx_0_tk);
    s1_tmpbuf_to_sendbuf_5_pidx_0_tk->idx = 0;
    s1_tmpbuf_to_sendbuf_5_pidx.pushToken(s1_tmpbuf_to_sendbuf_5_pidx_0_tk);

    NEW_TOKEN(token_class_idx, s1_tmpbuf_to_sendbuf_6_pidx_0_tk);
    s1_tmpbuf_to_sendbuf_6_pidx_0_tk->idx = 0;
    s1_tmpbuf_to_sendbuf_6_pidx.pushToken(s1_tmpbuf_to_sendbuf_6_pidx_0_tk);

    for (int i = 0; i < 8; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d1_reqbuf_cap.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d1_reqbuf_cmpl_cap.pushToken(new_token);
    }

    NEW_TOKEN(token_class_idx, d1_pidx_0_tk);
    d1_pidx_0_tk->idx = 0;
    d1_pidx.pushToken(d1_pidx_0_tk);

    NEW_TOKEN(token_class_drcf, d1_reqbuf_nonpost_0_tk);
    d1_reqbuf_nonpost_0_tk->device = 2;
    d1_reqbuf_nonpost_0_tk->req = 64;
    d1_reqbuf_nonpost_0_tk->cmpl = 16;
    d1_reqbuf_nonpost_0_tk->from = 1;
    d1_reqbuf_nonpost.pushToken(d1_reqbuf_nonpost_0_tk);
    NEW_TOKEN(token_class_drcf, d1_reqbuf_nonpost_1_tk);
    d1_reqbuf_nonpost_1_tk->device = 3;
    d1_reqbuf_nonpost_1_tk->req = 64;
    d1_reqbuf_nonpost_1_tk->cmpl = 16;
    d1_reqbuf_nonpost_1_tk->from = 1;
    d1_reqbuf_nonpost.pushToken(d1_reqbuf_nonpost_1_tk);

    NEW_TOKEN(token_class_drcf, d1_reqbuf_post_0_tk);
    d1_reqbuf_post_0_tk->device = 2;
    d1_reqbuf_post_0_tk->req = 0;
    d1_reqbuf_post_0_tk->cmpl = 64;
    d1_reqbuf_post_0_tk->from = 1;
    d1_reqbuf_post.pushToken(d1_reqbuf_post_0_tk);
    NEW_TOKEN(token_class_drcf, d1_reqbuf_post_1_tk);
    d1_reqbuf_post_1_tk->device = 3;
    d1_reqbuf_post_1_tk->req = 0;
    d1_reqbuf_post_1_tk->cmpl = 64;
    d1_reqbuf_post_1_tk->from = 1;
    d1_reqbuf_post.pushToken(d1_reqbuf_post_1_tk);

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d1_reqbuf_nonpost_cap.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d1_reqbuf_post_cap.pushToken(new_token);
    }

    for (int i = 0; i < 8; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d2_reqbuf_cap.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d2_reqbuf_cmpl_cap.pushToken(new_token);
    }

    NEW_TOKEN(token_class_idx, d2_pidx_0_tk);
    d2_pidx_0_tk->idx = 0;
    d2_pidx.pushToken(d2_pidx_0_tk);

    NEW_TOKEN(token_class_drcf, d2_reqbuf_nonpost_0_tk);
    d2_reqbuf_nonpost_0_tk->device = 1;
    d2_reqbuf_nonpost_0_tk->req = 64;
    d2_reqbuf_nonpost_0_tk->cmpl = 16;
    d2_reqbuf_nonpost_0_tk->from = 2;
    d2_reqbuf_nonpost.pushToken(d2_reqbuf_nonpost_0_tk);
    NEW_TOKEN(token_class_drcf, d2_reqbuf_nonpost_1_tk);
    d2_reqbuf_nonpost_1_tk->device = 3;
    d2_reqbuf_nonpost_1_tk->req = 64;
    d2_reqbuf_nonpost_1_tk->cmpl = 16;
    d2_reqbuf_nonpost_1_tk->from = 2;
    d2_reqbuf_nonpost.pushToken(d2_reqbuf_nonpost_1_tk);

    NEW_TOKEN(token_class_drcf, d2_reqbuf_post_0_tk);
    d2_reqbuf_post_0_tk->device = 1;
    d2_reqbuf_post_0_tk->req = 0;
    d2_reqbuf_post_0_tk->cmpl = 64;
    d2_reqbuf_post_0_tk->from = 2;
    d2_reqbuf_post.pushToken(d2_reqbuf_post_0_tk);
    NEW_TOKEN(token_class_drcf, d2_reqbuf_post_1_tk);
    d2_reqbuf_post_1_tk->device = 3;
    d2_reqbuf_post_1_tk->req = 0;
    d2_reqbuf_post_1_tk->cmpl = 64;
    d2_reqbuf_post_1_tk->from = 2;
    d2_reqbuf_post.pushToken(d2_reqbuf_post_1_tk);

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d2_reqbuf_nonpost_cap.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d2_reqbuf_post_cap.pushToken(new_token);
    }

    for (int i = 0; i < 8; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d3_reqbuf_cap.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d3_reqbuf_cmpl_cap.pushToken(new_token);
    }

    NEW_TOKEN(token_class_idx, d3_pidx_0_tk);
    d3_pidx_0_tk->idx = 0;
    d3_pidx.pushToken(d3_pidx_0_tk);

    NEW_TOKEN(token_class_drcf, d3_reqbuf_nonpost_0_tk);
    d3_reqbuf_nonpost_0_tk->device = 2;
    d3_reqbuf_nonpost_0_tk->req = 64;
    d3_reqbuf_nonpost_0_tk->cmpl = 16;
    d3_reqbuf_nonpost_0_tk->from = 3;
    d3_reqbuf_nonpost.pushToken(d3_reqbuf_nonpost_0_tk);
    NEW_TOKEN(token_class_drcf, d3_reqbuf_nonpost_1_tk);
    d3_reqbuf_nonpost_1_tk->device = 1;
    d3_reqbuf_nonpost_1_tk->req = 64;
    d3_reqbuf_nonpost_1_tk->cmpl = 16;
    d3_reqbuf_nonpost_1_tk->from = 3;
    d3_reqbuf_nonpost.pushToken(d3_reqbuf_nonpost_1_tk);

    NEW_TOKEN(token_class_drcf, d3_reqbuf_post_0_tk);
    d3_reqbuf_post_0_tk->device = 2;
    d3_reqbuf_post_0_tk->req = 0;
    d3_reqbuf_post_0_tk->cmpl = 64;
    d3_reqbuf_post_0_tk->from = 3;
    d3_reqbuf_post.pushToken(d3_reqbuf_post_0_tk);
    NEW_TOKEN(token_class_drcf, d3_reqbuf_post_1_tk);
    d3_reqbuf_post_1_tk->device = 1;
    d3_reqbuf_post_1_tk->req = 0;
    d3_reqbuf_post_1_tk->cmpl = 64;
    d3_reqbuf_post_1_tk->from = 3;
    d3_reqbuf_post.pushToken(d3_reqbuf_post_1_tk);

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d3_reqbuf_nonpost_cap.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        d3_reqbuf_post_cap.pushToken(new_token);
    }

}
#endif