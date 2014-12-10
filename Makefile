# Makefile for WeeWX Graphite Extension.
#
# Source:: https://github.com/ampledata/weewx_graphite
# Author:: Greg Albrecht <gba@onbeep.com>
# Copyright:: Copyright 2014 OnBeep, Inc.
# License:: Apache License, Version 2.0
#


.DEFAULT_GOAL := all
TARGETS=install.py bin/user/graphite.py


all: install

install:
	./setup.py --extension --install weewx_graphite.tar.gz


install_requirements:
	pip install -r requirements.txt

clean:
	@rm -rf *.egg* build dist *.py[oc] */*.py[co] cover doctest_pypi.cfg \
		nosetests.xml pylint.log output.xml flake8.log tests.log \
		test-result.xml htmlcov fab.log .coverage

pep8: install_requirements
	flake8 --max-complexity 12 --exit-zero $(TARGETS)

lint: install_requirements
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
		-r n $(TARGETS) || exit 0

test: lint pep8
