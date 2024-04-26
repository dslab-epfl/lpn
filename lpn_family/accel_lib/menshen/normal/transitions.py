from lpnlang import Transition 
from .places import *
from .expr_o import *
from .expr_i import *
from .delay_func import *

PIP_TRY_TYPE_1 = None
PIP_TRY_TYPE_2 = None
PIP_TRY_TYPE_3 = const_pip(1)
PIP_TRY_TYPE_4 = None
PIP_TRY_TYPE_5 = None
PIP_TRY_TYPE_6 = None

t_pkt_filter_fifo = Transition(
    "t_pkt_filter_fifo",
    fifo_delay_func(),
    pi=[p_before_pkt_filter],
    po=[p_after_pkt_filter_fifo],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_pkt_filter, 1)],
    pip=exact_n_words_delay(p_before_pkt_filter) 
)

# Packet filter state machine
t_pkt_filter = Transition(
    "t_pkt_filter",
    con_delay(1),
    # pkt_filter_delay(p_after_pkt_filter_fifo),
    pi=[p_after_pkt_filter_fifo],
    po=[p_control_drop, p_after_pkt_filter],
    pi_w=[take_1_token()],
    # Use pass_data_token() instead of pass_token(p_after_pkt_filter_fifo, 1) as we need the condition to be mutually-exclusive
    # with pass_drop_or_control_token(p_after_pkt_filter_fifo).
    po_w=[pass_drop_or_control_token(p_after_pkt_filter_fifo), pass_data_token(p_after_pkt_filter_fifo)],
    pip=pkt_filter_delay(p_after_pkt_filter_fifo) 
)

# Pipeline registers between pkt_filter and parser
t_pkt_filter_reg_delay = Transition(
    "t_pkt_filter_reg_delay",
    con_delay(1),
    pi=[p_after_pkt_filter],
    po=[p_after_pkt_filter_reg_delay_to_parser, p_after_pkt_filter_reg_delay_to_pkt_fifos],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_after_pkt_filter, 1), pass_token(p_after_pkt_filter, 1)],
    pip=exact_n_words_delay(p_after_pkt_filter),
)

t_parser_after_pkt_filter = Transition(
    "t_parser_after_pkt_filter",
    con_delay(1),
    pi = [p_after_pkt_filter_reg_delay_to_parser],
    po = [p_after_pkt_filter_reg_delay_to_parser_delayed],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_after_pkt_filter_reg_delay_to_parser, 1)],
    pip = exact_n_words_delay(p_after_pkt_filter_reg_delay_to_parser),
)

# parser.get_segs
t_parser_get_segs = Transition(
    "t_parser_get_segs",
    parser_get_segs_delay(p_after_pkt_filter_reg_delay_to_parser_delayed),
    pi=[p_after_pkt_filter_reg_delay_to_parser_delayed],
    po=[p_after_parser_get_segs],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_after_pkt_filter_reg_delay_to_parser_delayed, 1)],
    pip=PIP_TRY_TYPE_1 
)

# PHV parser -> 4 packet FIFOs
t_parser_to_pkt_fifos = Transition(
    "t_parser_to_pkt_fifos",
    n_words_delay(p_after_pkt_filter_reg_delay_to_pkt_fifos),
    pi=[p_pkt_fifo_cnt, p_after_pkt_filter_reg_delay_to_pkt_fifos],
    po=[p_pkt_fifo_cnt, p_before_pkt_fifo_0, p_before_pkt_fifo_1, p_before_pkt_fifo_2, p_before_pkt_fifo_3],
    pi_w=[take_1_token(), take_1_token()],
    po_w=[pass_inc_cnt(p_pkt_fifo_cnt, 4), pass_token_if_index(p_after_pkt_filter_reg_delay_to_pkt_fifos, p_pkt_fifo_cnt, 0), pass_token_if_index(p_after_pkt_filter_reg_delay_to_pkt_fifos, p_pkt_fifo_cnt, 1),pass_token_if_index(p_after_pkt_filter_reg_delay_to_pkt_fifos, p_pkt_fifo_cnt, 2),pass_token_if_index(p_after_pkt_filter_reg_delay_to_pkt_fifos, p_pkt_fifo_cnt, 3) ],
    # pip=n_words_delay(p_after_pkt_filter_reg_delay_to_pkt_fifos)
    pip = PIP_TRY_TYPE_1 
)

# Pipeline registers
t_parser_get_segs_reg_delay = Transition(
    "t_parser_get_segs_reg_delay",
    con_delay(1),
    # exact_n_words_delay(p_after_parser_get_segs),
    pi=[p_after_parser_get_segs],
    po=[p_after_parser_get_segs_reg_delay],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_after_parser_get_segs, 1)],
    pip=const_pip(-1)
)

# parser.do_parsing -> 2 subparsers
# actually parsing
t_parser_to_subparsers = Transition(
    "t_parser_to_subparsers",
    con_delay(1),
    # n_words_delay(p_after_parser_get_segs_reg_delay), # TODO (sk): check code for this.
    pi=[p_subparser_dispatch_cnt, p_after_parser_get_segs_reg_delay],
    po=[p_subparser_dispatch_cnt, p_before_subparser_0, p_before_subparser_1],
    pi_w=[take_1_token(), take_1_token()],
    po_w=[pass_inc_cnt(p_subparser_dispatch_cnt, 2), pass_token_if_index(p_after_parser_get_segs_reg_delay, p_subparser_dispatch_cnt, 0), pass_token_if_index(p_after_parser_get_segs_reg_delay, p_subparser_dispatch_cnt, 1)],
    pip=n_words_delay(p_after_parser_get_segs_reg_delay) 
)

t_subparser_0 = Transition(
    "t_subparser_0",
    con_delay(3),
    pi=[p_before_subparser_0],
    po=[p_after_subparser_0],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_subparser_0, 1)],
    pip=PIP_TRY_TYPE_1 
)

t_subparser_1 = Transition(
    "t_subparser_1",
    con_delay(3),
    pi=[p_before_subparser_1],
    po=[p_after_subparser_1],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_subparser_1, 1)],
    pip=PIP_TRY_TYPE_1
)

t_select_subparser_output = Transition(
    "t_select_subparser_output",
    con_delay(0),
    # multi_queue_n_delay(p_subparser_aggregate_cnt, ["p_after_subparser_0", "p_after_subparser_1"]),
    pi=[p_subparser_aggregate_cnt, p_after_subparser_0, p_after_subparser_1],
    po=[p_subparser_aggregate_cnt, p_subparser_result],
    pi_w=[take_1_token(), take_token_if_queue(p_subparser_aggregate_cnt, 0), take_token_if_queue(p_subparser_aggregate_cnt, 1)],
    po_w=[pass_inc_cnt(p_subparser_aggregate_cnt, 2), pass_token_from_multi_input([p_after_subparser_0, p_after_subparser_1], p_subparser_aggregate_cnt)],
    pip = PIP_TRY_TYPE_2 
)

# Pipeline registers between parser and stage 0
t_subparser_output_reg_delay = Transition(
    "t_subparser_output_reg_delay",
    con_delay(3),
    pi=[p_subparser_result],
    po=[p_before_stage_0],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_subparser_result, 1)],
    pip=const_pip(1)
)

# Stage 0
t_stage_0 = Transition(
    "t_stage_0",
    con_delay(15),
    pi=[p_before_stage_0],
    po=[p_before_stage_1],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_stage_0, 1)],
    pip=exact_n_words_delay(p_before_stage_0)
)

# Stage 1
t_stage_1 = Transition(
    "t_stage_1",
    con_delay(15),
    pi=[p_before_stage_1],
    po=[p_before_stage_2],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_stage_1, 1)],
    pip=exact_n_words_delay(p_before_stage_1)
)

# Stage 2
t_stage_2 = Transition(
    "t_stage_2",
    con_delay(15),
    pi=[p_before_stage_2],
    po=[p_before_stage_3],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_stage_2, 1)],
    pip=exact_n_words_delay(p_before_stage_2)
)

# Stage 3
t_stage_3 = Transition(
    "t_stage_3",
    con_delay(15),
    pi=[p_before_stage_3],
    po=[p_before_stage_4],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_stage_3, 1)],
    pip=exact_n_words_delay(p_before_stage_3)
)

# Stage 4 (last stage)
# The code does not have a counter to select where the output goes. It instead uses a bit in the PHV itself. This is
# annoying to compute as it would require understanding and replicating the logic of the full RMT pipeline. Since
# each PHV FIFO goes to a single deparser, I'm pretty sure that the system would get stuck if the PHV FIFOs were
# written in non-round-robin fashion. So we can use proxy logic with a round-robin counter here instead of relying
# on parsing a field in the modified PHV.
t_stage_4 = Transition(
    "t_stage_4",
    con_delay(15),
    pi=[p_phv_fifo_cnt, p_before_stage_4],
    po=[p_phv_fifo_cnt, p_before_phv_fifo_0, p_before_phv_fifo_1, p_before_phv_fifo_2, p_before_phv_fifo_3],
    pi_w=[take_1_token(), take_1_token()],
    po_w=[pass_inc_cnt(p_phv_fifo_cnt, 4), pass_token_if_index(p_before_stage_4, p_phv_fifo_cnt, 0), pass_token_if_index(p_before_stage_4, p_phv_fifo_cnt, 1), pass_token_if_index(p_before_stage_4, p_phv_fifo_cnt, 2), pass_token_if_index(p_before_stage_4, p_phv_fifo_cnt, 3)],
    pip=exact_n_words_delay(p_before_stage_4)
)

# PHV FIFOs after stage 4
t_phv_fifo_0 = Transition(
    "t_phv_fifo_0",
    fifo_delay_func(),
    pi=[p_before_phv_fifo_0],
    po=[p_after_phv_fifo_0],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_phv_fifo_0, 1)],
    pip = PIP_TRY_TYPE_3 
)
t_phv_fifo_1 = Transition(
    "t_phv_fifo_1",
    fifo_delay_func(),
    pi=[p_before_phv_fifo_1],
    po=[p_after_phv_fifo_1],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_phv_fifo_1, 1)],
    pip = PIP_TRY_TYPE_3 
)
t_phv_fifo_2 = Transition(
    "t_phv_fifo_2",
    fifo_delay_func(),
    pi=[p_before_phv_fifo_2],
    po=[p_after_phv_fifo_2],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_phv_fifo_2, 1)],
    pip = PIP_TRY_TYPE_3 
)
t_phv_fifo_3 = Transition(
    "t_phv_fifo_3",
    fifo_delay_func(),
    pi=[p_before_phv_fifo_3],
    po=[p_after_phv_fifo_3],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_phv_fifo_3, 1)],
    pip = PIP_TRY_TYPE_3 
)

# # Packet FIFOs after parser
t_pkt_fifo_0 = Transition(
    "t_pkt_fifo_0",
    fifo_delay_func(),
    pi=[p_before_pkt_fifo_0],
    po=[p_after_pkt_fifo_0],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_pkt_fifo_0, 1)],
    pip = PIP_TRY_TYPE_4
)
t_pkt_fifo_1 = Transition(
    "t_pkt_fifo_1",
    fifo_delay_func(),
    pi=[p_before_pkt_fifo_1],
    po=[p_after_pkt_fifo_1],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_pkt_fifo_1, 1)],
    pip = PIP_TRY_TYPE_4
)
t_pkt_fifo_2 = Transition(
    "t_pkt_fifo_2",
    fifo_delay_func(),
    pi=[p_before_pkt_fifo_2],
    po=[p_after_pkt_fifo_2],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_pkt_fifo_2, 1)],
    pip = PIP_TRY_TYPE_4
)
t_pkt_fifo_3 = Transition(
    "t_pkt_fifo_3",
    fifo_delay_func(),
    pi=[p_before_pkt_fifo_3],
    po=[p_after_pkt_fifo_3],
    pi_w=[take_1_token()],
    po_w=[pass_token(p_before_pkt_fifo_3, 1)],
    pip = PIP_TRY_TYPE_4
)

# Sub-deparsers
t_deparser_0 = Transition(
    "t_deparser_0",
    con_delay(6),
    pi=[p_after_pkt_fifo_0, p_after_phv_fifo_0],
    # pi=[p_after_phv_fifo_0],
    po=[p_after_subdeparser_0],
    pi_w=[take_1_token(), take_1_token()],
    # Pass data from pkt_fifo so we can have access to n_words in output arbiter.
    po_w=[pass_token(p_after_pkt_fifo_0, 1)],
    pip = PIP_TRY_TYPE_5
)
t_deparser_1 = Transition(
    "t_deparser_1",
    con_delay(6),
    pi=[p_after_pkt_fifo_1, p_after_phv_fifo_1],
    # pi=[p_after_phv_fifo_1],
    po=[p_after_subdeparser_1],
    pi_w=[take_1_token(), take_1_token()],
    # Pass data from pkt_fifo so we can have access to n_words in output arbiter.
    po_w=[pass_token(p_after_pkt_fifo_1, 1)],
    pip = PIP_TRY_TYPE_5
)
t_deparser_2 = Transition(
    "t_deparser_2",
    con_delay(6),
    pi=[p_after_pkt_fifo_2, p_after_phv_fifo_2],
    # pi=[p_after_phv_fifo_2],
    po=[p_after_subdeparser_2],
    pi_w=[take_1_token(), take_1_token()],
    # Pass data from pkt_fifo so we can have access to n_words in output arbiter.
    po_w=[pass_token(p_after_pkt_fifo_2, 1)],
    pip = PIP_TRY_TYPE_5
)
t_deparser_3 = Transition(
    "t_deparser_3",
    con_delay(6),
    pi=[p_after_pkt_fifo_3, p_after_phv_fifo_3],
    # pi=[p_after_phv_fifo_3],
    po=[p_after_subdeparser_3],
    pi_w=[take_1_token(), take_1_token()],
    # Pass data from pkt_fifo so we can have access to n_words in output arbiter.
    po_w=[pass_token(p_after_pkt_fifo_3, 1)],
    pip = PIP_TRY_TYPE_5
)

# Output arbiter
t_output_arbiter = Transition(
    "t_output_arbiter",
    # con_delay(0),
    multi_queue_n_plus_f_delay(p_output_arbiter_cnt, [p_after_subdeparser_0, p_after_subdeparser_1, p_after_subdeparser_2, p_after_subdeparser_3]),
    pi=[p_output_arbiter_cnt, p_after_subdeparser_0, p_after_subdeparser_1, p_after_subdeparser_2, p_after_subdeparser_3],
    po=[p_output_arbiter_cnt, p_after_output_arbiter],
    pi_w=[take_1_token(), take_token_if_queue(p_output_arbiter_cnt, 0), take_token_if_queue(p_output_arbiter_cnt, 1), take_token_if_queue(p_output_arbiter_cnt, 2), take_token_if_queue(p_output_arbiter_cnt, 3)], # TODO: Have to choose in round-robin order, not 1 from all queues.
    po_w=[pass_inc_cnt(p_output_arbiter_cnt, 4), pass_empty_token()],
    pip =None
)
