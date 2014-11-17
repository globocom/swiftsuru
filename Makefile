.PHONY:tests
tests:
	@-pep8 swiftsuru/ --ignore=E501,E126,E127,E128
	@python -m unittest discover

clean:
	@find . -name "*.pyc" -delete

run:
	@python -m swiftsuru
