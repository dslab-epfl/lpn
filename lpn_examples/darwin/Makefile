default: copy_files run_example

# Target for copying files
copy_files:
	# @echo "Copying darwin lpn files..."
	@cp -r ../../lpn_family/accel_lib/darwin/normal/lpn_def lpn_def/
	@cp -r ../../lpn_family/accel_lib/darwin/normal/test_data .
	@mkdir -p LPNCPP/
	@cp -r ../../lpntools/cpplib/simlib/sim_makefile LPNCPP/Makefile
	@cp -r ../../lpntools/cpplib/simlib/place_transition.* LPNCPP/

copy_files_for_symbex:	
	@mkdir -p tmp/classes/
	@rm -rf tmp/classes/*

# Target for running the example
run_example: copy_files
	@echo "Run example instructions"
	@python3 run_sim.py  -ref test_data/ref.0.hex -query test_data/query.0.hex

run_translate: copy_files
	@echo "Run translation"
	@python3 run_translate.py -ref test_data/ref.0.hex -query test_data/query.0.hex
	@make -C LPNCPP/ -f Makefile

run_cpp: run_translate
	@echo "Run cpp simulation"
	@./LPNCPP/lpnsim

run_pi : copy_files copy_files_for_symbex
	@echo "Run perf interface generation"
	@echo "Run generation of perf interface based on input classes"
	@python3 run_pi.py -pi True

# Target for cleaning up
clean:
	@echo "Cleaning up darwin lpn files..."
	@rm -rf lpn_def/
	@rm -rf LPNCPP/
	@rm -rf LPNCPP_KLEE/
	@rm -rf exprs/
	@rm -rf perf_interface.py
	@rm -rf test_data/

.PHONY: default copy_files run_example run_translate run_cpp clean

