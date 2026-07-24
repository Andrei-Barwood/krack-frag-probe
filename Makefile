.PHONY: help install install-dev check lint typecheck test test-cov format clean build run-list dry-run

PYTHON ?= python3
PKG := krack-frag-probe

help:
	@echo "krack-frag-probe developer targets"
	@echo "  make install       Install package (editable)"
	@echo "  make install-dev   Install with dev extras"
	@echo "  make check         lint + typecheck + unit tests"
	@echo "  make lint          Run ruff"
	@echo "  make typecheck     Run mypy"
	@echo "  make test          Run pytest"
	@echo "  make test-cov      Run pytest with coverage"
	@echo "  make format        Auto-format with ruff"
	@echo "  make build         Build sdist/wheel"
	@echo "  make run-list      List regression tests"
	@echo "  make dry-run       Dry-run all tests (no hardware)"
	@echo "  make clean         Remove build artifacts"

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

lint:
	$(PYTHON) -m ruff check src tests
	$(PYTHON) -m ruff format --check src tests

format:
	$(PYTHON) -m ruff check --fix src tests
	$(PYTHON) -m ruff format src tests

typecheck:
	$(PYTHON) -m mypy src

test:
	$(PYTHON) -m pytest tests

test-cov:
	$(PYTHON) -m pytest tests --cov=krack_frag_probe --cov-report=term-missing

check: lint typecheck test

build:
	$(PYTHON) -m pip install build
	$(PYTHON) -m build

run-list:
	$(PYTHON) -m krack_frag_probe list-tests

dry-run:
	$(PYTHON) -m krack_frag_probe run \
		--iface mon0 \
		--bssid aa:bb:cc:dd:ee:ff \
		--test all \
		--dry-run \
		--yes-i-understand

clean:
	rm -rf build dist *.egg-info src/*.egg-info .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
