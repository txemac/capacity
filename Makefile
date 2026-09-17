# Makefile

.PHONY: help pre-commit-install pre-commit clean install-producer run-producer test-producer install-consumer run-consumer test-consumer

MODEL_ID ?= google/bert_uncased_L-2_H-128_A-2
MODEL_FILE ?= google-bert_uncased_L-2_H-128_A-2.tar.gz.enc

help:
	@echo "Available commands:"
	@echo "  make pre-commit-install   - Install pre-commit hooks"
	@echo "  make pre-commit           - Run linters and formatters"
	@echo "  make clean                - Remove temporary files"
	@echo "  make tests                - Run tests with pytest"
	@echo " "
	@echo " Producer:"
	@echo "  make install-producer     - Install producer project dependencies with uv"
	@echo "  make run-producer         - Run the producer"
	@echo "  make test-producer        - Run producer tests with pytest"
	@echo " "
	@echo " Consumer:"
	@echo "  make install-consumer     - Install consumer project dependencies with uv"
	@echo "  make run-consumer         - Run the consumer"
	@echo "  make test-consumer        - Run consumer tests with pytest"


pre-commit-install:
	uv run pre-commit install

pre-commit: pre-commit-producer pre-commit-consumer

clean:
	find producer consumer -type d \( -name "__pycache__" -o -name ".pytest_cache" \) -prune -exec rm -rf {} +

test: test-producer test-consumer

# producer
pre-commit-producer:
	cd producer && uv run pre-commit run --all-files --verbose

install-producer:
	cd producer && uv sync

run-producer:
	cd producer && uv run python src/main.py --model "$(MODEL_ID)"

test-producer:
	cd producer && uv run pytest --verbose

# consumer
pre-commit-consumer:
	cd consumer && uv run pre-commit run --all-files --verbose

install-consumer:
	cd consumer && uv sync

run-consumer:
	cd consumer && uv run python src/main.py --model "$(MODEL_FILE)"

test-consumer:
	cd consumer && uv run pytest --verbose
