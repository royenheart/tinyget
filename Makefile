all: clean lint build uninstall install test

NO_LINT ?= OFF

build:
	python -m build --wheel

clean:
	rm -rf dist

install:
	pip install dist/*.whl

uninstall:
	@if pip freeze | grep -q tinyget; then \
		pip uninstall -y tinyget; \
	else \
		echo "tinyget not installed."; \
	fi

.PHONY: test
test:
	pytest

lint:
ifeq ($(NO_LINT),OFF)
	flake8 ./tinyget --count --show-source --statistics
	black ./tinyget --check --verbose
endif
