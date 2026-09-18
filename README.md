# Confidential ML Model Distribution PoC

## Summary

Design and implement a proof-of-concept for a confidential LLM model delivery pipeline. The
task has three progressive layers: Layer 1 is required and Layer 2 and 3 are optional. All layers
share the same two-part structure: a Producer that encrypts and publishes a model, and a
Consumer that retrieves and decrypts it. No confidential hardware is required at any layer.

## Layer 1 (Required): Encrypted Model Distribution in Kubernetes

Implement a basic confidential model delivery pipeline running in a Kubernetes environment.

### Producer

1. Select a small open model from Hugging Face (e.g. a small BERT).
2. Encrypt the model (free to choose any tool/library).
3. Push the encrypted artifact to Hugging Face Hub.
4. Store the decryption key as a Kubernetes Secret, accessible to the consumer workload.

### Consumer

1. Deploy a Kubernetes pod that mounts the decryption key from the Kubernetes Secret.
2. Download the encrypted artifact from Hugging Face Hub.
3. Decrypt the model.
4. Load the model.

## Layer 2 (Optional): Model Signing & Verification

Extend Layer 1 by adding a signing step to the producer and a verification step to the consumer,
ensuring the model artifact was not tampered with between publication and use.

### Additional steps on top of Layer 1

1. Generate an asymmetric key pair (free to choose any tool/library).
2. Sign the encrypted artifact with the private key during the producer phase.
3. Publish the signature alongside the artifact.
4. In the consumer, verify the signature using the public key before decryption takes place
   (abort if verification fails).

## Layer 3 (Optional): Attested Key Release via Kata+CoCo

Extend the pipeline by replacing the Kubernetes Secret with attested key retrieval using
Confidential Containers in development mode. The consumer no longer trusts the host for key
delivery, so the decryption key is only released after an attestation. This layer can be
implemented on top of Layer 1 alone or combined with Layer 2 for the full confidential pipeline
(encrypt + sign + attest).

### Additional steps on top of Layer 1

1. Deploy the CoCo operator and Trustee KBS on the cluster using the
   `kata-qemu-coco-dev` runtime class.
2. Store the decryption key in KBS via `kbs-client set-resource` under a defined resource
   path (e.g. `default/key/my-model`) instead of a Kubernetes Secret.
3. Configure a permissive resource policy in KBS allowing key release to sample TEE
   attestation.
4. Run the consumer pod with the KBS address configured via the `agent.aa_kbc_params` parameter
   annotation.
5. Fetch the decryption key from KBS through the Confidential Data Hub (CDH) endpoint at
   `127.0.0.1:8006/cdh/resource/...`, relying on the full attestation flow.

## General Notes

- Layers 2 and 3 are independent: a candidate may implement Layer 1 + Layer 3 (attested
  delivery without signing) or Layer 1 + Layer 2 + Layer 3 (the full stack).
- The choice of model, encryption library, and tooling is left to the candidate (justification
  might be asked during the discussion of the solution).

## Deliverables

A public Git repository containing:

- Dockerfiles for the producer and consumer workloads.
- Kubernetes manifests for all workloads (Pods, Secrets, or any other resources used).
- A README covering prerequisites, how to build and deploy the full pipeline, and how to verify
  each layer works.

Reference: [Confidential Containers without confidential hardware](https://confidentialcontainers.org/blog/2024/12/03/confidential-containers-without-confidential-hardware/)


# SOLUTION

## 📖 Table of Contents

- [🏗️ Solution Overview](#️-solution-overview)
- [🔐 Encryption Approach](#-encryption-approach)
- [🤗 Model Selection](#-model-selection)
- [📦 Artifact Packaging](#-artifact-packaging)
- [⚙️ Producer](#️-producer)
- [👤 Consumer](#-consumer)
- [🔑 Key Management](#-key-management)
- [☸️ Kubernetes](#️-kubernetes)
- [🐳 Docker](#-docker)
- [🧪 Testing Strategy](#-testing-strategy)
- [🗂️ Repository Structure](#-repository-structure)
- [🚀 Local Installation](#-local-installation)
- [▶️ Running the Pipeline](#️-running-the-pipeline)
- [🛡️ Security Considerations](#️-security-considerations)
- [🛠️ Contribution Guide](#️-contribution-guide)

## 🏗️ Solution Overview

The solution implements the required Layer 1 model distribution pipeline using two independent applications:

```text
                    ┌─────────────────────┐
                    │      Producer       │
                    │---------------------│
                    │ Download model      │
                    │ Package model       │
                    │ Generate key        │
                    │ Encrypt artifact    │
                    └──────────┬──────────┘
                               │
                               │ Encrypted artifact
                               ▼
                    ┌─────────────────────┐
                    │  Hugging Face Hub   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Consumer Pod     │
                    │---------------------│
                    │ Read mounted key    │
                    │ Download artifact   │
                    │ Decrypt artifact    │
                    │ Extract model       │
                    │ Load model          │
                    └─────────────────────┘
                               ▲
                               │
                    ┌──────────┴──────────┐
                    │ Kubernetes Secret   │
                    │ AES encryption key  │
                    └─────────────────────┘
```

The Producer prepares and publishes the encrypted model artifact.

The Consumer retrieves the encrypted artifact from Hugging Face Hub and obtains the decryption
key from a Kubernetes Secret mounted as a file.

The complete Layer 1 flow has been verified end to end on Docker Desktop Kubernetes.

## 🔐 Encryption Approach

The model artifact is encrypted using **AES-256-GCM**, an authenticated symmetric encryption
scheme.

AES-GCM was selected because it provides:

- **Confidentiality** ... the encrypted artifact does not expose the model contents.
- **Integrity** ... modifications to the encrypted artifact are detected during decryption.
- Authenticated encryption through a mature cryptographic library.

The encryption uses a randomly generated 256-bit key.

A new random 12-byte nonce is generated for each encryption operation. The nonce is not secret
and is stored together with the encrypted data.

The encrypted file therefore contains:

```text
┌──────────────┬──────────────────────┬─────────────────┐
│    Nonce     │     Ciphertext       │  GCM Auth Tag   │
│   12 bytes   │    encrypted data    │     16 bytes    │
└──────────────┴──────────────────────┴─────────────────┘
```

For Layer 1, the AES key is distributed separately through a Kubernetes Secret.

### Why not RSA?

RSA was not selected to encrypt the model directly because asymmetric encryption is not designed
for efficiently encrypting large files.

A hybrid encryption architecture could use AES for the model and asymmetric cryptography for
protecting the AES key. For this PoC, the key is distributed through a Kubernetes Secret, so
adding asymmetric key wrapping would introduce complexity without being required.

## 🤗 Model Selection

`google/bert_uncased_L-2-H-128-A-2` was selected as the reference model.

It is a compact BERT model with 4.43 million parameters and a model size of approximately
17.7 MB in Safetensors format.

The model was intentionally selected to be small because model size is not relevant to the
security properties being demonstrated.

A smaller model provides:

- Faster downloads.
- Lower resource requirements.
- Faster encryption and packaging.
- Faster test and development cycles.

The default model is defined in the root `Makefile`:

```makefile
MODEL_ID ?= google/bert_uncased_L-2-H-128-A-2
```

It can be overridden:

```bash
make run-producer MODEL_ID=distilbert/distilbert-base-uncased
```

## 📦 Artifact Packaging

A Hugging Face model normally consists of multiple files.

The model directory is first packaged into a single `tar.gz` archive and then encrypted:

```text
Model directory
      │
      ▼
 model.tar.gz
      │
      ▼
 AES-256-GCM
      │
      ▼
model.tar.gz.enc
```

This provides a single artifact for distribution and ensures that all model files are protected
by the same encryption operation.

For this PoC, the complete archive is read into memory during encryption and decryption. This is
acceptable for the selected small model.

A production implementation handling multi-gigabyte models should consider streaming or chunked
encryption and decryption.

## ⚙️ Producer

The Producer workflow is:

1. Download the selected model from Hugging Face.
2. Package the model files into a `tar.gz` archive.
3. Generate a cryptographically secure AES-256 key.
4. Encrypt the archive using AES-256-GCM.
5. Store the generated key temporarily in `producer/output/.key`.
6. Publish the encrypted artifact to Hugging Face Hub.

The Producer does not contain Kubernetes deployment logic. The Kubernetes Secret is created by
the deployment workflow after the Producer has generated the key.

### Local Producer

Local execution uses the configured `KEY_BASE64` value instead of generating a new key:

```bash
make run-producer
```

### Kubernetes Producer

The Kubernetes flow generates a fresh key:

```bash
make run-producer-k8s
```

The generated key is stored temporarily in:

```text
producer/output/.key
```

## 👤 Consumer

The Consumer retrieves the protected model and loads it locally.

The Kubernetes workflow is:

```text
Kubernetes Secret
       │
       ▼
mounted key file
       │
Hugging Face Hub
       │
       ▼
model.tar.gz.enc
       │
       ▼
download
       │
       ▼
decrypt
       │
       ▼
model.tar.gz
       │
       ▼
extract
       │
       ▼
model files
       │
       ▼
load model
```

The Consumer reads the encryption key from the mounted Kubernetes Secret.

After decryption and extraction, the model is loaded from the local files rather than being
downloaded again from Hugging Face.

A successful execution ends with:

```text
Model loaded successfully: BertForPreTraining
```

## 🔑 Key Management

The encryption key is generated by the Producer for the Kubernetes flow.

The key is not embedded in the encrypted artifact and is not published to Hugging Face.

The Layer 1 architecture is:

```text
                   Producer
                      │
             generates AES key
                      │
              ┌───────┴────────┐
              │                │
              ▼                ▼
     encrypted artifact      key
              │                │
              ▼                ▼
       Hugging Face Hub   Kubernetes Secret
                                 │
                                 │ mounted as file
                                 ▼
                              Consumer
```

The Makefile creates or updates the Secret with:

```bash
make create-model-secret
```

The Secret is named:

```text
model-encryption-key
```

The Consumer reads the key from:

```text
/run/secrets/model-encryption-key/KEY_BASE64
```

### Key rotation

The Kubernetes Producer generates a new 256-bit key on every execution.

The generated keys were verified to be different across two executions of the Kubernetes flow.

The Secret is updated with the new key before the Consumer Job is started.

## ☸️ Kubernetes

Kubernetes runs the Consumer as a Job and provides the encryption key through a Secret.

The relevant manifest mounts the Secret as a read-only volume:

```yaml
volumeMounts:
  - name: model-encryption-key
    mountPath: /run/secrets/model-encryption-key
    readOnly: true

volumes:
  - name: model-encryption-key
    secret:
      secretName: model-encryption-key
```

This directly satisfies the Layer 1 requirement that the Consumer workload mounts the decryption
key from a Kubernetes Secret.

### Docker Desktop Kubernetes

The end-to-end verification was performed using Docker Desktop Kubernetes.

The Consumer image is built locally and imported into the Kubernetes node because the tested
cluster uses containerd.

The current Makefile uses the Docker Desktop Kubernetes node:

```text
desktop-control-plane
```

This is environment-specific. A different Kubernetes environment would normally use a container
registry instead of importing the image directly into the node.

### Kubernetes resources

The Layer 1 deployment uses:

- `model-encryption-key` Kubernetes Secret for the AES key.
- `huggingface-token` Kubernetes Secret for Hugging Face authentication.
- A Consumer Kubernetes Job.
- A Consumer Pod created by the Job.

### Step-by-step deployment

Verify the cluster:

```bash
kubectl config current-context
kubectl get nodes
```

Generate and publish the encrypted artifact:

```bash
make run-producer-k8s
```

Create or update the encryption Secret:

```bash
make create-model-secret
```

Build the Consumer image:

```bash
make build-consumer
```

Load the image into the Kubernetes node:

```bash
make load-consumer-k8s
```

Run the Consumer Job:

```bash
make run-consumer-k8s
```

Check the Pod:

```bash
kubectl get pods
```

Then inspect the logs:

```bash
kubectl logs <consumer-pod-name>
```

A successful execution contains:

```text
Model encrypted file downloaded at: ...
Model zip decrypted file downloaded at: ...
Model extracted file downloaded at: ...
Loading weights: 100% ...
Model loaded successfully: BertForPreTraining
```

### Complete Kubernetes flow

The complete flow can also be executed with:

```bash
make run-k8s
```

This performs:

```text
1. Generate a new encryption key
2. Download and encrypt the model
3. Upload the encrypted artifact
4. Create/update the Kubernetes Secret
5. Build the Consumer Docker image
6. Import the image into the Kubernetes node
7. Create the Consumer Job
8. Download encrypted artifact
9. Read the mounted key
10. Decrypt the artifact
11. Extract the model
12. Load the model
```

## 🐳 Docker

Producer and Consumer are packaged as independent Docker images.

Each application has its own dependency definition and lock file.

Build the Producer image:

```bash
make build-producer
```

Build the Consumer image:

```bash
make build-consumer
```

The Consumer image used by Kubernetes is:

```text
capacity-consumer:latest
```

For the current Docker Desktop Kubernetes environment, it is imported with:

```bash
make load-consumer-k8s
```

## 🧪 Testing Strategy

The project uses `pytest` for automated tests.

Run the complete test suite:

```bash
make test
```

The current test suite contains 20 tests:

- 14 Producer tests
- 6 Consumer tests

Producer tests cover encryption, key generation, decryption, tampering detection, wrong-key
handling, model download, packaging, publishing and CLI argument parsing.

Consumer tests cover encrypted artifact handling, decryption, wrong-key rejection and CLI
argument parsing.

Run the code-quality checks:

```bash
make pre-commit
```

The complete test suite and pre-commit checks have been successfully executed during development.

## 🗂️ Repository Structure

```text
.
├── producer/
│   ├── src/
│   │   ├── encryption.py
│   │   ├── main.py
│   │   ├── model.py
│   │   ├── publishing.py
│   │   ├── settings.py
│   │   └── zip.py
│   ├── tests/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── uv.lock
│
├── consumer/
│   ├── src/
│   │   ├── downloading.py
│   │   ├── encryption.py
│   │   ├── main.py
│   │   ├── model.py
│   │   └── settings.py
│   ├── tests/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── uv.lock
│
├── kubernetes/
│   └── consumer.yaml
│
├── .pre-commit-config.yaml
├── .gitignore
├── Makefile
└── README.md
```

## 🚀 Local Installation

### Prerequisites

The following tools are required:

- Python 3.14
- `uv`
- Docker
- `kubectl`
- A running Kubernetes cluster for the Kubernetes deployment
- A Hugging Face account and access token
- A Hugging Face repository where the encrypted artifact can be uploaded

Verify the tools:

```bash
python --version
uv --version
docker --version
kubectl version --client
```

Verify Kubernetes:

```bash
kubectl config current-context
kubectl get nodes
```

### Install dependencies

Install Producer dependencies:

```bash
make install-producer
```

Install Consumer dependencies:

```bash
make install-consumer
```

### Configuration

For local execution, the required configuration is provided through `.env` files.

The encryption key for local execution is provided as:

```text
KEY_BASE64
```

Do not commit `.env` files or real credentials to the repository.

For Kubernetes execution, the encryption key is generated by the Producer and delivered through
the Kubernetes Secret instead of the Consumer `.env`.

## ▶️ Running the Pipeline

### Local flow

Run the Producer:

```bash
make run-producer
```

Then run the Consumer:

```bash
make run-consumer
```

### Kubernetes flow

For the complete Kubernetes flow:

```bash
make run-k8s
```

For the individual steps:

```bash
make run-producer-k8s
make create-model-secret
make build-consumer
make load-consumer-k8s
make run-consumer-k8s
```

Then verify:

```bash
kubectl get pods
kubectl logs <consumer-pod-name>
```

The expected final result is:

```text
Model loaded successfully: BertForPreTraining
```

## 🛡️ Security Considerations

This project is a proof of concept focused on the required Layer 1 confidential model
distribution flow.

### Encryption key

The AES key is the most sensitive value in the system.

It must not be committed to Git or published together with the encrypted artifact.

The Kubernetes flow generates a fresh key for every Producer execution.

### Kubernetes Secret

The Kubernetes Secret is the Layer 1 key-delivery mechanism.

The Secret is mounted into the Consumer Pod as a read-only file.

Kubernetes Secret values are represented using Base64 encoding. Base64 is encoding, not
encryption.

Protection of Secret data at rest depends on the Kubernetes cluster configuration and access
controls.

### Hugging Face artifact

The artifact stored in Hugging Face is encrypted.

The plaintext model is not uploaded as part of this distribution flow.

Artifact metadata such as filename and size is still visible.

### AES-GCM integrity

AES-256-GCM provides authenticated encryption.

If the encrypted artifact is modified, authentication fails during decryption and the Consumer
does not accept the modified ciphertext.

### PoC limitations

The current implementation reads the complete archive into memory during encryption and
decryption. This is appropriate for the selected small model but would need to be reconsidered
for multi-gigabyte models.

The current Kubernetes image-loading approach is specific to the tested Docker Desktop
Kubernetes environment. A production cluster would normally pull the Consumer image from a
container registry.

## 🛠️ Contribution Guide

### Pre-commit Hooks

Install the hooks:

```bash
make pre-commit-install
```

Run all checks:

```bash
make pre-commit
```

### Tests

Run the complete test suite:

```bash
make test
```

### Code style

The project uses Ruff for linting and formatting.

Changes should keep Producer and Consumer responsibilities clearly separated and avoid adding
complexity that is not required by the current Layer 1 implementation.
