
#ifndef __SETUP_PLACE__
#define __SETUP_PLACE__
#include "places.hh"
#include "parse_message.hh"
void lpn_init(int argc, char* argv[]) {
    if(argc < 2) {
       printf("specify the message path\n");
       exit(1);
    }
    string file_path = argv[1];
    setup_LPN(file_path);

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        pdispatch_hold.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        pf1_S_WAIT_CMD.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        pwrite_hold.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(token_class_field_index, pwrite_index_holder_tk);
        pwrite_index_holder_tk->field_index = 1;
        pwrite_index_holder.pushToken(pwrite_index_holder_tk);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        psWaitForRequest.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        phold.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        pf1_dist_hold.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        pholder_split_msg.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        pf1_hold.pushToken(new_token);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(token_class_field_index, pdispatch_index_holder_tk);
        pdispatch_index_holder_tk->field_index = 1;
        pdispatch_index_holder.pushToken(pdispatch_index_holder_tk);
    }

    for (int i = 0; i < 1; ++i){
        NEW_TOKEN(EmptyToken, new_token);
        ps_hasBitsLoader_IsSubmessageLoad.pushToken(new_token);
    }

}
#endif
