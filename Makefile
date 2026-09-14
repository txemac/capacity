# Makefile

.PHONY: help install test pre-commit-install pre-commit run-producer clean

MODEL_ID ?= google/bert_uncased_L-2_H-128_A-2

help:
	@echo "Available commands:"
	@echo "  make install              - Install project dependencies with uv"
	@echo "  make test                 - Run tests with pytest"
	@echo "  make pre-commit-install   - Install pre-commit hooks"
	@echo "  make pre-commit           - Run linters and formatters"
	@echo "  make clean                - Remove temporary files"
	@echo "  make run-producer         - Run the producer"

install:
	uv sync

test:
	uv run pytest --verbose

pre-commit-install:
	uv run pre-commit install

pre-commit:
	uv run pre-commit run --all-files --verbose

clean:
	rm -rf __pycache__ .pytest_cache

run-producer:
	uv run python producer/src/main.py --model "$(MODEL_ID)"
