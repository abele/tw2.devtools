.PHONY: clean-pyc clean-env test develop

WD := $(shell pwd)
VIRTUAL_ENV := $(WD)/env
PYTHON := $(VIRTUAL_ENV)/bin/python

all: clean-pyc env develop test

develop: $(PYTHON) $(VIRTUAL_ENV)/lib/python*/site-packages/tw2.devtools.egg-link
$(VIRTUAL_ENV)/lib/python*/site-packages/tw2.devtools.egg-link:
	$(PYTHON) setup.py develop

$(PYTHON): env

test: $(PYTHON)
	$(PYTHON) setup.py nosetests

env:
	virtualenv -p python2.7 --no-site-packages env

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean-env:
	rm -rf $(VIRTUAL_ENV)

clean-eggs:
	rm -rf *.egg*
