default: copy_files run_example

# Target for copying files
copy_files:
	@echo "Copying vta lpn files..."
	@cp -r ../../lpn_family/accel_lib/pcie_topo/lpn_def/ lpn_def/
	@mkdir -p LPNCPP/
	@cp -r ../../lpntools/cpplib/simlib/sim_makefile LPNCPP/Makefile
	@cp -r ../../lpntools/cpplib/simlib/place_transition.* LPNCPP/

# Target for running the example
run_example: clean_no_cpp copy_files
	@echo "Run example instructions"
	@python3 run_sim.py -t 256

run_translate: clean_no_cpp copy_files
	@echo "Run translation"
	@python3 run_translate.py -t 256
	@make -C LPNCPP/ -f Makefile

run_cpp: run_translate
	@echo "Run cpp simulation"
	@./LPNCPP/lpnsim

# Target for cleaning up
clean_no_cpp:
	@echo "Cleaning up vta lpn files..."
	@rm -rf lpn_def/

clean:
	@echo "Cleaning up vta lpn files..."
	@rm -rf lpn_def/
	@rm -rf LPNCPP/

.PHONY: default copy_files run_example run_translate run_cpp clean

