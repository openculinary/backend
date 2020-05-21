.PHONY: build lint tests

build: lint tests

lint:
	flake8

tests:
	pytest tests
