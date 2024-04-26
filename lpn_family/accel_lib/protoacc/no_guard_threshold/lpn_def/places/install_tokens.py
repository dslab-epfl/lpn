
from lpn_def.places.places import *
from lpnlang import Token

def install_tokens():

    ps_hasBitsLoader_IsSubmessageLoad.assign_marking(deque([Token()])) 
    ps_hasBitsConsumer_AcceptIsSubmessage.assign_marking(deque([Token()]))  
    psWaitForRequest.assign_marking(deque([Token()])) 
    pdispatch_index_holder.assign_marking(deque([Token({"field_index": 1})])) 
    pf1_S_WAIT_CMD.assign_marking(deque([Token()]))  
    pf1_hold.assign_marking(deque([Token()]))  
    pf2_S_WAIT_CMD.assign_marking(deque([Token()]))  
    pf2_hold.assign_marking(deque([Token()]))  
    pf3_S_WAIT_CMD.assign_marking(deque([Token()]))  
    pf3_hold.assign_marking(deque([Token()]))  
    pf4_S_WAIT_CMD.assign_marking(deque([Token()]))  
    pf4_hold.assign_marking(deque([Token()]))  
    pf5_S_WAIT_CMD.assign_marking(deque([Token()]))  
    pf5_hold.assign_marking(deque([Token()]))  
    pf6_S_WAIT_CMD.assign_marking(deque([Token()]))  
    pf6_hold.assign_marking(deque([Token()]))  
    pwrite_index_holder.assign_marking(deque([Token({"field_index": 1})])) 
    pmem_resp_queues_cap.assign_marking(deque([Token() for i in range(16*4)]))  
    pwrite_mem_request_cap.assign_marking(deque([Token() for i in range(8)]))   
    phold.assign_marking(deque([Token()]))   
    pf1_dist_hold.assign_marking(deque([Token()]))   
    pf2_dist_hold.assign_marking(deque([Token()]))   
    pf3_dist_hold.assign_marking(deque([Token()]))   
    pf4_dist_hold.assign_marking(deque([Token()]))   
    pf5_dist_hold.assign_marking(deque([Token()]))   
    pf6_dist_hold.assign_marking(deque([Token()]))   
    pdispatch_hold.assign_marking(deque([Token()]))   
    pwrite_hold.assign_marking(deque([Token()]))   
    pholder_split_msg.assign_marking(deque([Token()]))   

