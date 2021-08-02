mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(patsubst %/,%,$(dir $(mkfile_path)))

test:
	PYTHONPATH=${current_dir}/tmetrics_wrapper/ pytest