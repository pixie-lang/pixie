all: help

EXTERNALS=../externals

PYTHON ?= pypy
PYTHONPATH=$$PYTHONPATH:$(EXTERNALS)/pypy

help:
	@echo "make help              - display this message"
	@echo "make run               - run the compiled interpreter"
	@echo "make run_interactive   - run without compiling (slow)"
	@echo "make build_with_jit    - build with jit enabled"
	@echo "make build_no_jit      - build without jit"

build_with_jit: fetch_externals
	$(PYTHON) $(EXTERNALS)/pypy/rpython/bin/rpython --opt=jit --continuation --no-shared target.py

build_no_jit: fetch_externals
	$(PYTHON) $(EXTERNALS)/pypy/rpython/bin/rpython --continuation --no-shared target.py

fetch_externals: $(EXTERNALS)/pypy

$(EXTERNALS)/pypy:
	mkdir $(EXTERNALS)
	cd $(EXTERNALS)
	curl https://bitbucket.org/pypy/pypy/get/default.tar.bz2 >  pypy.tar.bz2
	mkdir pypy
	cd pypy
	tar -jxf ../pypy.tar.bz2 --strip-components=1

run:
	./pixie-vm

run_interactive:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) target.py

run_built_tests: pixie-vm
	./pixie-vm run-tests.pxi

run_interpreted_tests: target.py
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) target.py run-tests.pxi

run_python_tests:
	PYTHONPATH=$(PYTHONPATH) nosetests
