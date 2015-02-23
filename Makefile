all: help

EXTERNALS=../externals

PYTHON ?= python
PYTHONPATH=$$PYTHONPATH:$(EXTERNALS)/pypy

COMMON_BUILD_OPTS?=--thread --no-shared --gcrootfinder=shadowstack
JIT_OPTS?=--opt=jit
TARGET_OPTS?=target.py

help:
	@echo "make help                   - display this message"
	@echo "make run                    - run the compiled interpreter"
	@echo "make run_interactive        - run without compiling (slow)"
	@echo "make build_with_jit         - build with jit enabled"
	@echo "make build_no_jit           - build without jit"
	@echo "make fetch_externals	   - download and unpack external deps"

find_externals_name:
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) find_externals_name.py

build_with_jit: fetch_externals
	$(PYTHON) $(EXTERNALS)/pypy/rpython/bin/rpython $(COMMON_BUILD_OPTS) --opt=jit target.py

build_no_jit: fetch_externals
	$(PYTHON) $(EXTERNALS)/pypy/rpython/bin/rpython $(COMMON_BUILD_OPTS) target.py

build_preload_with_jit: fetch_externals
	$(PYTHON) $(EXTERNALS)/pypy/rpython/bin/rpython $(COMMON_BUILD_OPTS) --opt=jit target_preload.py 2>&1 >/dev/null | grep -v 'WARNING'

build_preload_no_jit: fetch_externals
	$(PYTHON) $(EXTERNALS)/pypy/rpython/bin/rpython $(COMMON_BUILD_OPTS) target_preload.py

build: fetch_externals
	$(PYTHON) $(EXTERNALS)/pypy/rpython/bin/rpython $(COMMON_BUILD_OPTS) $(JIT_OPTS) $(TARGET_OPTS) 

fetch_externals: $(EXTERNALS)/pypy $(EXTERNALS)/binaries

$(EXTERNALS)/binaries:
	mkdir $(EXTERNALS); \
	echo https://github.com/pixie-lang/external-deps/releases/download/1.0/`uname -s`-`uname -m`.tar.bz2
	curl -L https://github.com/pixie-lang/external-deps/releases/download/1.0/`uname -s`-`uname -m`.tar.bz2 > $(EXTERNALS)/externals.tar.bz2
	cd $(EXTERNALS) && tar -jxf externals.tar.bz2 


$(EXTERNALS)/pypy:
	mkdir $(EXTERNALS); \
	cd $(EXTERNALS); \
	curl https://bitbucket.org/pypy/pypy/get/default.tar.bz2 >  pypy.tar.bz2; \
	mkdir pypy; \
	cd pypy; \
	tar -jxf ../pypy.tar.bz2 --strip-components=1

run:
	./pixie-vm

run_interactive:
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) target.py -l ../externals/externals/lib

run_built_tests: pixie-vm
	./pixie-vm -l ../externals/externals/lib -l ../externals/externals/include run-tests.pxi

run_interpreted_tests: target.py
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) target.py run-tests.pxi

compile_tests:
	find "tests" -name "*.pxi" | xargs -L1 ./pixie-vm -l "tests" -c

clean_pxic:
	find * -name "*.pxic" | xargs rm
