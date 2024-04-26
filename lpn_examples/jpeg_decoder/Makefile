default: copy_files run_example

# Target for copying files
copy_files:
	@echo "Copying jpeg_decoder lpn files..."
	@cp -r ../../lpn_family/accel_lib/jpeg_decoder/no_guard_threshold/lpn_def lpn_def/
	@cp -r ../../lpn_family/accel_lib/jpeg_decoder/no_guard_threshold/test_imgs .
	@mkdir -p LPNCPP/
	@cp -r ../../lpntools/cpplib/simlib/sim_makefile LPNCPP/Makefile
	@cp -r ../../lpntools/cpplib/simlib/place_transition.* LPNCPP/

copy_files_for_symbex:	
	@mkdir -p LPNCPP_KLEE/
	@cp -r ../../lpntools/cpplib/symbexlib/* LPNCPP_KLEE/
	@mkdir -p LPNCPP_KLEE/classes

# Target for running the example
run_example: copy_files
	@echo "Run example instructions"
	@python3 run_sim.py -img test_imgs/420/33.jpg

run_translate: copy_files
	@echo "Run translation"
	@python3 run_translate.py -img test_imgs/420/33.jpg
	@make -C LPNCPP/ -f Makefile

run_cpp: run_translate
	@echo "Run cpp simulation"
	@./LPNCPP/lpnsim reference.insns

run_pi : copy_files copy_files_for_symbex
	@rm -rf LPNCPP_KLEE/classes/*
	@echo "Run perf interface generation"
	@echo "Run symbex to find input classes on 12 blocks chunk"
	@python3 run_pi.py -nb 12 -s True
	@CPATH= make -C LPNCPP_KLEE/ -f makefile klee
	@echo "Run generation of perf interface based on input classes"
	@python3 run_pi.py -nb 12 -pi True	


run_pi_oneclass : copy_files copy_files_for_symbex
	@rm -rf LPNCPP_KLEE/classes/*
	@echo "Run perf interface generation"
	@echo "Run generation of perf interface based on input classes on 12 blocks chunk"
	@python3 run_pi_oneclass.py -nb 12 -s True -pi True	

run_smt : copy_files copy_files_for_symbex
	@echo "Remove old classes"
	@rm -rf LPNCPP_KLEE/classes/*
	@echo "Run perf interface generation"
	@echo "Run symbex to find input classes"
	@python3 run_smt.py -nb 18 -s True
	@CPATH= make -C LPNCPP_KLEE/ -f makefile klee
	@echo "Run smt based on input classes"
	@python3 run_smt.py -nb 18 -smt True	

# Target for cleaning up
clean:
	@echo "Cleaning up jpeg_decoder lpn files..."
	@rm -rf lpn_def/
	@rm -rf LPNCPP/
	@rm -rf LPNCPP_KLEE/
	@rm -rf exprs/
	@rm -rf perf_interface.py

.PHONY: default copy_files run_example run_translate run_cpp clean

