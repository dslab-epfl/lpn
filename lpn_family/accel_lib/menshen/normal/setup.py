from .places import *
from .transitions import *

def empty_tokens(x):
    new_queue = deque()
    [new_queue.append(Token()) for i in range(x)]
    return new_queue

last_log = dict()

def log_tokens(all_Place):
    print("========================")
    for p in all_Place:
        if last_log[p.id] != len(p.tokens):
            print(p.id, last_log[p.id], " -> ",len(p.tokens))
            last_log[p.id] = len(p.tokens)
    print("========================")

def setup_packets():

    pkts = [
        # n_words, is_control, is_data, is_drop
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (3, 1, 0, 0),
        (2, 1, 0, 0),
        (3, 1, 0, 0),
        (2, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (3, 1, 0, 0),
        (2, 1, 0, 0),
        (3, 1, 0, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (3, 1, 0, 0),
        (2, 1, 0, 0),
        (3, 1, 0, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (2, 0, 1, 0),
        (5, 0, 1, 0),
        (5, 0, 1, 0),
        (2, 0, 1, 0),
        (25, 0, 1, 0),
        (7, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (10, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (25, 0, 1, 0),
        (30, 0, 1, 0),
        (30, 0, 1, 0),
        (30, 0, 1, 0),
        (30, 0, 1, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (30, 0, 1, 0),
        (30, 0, 1, 0),
        (30, 0, 1, 0),
        (30, 0, 1, 0),
        (30, 0, 1, 0),
        (30, 0, 1, 0),
        (30, 0, 1, 0),
    ]
    pkts = [
        # n_words, is_control, is_data, is_drop
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (2, 1, 0, 0),
        (3, 1, 0, 0),
        (2, 1, 0, 0),
        (3, 1, 0, 0),
        (5, 0, 1, 0),
        (25, 0, 1, 0)
    ]
    print("packet length", len(pkts))
    tokens = deque()
    for cnt, (n_words, is_control, is_data, is_drop) in enumerate(pkts):
        dic = {"n_words": n_words, "is_control": is_control, "is_data": is_data, "is_drop": is_drop}
        token = Token(dic)
        tokens.append(token)
    return tokens 

def lpn_init(args):
    tokens = setup_packets()

    p_before_pkt_filter.assign_marking(tokens)
    p_subparser_dispatch_cnt.assign_marking(deque([Token({"cnt": 0})]))
    p_subparser_aggregate_cnt.assign_marking(deque([Token({"cnt": 0})]))
    p_after_subparser_0.type_annotations = ['n_words', 'is_control', 'is_data', 'is_drop']
    p_after_subparser_1 = Place("p_after_subparser_1")
    p_after_subparser_1.type_annotations = ['n_words', 'is_control', 'is_data', 'is_drop']
    p_phv_fifo_cnt.assign_marking(deque([Token({"cnt": 0})]))
    p_after_subdeparser_0.type_annotations = ['n_words', 'is_control', 'is_data', 'is_drop']
    p_after_subdeparser_1.type_annotations = ['n_words', 'is_control', 'is_data', 'is_drop']
    p_after_subdeparser_2.type_annotations = ['n_words', 'is_control', 'is_data', 'is_drop']
    p_after_subdeparser_3.type_annotations = ['n_words', 'is_control', 'is_data', 'is_drop']
    p_output_arbiter_cnt.assign_marking(deque([Token({"cnt": 0})]))
    p_pkt_fifo_cnt.assign_marking(deque([Token({"cnt": 0})]))

