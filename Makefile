.PHONY: clean pep8 tests tests_ci run

CWD="`pwd`"
PROJECT_NAME = swiftsuru
PROJECT_HOME ?= $(CWD)


clean:
	@find . -name "*.pyc" -delete
	@find . -name "*.~" -delete

pep8:
	@-pep8 $(PROJECT_HOME) --ignore=E501,E126,E127,E128

tests: clean pep8
	@py.test --cov-config .coveragerc --cov $(PROJECT_HOME) --cov-report term-missing

tests_ci: clean pep8
	@py.test

run: clean
	@python -m swiftsuru
