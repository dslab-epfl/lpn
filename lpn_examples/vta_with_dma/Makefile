default: copy_files run_example

# Target for copying files
copy_files:
	@echo "Copying vta lpn files..."
	@cp -r ../../lpn_family/accel_lib/vta/normal/ lpn_def/
	@mkdir -p LPNCPP/
	@cp -r ../../lpn_family/accel_lib/vta/normal/LPNCPP/setup.hh LPNCPP/
	@cp -r ../../lpn_family/accel_lib/vta/normal/LPNCPP/setup.hh LPNCPP/
	@cp -r ../../lpntools/cpplib/simlib/sim_makefile LPNCPP/Makefile
	@cp -r ../../lpntools/cpplib/simlib/place_transition.* LPNCPP/

# Target for running the example
run_example: clean copy_files
	@echo "Run example instructions"
	@python3 run_sim.py -b reference.insns

run_translate: clean copy_files
	@echo "Run translation"
	@python3 run_translate.py -b reference.insns
	@make -C LPNCPP/ -f Makefile

run_cpp: run_translate
	@echo "Run cpp simulation"
	@./LPNCPP/lpnsim reference.insns

run_visual: run_visual
	@echo "Run visualization"
	@python3 run_visual.py -b reference.insns


# Target for cleaning up
clean:
	@echo "Cleaning up vta lpn files..."
	@rm -rf lpn_def/
	@rm -rf LPNCPP/

.PHONY: default copy_files run_example run_translate run_cpp clean

