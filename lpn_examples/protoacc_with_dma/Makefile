default: copy_files run_example

# Target for copying files
copy_files:
	@echo "Copying protoacc lpn files..."
	@cp -r ../../lpn_family/accel_lib/protoacc/no_guard_threshold/lpn_def lpn_def/
	@mkdir -p LPNCPP/
	@cp -r ../../lpntools/cpplib/simlib/sim_makefile LPNCPP/Makefile
	@cp -r ../../lpntools/cpplib/simlib/place_transition.* LPNCPP/

copy_files_for_symbex:	
	@mkdir -p LPNCPP_KLEE/
	@cp -r ../../lpntools/cpplib/symbexlib/* LPNCPP_KLEE/
	@mkdir -p LPNCPP_KLEE/classes

# Target for running the example
run_example: clean copy_files
	@echo "Run example instructions"
	@python3 run_sim.py -b bench2

run_translate: clean copy_files
	@echo "Run translation"
	@python3 run_translate.py -b bench2
	@make -C LPNCPP/ -f Makefile

run_cpp: run_translate
	@echo "Run cpp simulation"
	@./LPNCPP/lpnsim reference.insns

run_pi : clean copy_files copy_files_for_symbex
	@echo "Run perf interface generation"
	@echo "Run symbex to find input classes"
	@python3 run_pi.py -b bench1 -s True
	@CPATH= make -C LPNCPP_KLEE/ -f makefile klee
	@echo "Run generation of perf interface based on input classes"
	@python3 run_pi.py -b bench1 -pi True	


run_smt : clean copy_files copy_files_for_symbex
	@echo "Remove old classes"
	@rm -rf LPNCPP_KLEE/classes/*
	@echo "Run perf interface generation"
	@echo "Run symbex to find input classes"
	@python3 run_smt.py -s True
	@CPATH= make -C LPNCPP_KLEE/ -f makefile klee
	@echo "Run smt based on input classes"
	@python3 run_smt.py -smt True	

run_pi_oneclass: clean copy_files
	@echo "Run perf interface generation of google hyperprotobench"
	@mkdir -p tmp/classes
	@rm -rf tmp/classes/*
	@python3 run_pi_oneclass.py -b bench0
	@python3 run_pi_oneclass.py -b bench1
	@python3 run_pi_oneclass.py -b bench2
	@python3 run_pi_oneclass.py -b bench3
	@python3 run_pi_oneclass.py -b bench4
	@python3 run_pi_oneclass.py -b bench5
	@echo "Run generation of perf interface based on input classes"
	@python3 run_pi_oneclass.py -pi True


# Target for cleaning up
clean:
	@echo "Cleaning up protoacc lpn files..."
	@rm -rf lpn_def/
	@rm -rf LPNCPP/
	@rm -rf LPNCPP_KLEE/
	@rm -rf exprs/
	@rm -rf perf_interface.py

.PHONY: default copy_files run_example run_translate run_cpp clean

