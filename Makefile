.PHONY:tests
tests:
	@python -m unittest discover

clean:
	@find . -name "*.pyc" -delete
