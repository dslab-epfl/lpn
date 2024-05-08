# LPN (Latency Petri Net)

LPN stands for Latency Petri Net. LPN is a representation to model the performance of hardware accelerators. LPN is a variant of petri nets.

This repo contains LPN definitions, LPN tools that operate on LPNs and  LPN representations for various hardware accelerators.

We provide this [docker image](https://hub.docker.com/r/mjccjm/lpn_ae0) that contains a list of experiments and the LPN repo.
You can jump to [experiments](#run-experiments-in-the-paper) section to start various experiments we have done.

We constructed example LPNs for the following hardwares:
- [JPEG Decoder](https://github.com/ultraembedded/core_jpeg) (an image decoding accelerator)
- [Versatile Tensor Accelerator](https://github.com/apache/tvm-vta/) (a ML accelerator)
- [Menshen](https://github.com/multitenancy-project/menshen/tree/master) (a RMT pipeline)
- [Darwin](https://github.com/yatisht/darwin/tree/master) (a genomic sequence alignment accelerator)
- [Protoacc](https://github.com/ucb-bar/protoacc) (a protobuf accelerator)
- [PCIe Topology](https://www.mindshare.com/files/ebooks/PCI%20Express%20Technology%203.0.pdf) (a reconfigurable pcie topology)

## Everything about _lpn-lang_

`lpnlang` (stands for lpn language) python package contains definitions of all LPN constructs and a list of useful tools based on LPN.

### Installation

To install _lpnlang_, follow these steps:

1. `bash env_setup.sh` (to install _lpnlang_ package locally)
2. `bash setup_klee.sh` (to install [KLEE](https://klee-se.org/), you can skip this step if you only want to play with LPN in python)

### List of LPN constructs:
- _Token_ (usage: `from lpnlang import Token`) : A token is similar to a dictionary. A token has properties and integer values corresponding to each property. Properties are similar to keys in a dictionary. A token also carries an integer timestamp which denotes the time the token is produced.

- _Place_ (usage: `from lpnlang import Place`): A buffer holding tokens.
    The type of a place equals the property sets of any token it contains. All tokens that appear in one place needs to have the same property sets.

- _Transition_ (usage: `from lpnlang import Transition`): An actor that change the states of LPN by consuming and producing tokens. A transition is enabled when input places have the required tokens, after a delay, the transition will commit or fire which consumes tokens from input places and produces tokens to output places.

- _DelayFunc_ (usage: `from lpnlang import DelayFunc`): is used to construct delay functions that returns the delay for transitions. the delay function returns an integer that defines that time the corresponding transition should wait before commits after being enabled.

- _InWeightFunc_ (usage: `from lpnlang import InWeightFunc`): is used to construct input edge functions that returns the input weight on input edges. _InWeightFunc_ returns a function _f_, and _f_ returns an integer denoting the weight. One _InWeightFunc_ can be parametrized to create different edge functions with slight variation.

- _OutWeightFunc_ (usage: `from lpnlang import OutWeightFunc`): similar to _InWeightFunc_, _OutWeightFunc_ is used to construct output edge functions that returns tokens on output edges.

- _GuardFunc_ (usage: `from lpnlang import GuardFunc`): is used to create guardian (boolean) conditions on input edges. Even if the input place has enough tokens as indicated by input weights. if the guardian function returns false, the transition is not enabled.

- _ThresholdFunc_ (usage: `from lpnlang import ThresholdFunc`): is similar to _InWeightFunc_, that constructs input edge function that returns threshold on input edges. if _threshold_ is defined for an input edge, the transition enabledness condition is checked against the threshold value, however, the number of tokens consumed still equal to the input weights when the transition commits.

**Check examples under _lpn_family/accel_lib/*/lpn_def_ to see how those constructs are used.**

### List of LPN tools
- _simulate LPN_ (usage:`from lpnlang import lpn_sim`): simulates LPN in python.

- _lpn2visual_ (usage: `from lpnlang.lpn2visual import lpn_visualize`)([example](lpn_examples/vta/run_visual.py)): converts LPN into an interactive html file. Open the html file in any browser to view graphical LPN.

- _lpn2sim_ (usage: `from lpnlang.lpn2sim import pylpn2cpp`)([example](lpn_examples/vta/run_translate.py)): converts LPN in python to LPN in cpp which can then be compiled into a fast simulator. The generated simulator can't parse commandline inputs, to do that, separate cpp files to parse inputs have to be written manually.

- _lpn2pi_ (usage: `from lpnlang.lpn2pi import lpn_pi`)([example1](lpn_examples/protoacc/run_pi.py), [example2](lpn_examples/protoacc/run_pi_oneclass.py)): converts LPN and user defined symbolic input space into a readable Python program which serves as a performance interface.

- _lpn2smt_ (usage: `from lpnlang.lpn2smt import lpn_smt`)([example](lpn_examples/protoacc/run_smt.py)): converts LPN and user defined symbolic input space into verification conditions that can then be checked using solvers against user defined queries.

- _lpn2symlpn_ (usage: `from lpnlang.symbex import lpn2symlpn`)([example](lpn_examples/protoacc/run_smt.py)): converts python LPN and user defined symbolic input space into cpp LPN that can be symbolically executed by [KLEE](https://klee-se.org/) and input classes will be generated after symbolic execution. Input classes splits user defined input space into subspaces that can be processed by `lpn2smt` or `lpn2pi` one at a time.

- _log_one_class_ (usage: `from lpnlang.symbex import log_out_as_one_class`)([example](lpn_examples/protoacc/run_pi_oneclass.py)): converts user defined input space into one input class. It skips symbolic execution however relies on the users to properly define input space as one class. If the users are confident that the input space is one class, they can use this method to skip symbolic execution.

## Run examples
[lpn_examples](lpn_examples/) contains LPNs we have built for a list of hardware accelerators and a PCIe topology. In each example, there is a `Makefile`, you can run the following commands :
- `make run_example` : simulates LPN in Python.
- `make run_pi` : generate `perf_interface.py`.
- `make run_smt`: run example SMT solving.
- `make run_translate`: translate LPN in Python into LPN in cpp.
- `make run_cpp`: run `run_translate` and compile into a simulator and run.

## Run experiments in the paper

### Getting Started Instructions
- Run `docker pull mjccjm/lpn_ae0`
- Run `docker image list` and find the one pulled.
- Run `docker run -it mjccjm/lpn_ae0`
#### We provide the following list of experiments:
- Accuracy and Speedup of LPN against cycle-accurate simulation.
- Automatically generating fast simulator through `lpn2sim`.
- Automatically generating performance interfaces (`lpn2pi`)
- Accuracy of generating performance interfaces (accuracy of `lpn2pi`).
- Automatically generating performance verification conditions (`lpn2smt`).

### Detailed Instructions
Below you can find detailed instructions on how to evaluate each experiment.
We use cycle accurate simulators (Verilator or Vivado XSIM), to measure the ground-truth, so obtaining the baseline results could take a while, we mark these experiments with a **🕒**.
However, experiments that obtain performance metric s using LPNs are generally much faster (see the paper).
- **Accurary and Speedup of LPN:**
    - LPN is compared with cycle-accurate simulator (Verilator) on accuracy and speedup. We provided accuracy results for
        - JPEG decoder:
        - Menshen: the experiment includes 2 testbenches.
            - **🕒**: Running the baseline simulation Menshen requires Vivado XSIM, please consider setting it on your machine. However, for your convenience we report the measured results into the corresponding file.
        - Protoacc: is tested with the google [hyperprotobench](https://github.com/google/HyperProtoBench).
            - **🕒**: the baseline benchmark runs for a few days using Verilator. Hence we provided screen shots for the experiments we rerun (under `/home/experiments/protoacc_exp/protoacc_verilator/screenshots/`). To run the simulation, goto `/home/experiments/protoacc_exp/protoacc_verilator` and run `bash command.sh sim_binary/verilated_simulator bench<0-5>` (choose 0 to 5 corresponding to 6 benchmarks).
        - VTA: the experiment is done through `tvm` autotuning example on vta.
        - Darwin: the experiment includes 10 test examples.
    - We provide speedup results for
        - JPEG decoder: the experiment includes 50 images.
        - Protoacc: the experiment includes google hyperprotobench.
            - **🕒**: The baseline could take days to run and requires simulating a RISC-V core, which makes simulation intractably slow. To estimate the runtime we provide a testbed that feeds the accelerator with random data and measures simulation performance. Verilator's performance is known to be independent of the input stimulus, so the measurements are quite accurate.
        - VTA: the experiment is from tvm autotuning example with VTA.
            - Please use verilator version 4.022 (included in the docker).
        - Darwin: the experiment includes 10 test examples.
    - **Instructions (inside the docker)**:
        - Run tvm vta autotuning
            - Open a tmux session (run `tmux`)
            - Open 3 windows ( to open one more window: ctrl+p then press % or "), in each window goto the following directory:
                - `/home/lpn/lpn_with_x/lpn_in_tvm/tvm/vta/tutorials` (window A)
                - `/home/lpn/lpn_with_x/lpn_in_tvm/` (window B)
                - `/home/lpn/lpn_with_x/lpn_in_tvm/` (window C)
            - To run autotuning experiment:
                - Verilator:
                1. In window C, run `bash compile_verilator.sh`
                2. In window B, run `./rpc_tracker.sh`
                3. In window C, run `./rpc_server.sh > log_verilator_time 2>&1`
                4. In window A, run `bash run_tsim.sh`
                5. Wait for `bash run_tsim.sh` to finish (~2h)
                - LPN:
                1. In window C, run `bash compile_lpn.sh`
                2. In window B, run `./rpc_tracker.sh`
                3. In window C, run `./rpc_server.sh > log_lpn_time 2>&1`
                4. In window A, run `bash run_tsim.sh`
                5. Wait for `bash run_tsim.sh` to finish
        - Goto `/home/experiments`
        - Do `bash run_all.sh`
    - You will see a list of plots (in pdf) generated in /`home/experiments/pdfs`
            - To copy the pdfs out of container, use `docker cp <container-id>:<src_in_container> <dst_in_your_machine>`.

- **Automatically generating fast simulator through lpn2sim:**
    - In the [examples](lpn_examples/), run `make run_translate`, or run `make run_cpp`. Then cpp generated will be in _LPNCPP_. Supported examples:
        - [jpeg decoder](lpn_examples/jpeg_decoder/)
        - [darwin](lpn_examples/darwin/)
        - [protoacc](lpn_examples/pcie_topo/)
        - [menshen](lpn_examples/menshen/)
        - [vta](lpn_examples/vta/)
        - [pcie](lpn_examples/pcie_topo/)

- **Automatically generating performance interfaces:**
    - In the [examples](lpn_examples/), run `make run_pi`, or run `make run_pi_oneclass`. A `perf_interface.py` will be generated. Supported examples:
        - [jpeg decoder](lpn_examples/jpeg_decoder/)
        - [protoacc](lpn_examples/protoacc/)
        - [darwin](lpn_examples/darwin/)
        - [menshen](lpn_examples/menshen/).
    - VTA experiments are not provided, as the interface for instruction sequences gets very large and is not readable at all. If you still want to try extracting, we recommend specify concrete input (not symbolic input space), the same procedure is applied for performance interface extraction but the with no burden of handling large number of symbols that can not be summarized. 
            
- **Accuracy of generated performance interfaces:**
    - **Instructions (inside the docker):**
        1. Goto `/home/lpn/lpn_examples/jpeg_decoder/`, do `make run_pi`
        2. Goto `/home/lpn/lpn_examples/protoacc/`, do `make run_pi_oneclass`
        3. Goto `/home/lpn/lpn_examples/darwin/`, do `make run_pi`
        4. Goto `/home/experiments/perf_interface_exp`
        5. `bash run_all.sh`
    - You will see a pdf under `pdfs/` generated for the accuracy comparsion.

- **Automatically generating performance verification conditions**
    - In the [examples](lpn_examples/), run `make run_smt`. It will run example query on example input space. Supported examples:
    - [jpeg decoder](lpn_examples/jpeg_decoder/)
    - [protoacc](lpn_examples/protoacc/)

## Contact

If you have any questions or suggestions, feel free to reach out to us at (jiacheng.ma@epfl.ch).
