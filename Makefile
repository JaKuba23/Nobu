# Nobu - Makefile for common development tasks
# Usage: make <target>

.PHONY: help install install-dev test lint format type-check clean build all

# Default target
help:
	@echo "Nobu Development Commands"
	@echo "========================="
	@echo ""
	@echo "  make install      Install package in development mode"
	@echo "  make install-dev  Install with development dependencies"
	@echo "  make test         Run test suite with pytest"
	@echo "  make lint         Run flake8 linter"
	@echo "  make format       Format code with black and isort"
	@echo "  make type-check   Run mypy type checker"
	@echo "  make clean        Remove build artifacts and cache"
	@echo "  make build        Build distribution packages"
	@echo "  make all          Run lint, type-check, and tests"
	@echo ""

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=nobu --cov-report=term-missing --cov-report=html

# Linting
lint:
	flake8 nobu/ tests/ --max-line-length=88 --extend-ignore=E203

# Formatting
format:
	black nobu/ tests/
	isort nobu/ tests/

# Type checking
type-check:
	mypy nobu/ --ignore-missing-imports

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Build distribution
build: clean
	python -m build

# Run all checks
all: lint type-check test
	@echo "All checks passed!"

# Quick scan example (for testing)
demo:
	python -m nobu profile fast --target 127.0.0.1

