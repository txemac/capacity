# Makefile

.PHONY: help pre-commit-install pre-commit clean test
.PHONY: install-producer run-producer run-producer-k8s test-producer build-producer
.PHONY: install-consumer run-consumer test-consumer build-consumer
.PHONY: load-consumer-k8s create-model-secret create-signing-public-key
.PHONY: run-consumer-k8s run-k8s logs-consumer-k8s build

MODEL_ID ?= google/bert_uncased_L-2_H-128_A-2
MODEL_FILE ?= google-bert_uncased_L-2_H-128_A-2.tar.gz.enc

help:
	@echo "Available commands:"
	@echo "  make pre-commit-install   			- Install pre-commit hooks"
	@echo "  make pre-commit           			- Run linters and formatters"
	@echo "  make clean                			- Remove temporary files"
	@echo "  make test                 			- Run all tests with pytest"
	@echo "  make build                			- Build all Docker images"
	@echo " "
	@echo " Producer:"
	@echo "  make install-producer     			- Install producer project dependencies with uv"
	@echo "  make run-producer         			- Run the producer with the local encryption key"
	@echo "  make run-producer-k8s     			- Run the producer with a new encryption key"
	@echo "  make test-producer        			- Run producer tests with pytest"
	@echo "  make build-producer       			- Build producer Docker image"
	@echo " "
	@echo " Consumer:"
	@echo "  make install-consumer     			- Install consumer project dependencies with uv"
	@echo "  make run-consumer         			- Run the consumer with the local encryption key"
	@echo "  make test-consumer        			- Run consumer tests with pytest"
	@echo "  make build-consumer       			- Build consumer Docker image"
	@echo "  make load-consumer-k8s    			- Load Consumer image into Docker Desktop Kubernetes"
	@echo " "
	@echo " Kubernetes:"
	@echo "  make create-model-secret  			- Create/update the model encryption Secret"
	@echo "  make create-signing-public-key		- Create/update the signing public key ConfigMap"
	@echo "  make run-consumer-k8s     			- Run the Consumer Kubernetes Job"
	@echo "  make run-k8s              			- Run the complete Kubernetes flow"
	@echo "  make logs-consumer-k8s    			- Show logs from the latest Consumer Kubernetes Pod"

pre-commit-install:
	uv run pre-commit install

pre-commit: pre-commit-producer pre-commit-consumer

clean:
	find producer consumer -type d \( -name "__pycache__" -o -name ".pytest_cache" \) -prune -exec rm -rf {} +

test: test-producer test-consumer

build: build-producer build-consumer

# Producer
pre-commit-producer:
	cd producer && uv run pre-commit run --all-files --verbose

install-producer:
	cd producer && uv sync

run-producer:
	cd producer && uv run python src/main.py --model "$(MODEL_ID)"

run-producer-k8s:
	cd producer && uv run python src/main.py --model "$(MODEL_ID)" --generate-key

test-producer:
	cd producer && uv run pytest --verbose

build-producer:
	docker build -f producer/Dockerfile -t capacity-producer .

# Consumer
pre-commit-consumer:
	cd consumer && uv run pre-commit run --all-files --verbose

install-consumer:
	cd consumer && uv sync

run-consumer:
	cd consumer && uv run python src/main.py --model "$(MODEL_FILE)"

test-consumer:
	cd consumer && uv run pytest --verbose

build-consumer:
	docker build -f consumer/Dockerfile -t capacity-consumer .

load-consumer-k8s:
	docker save capacity-consumer:latest | docker exec -i desktop-control-plane ctr -n k8s.io images import -

# Kubernetes
create-model-secret:
	kubectl create secret generic model-encryption-key \
		--from-file=KEY_BASE64=producer/output/.key \
		--dry-run=client \
		-o yaml | kubectl apply -f -

create-signing-public-key:
	kubectl create configmap signing-public-key \
		--from-file=signing-public-key.pem=producer/output/signing-public-key.pem \
		--dry-run=client \
		-o yaml | kubectl apply -f -

run-consumer-k8s:
	sed 's|$${MODEL_FILE}|$(MODEL_FILE)|g' kubernetes/consumer.yaml | kubectl create -f -

run-k8s: run-producer-k8s create-model-secret create-signing-public-key build-consumer load-consumer-k8s run-consumer-k8s

logs-consumer-k8s:
	kubectl logs $$(kubectl get pods -l app=capacity-consumer --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')
