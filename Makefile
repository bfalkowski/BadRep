.PHONY: help install install-dev test test-cov lint format type-check clean quality-check

help:  ## Show this help message
	@echo "ReviewLab Development Commands"
	@echo "=============================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev]"

test:  ## Run all tests
	python -m pytest tests/ -v

test-cov:  ## Run tests with coverage report
	python -m pytest tests/ --cov=core --cov=cli --cov-report=term-missing --cov-report=html

test-fast:  ## Run tests quickly (no coverage)
	python -m pytest tests/ -q --tb=short

lint:  ## Run flake8 linting
	flake8 core/ cli/ tests/

format:  ## Format code with black and isort
	black core/ cli/ tests/
	isort core/ cli/ tests/

format-check:  ## Check if code is properly formatted
	black --check core/ cli/ tests/
	isort --check-only core/ cli/ tests/

type-check:  ## Run mypy type checking
	mypy core/ cli/

quality-check: format-check lint type-check test  ## Run all quality checks

clean:  ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf ground_truth/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install-hooks:  ## Install pre-commit hooks
	pre-commit install

update-hooks:  ## Update pre-commit hooks
	pre-commit autoupdate

run-hooks:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

benchmark:  ## Run performance benchmarks
	python -m pytest tests/ --benchmark-only

html-report:  ## Generate HTML test report
	python -m pytest tests/ --html=reports/test_report.html --self-contained-html

ci: quality-check  ## Run CI pipeline locally
