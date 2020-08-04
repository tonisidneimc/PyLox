PYTHON = python3
PKGDIR = ./lox
TESTDIR= ./tests
TESTFILE = t1.plox

.PHONY: clean-build

# If the first argument is "run"...
ifeq (run,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "run"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

clean-build:
	@find $(PKGDIR) -name '*.pyc' -delete
	@find $(PKGDIR) -name '__pycache__' -delete
	-@rm -rf __pycache__

help:
	@echo "[HELP] PyLox usage: "
	@echo " make check        to check python version (>= 3.5 required)"
	@echo " make repl         to run PyLox in a prompt mode"
	@echo " make run [path]   to run a .lox file located at path"
	@echo " make test         to run a simple test case"
	@echo " make help         show this help message"

clean: clean-build

check:
	$(PYTHON) --version

test: clean-build check
	@echo "running test script"

	$(PYTHON) PyLox.py ${TESTDIR}/${TESTFILE}

repl:
	$(PYTHON) PyLox.py

run:
	$(PYTHON) PyLox.py $(RUN_ARGS)
	
