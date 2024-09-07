all: clean lint build pre-test uninstall install post-test

NO_LINT ?= OFF
NO_TEST ?= OFF

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

.PHONY: pre-test
pre-test:
ifeq ($(NO_TEST),OFF)
	bash -c "export PATH=$(PATH);PYTHONPATH=. pytest -k 'not test_cli'"
endif

.PHONY: post-test
post-test:
ifeq ($(NO_TEST),OFF)
	bash -c "export PATH=$(PATH);pytest -k 'test_cli'"
endif

lint:
ifeq ($(NO_LINT),OFF)
	flake8 ./tinyget --count --show-source --statistics
	black ./tinyget --check --verbose
endif
