SRC=rogue_scores
BIN_TOOLS=venv/bin

PIP=$(BIN_TOOLS)/pip
PYTHON=$(BIN_TOOLS)/python

COVERFILE:=.coverage
COVERAGE_REPORT:=report -m

PY_VERSION:=$(subst ., ,$(shell python --version 2>&1 | cut -d' ' -f2))
PY_VERSION_MAJOR:=$(word 1,$(PY_VERSION))
PY_VERSION_MINOR:=$(word 2,$(PY_VERSION))
PY_VERSION_SHORT:=$(PY_VERSION_MAJOR).$(PY_VERSION_MINOR)

ifdef TRAVIS_PYTHON_VERSION
PY_VERSION_SHORT:=$(TRAVIS_PYTHON_VERSION)
endif

.PHONY: check check-versions stylecheck covercheck docs

default: deps check-versions

deps: venv
	$(PIP) install -qr requirements.txt
ifeq ($(PY_VERSION_SHORT),2.6)
	$(PIP) install -q unittest2
endif
ifneq ($(PY_VERSION_SHORT),3.3)
ifneq ($(PY_VERSION_SHORT),3.4)
	$(PIP) install -q wsgiref==0.1.2
endif
endif

venv:
	virtualenv $@

check:
	$(PYTHON) tests/test.py

check-versions:
	$(BIN_TOOLS)/tox

stylecheck:
	$(BIN_TOOLS)/pep8 $(SRC)

covercheck:
	$(BIN_TOOLS)/coverage run --source=$(SRC) tests/test.py
	$(BIN_TOOLS)/coverage $(COVERAGE_REPORT)

clean:
	find . -name '*~' -delete
	rm -f $(COVERFILE)
	make -C docs clean

publish: stylecheck check-versions
	cp README.rst README
	$(PYTHON) setup.py sdist upload
	rm -f README

docs:
	make -C docs html
