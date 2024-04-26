from .places import *
from .transitions import *

def lpn_def():
    # TODO: Fill
    all_ts = [
        t_pkt_filter_fifo,
        t_pkt_filter,
        t_pkt_filter_reg_delay,
        t_parser_after_pkt_filter,
        t_parser_get_segs,
        t_parser_get_segs_reg_delay,
        t_parser_to_subparsers,
        t_subparser_0,
        t_subparser_1,
        t_select_subparser_output,
        t_subparser_output_reg_delay,
        t_parser_to_pkt_fifos,
        t_stage_0,
        t_stage_1,
        t_stage_2,
        t_stage_3,
        t_stage_4,
        t_phv_fifo_0,
        t_phv_fifo_1,
        t_phv_fifo_2,
        t_phv_fifo_3,
        t_pkt_fifo_0,
        t_pkt_fifo_1,
        t_pkt_fifo_2,
        t_pkt_fifo_3,
        t_deparser_0,
        t_deparser_1,
        t_deparser_2,
        t_deparser_3,
        t_output_arbiter,
    ]
    node_dict = {}
    all_Place = []
    for t in all_ts:
        for p in t.p_input + t.p_output:
            if p not in all_Place:
                all_Place.append(p)

    for p in all_Place:
        # last_log[p.id] = len(p.tokens)
        node_dict[p.id] = p
    
    for t in all_ts:
        node_dict[t.id] = t
        
    return all_Place, all_ts, node_dict 