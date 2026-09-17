# Makefile

.PHONY: help pre-commit-install pre-commit clean install-producer run-producer test-producer

MODEL_ID ?= google/bert_uncased_L-2_H-128_A-2

help:
	@echo "Available commands:"
	@echo "  make pre-commit-install   - Install pre-commit hooks"
	@echo "  make pre-commit           - Run linters and formatters"
	@echo "  make clean                - Remove temporary files"
	@echo "  make install-producer     - Install producer project dependencies with uv"
	@echo "  make run-producer         - Run the producer"
	@echo "  make test-producer        - Run tests with pytest"

pre-commit-install:
	uv run pre-commit install

pre-commit:
	uv run pre-commit run --all-files --verbose

clean:
	rm -rf __pycache__ .pytest_cache

install-producer:
	cd producer && uv sync

run-producer:
	cd producer && uv run python src/main.py --model "$(MODEL_ID)"

test-producer:
	cd producer && uv run pytest --verbose
