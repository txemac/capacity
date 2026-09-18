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
1. Deploy the CoCo operator and Trustee KBS on the cluster using the `kata-qemu-coco-dev` runtime class.
2. Store the decryption key in KBS via `kbs-client set-resource` under a defined resource path (e.g. `default/key/my-model`) instead of a Kubernetes Secret.
3. Configure a permissive resource policy in KBS allowing key release to sample TEE attestation.
4. Run the consumer pod with the KBS address configured via the `agent.aa_kbc_params` parameter annotation.
5. Fetch the decryption key from KBS through the Confidential Data Hub (CDH) endpoint at `127.0.0.1:8006/cdh/resource/...`, relying on the full attestation flow.

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
- [🔮 Future Extensions](#-future-extensions)
- [🛠️ Contribution Guide](#️-contribution-guide)


## 🏗️ Solution Overview

The solution is designed as a two-part model distribution pipeline:

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
                               │ Encrypted artifact
                               ▼
                    ┌─────────────────────┐
                    │      Consumer       │
                    │---------------------│
                    │ Download artifact   │
                    │ Obtain key          │
                    │ Decrypt artifact    │
                    │ Extract model       │
                    │ Load model          │
                    └─────────────────────┘
```

The implementation follows the three layers defined in the assignment.

Layer 1 is the required scope and is the primary focus of this implementation. Layers 2 and 3
are optional extensions that can be added after the required pipeline is complete.

The Producer and Consumer are implemented as independent applications. This keeps the
responsibilities of each workload explicit and allows the individual components to be tested
independently before deploying the complete pipeline to Kubernetes.


## 🔐 Encryption Approach

The model artifact is encrypted using **AES-256-GCM**, an authenticated symmetric encryption
scheme.

Symmetric encryption was selected because model artifacts can potentially be large and
symmetric algorithms are efficient for encrypting and decrypting large amounts of data.

AES-GCM was selected because it provides both:

- **Confidentiality** ... the encrypted artifact does not expose the model contents.
- **Integrity** ... modifications to the encrypted artifact are detected during decryption.

The encryption key is generated by the Producer and is kept separate from the encrypted
artifact.

For Layer 1, the key is distributed to the Consumer through a Kubernetes Secret, as required by
the assignment.

### Why AES-256-GCM?

AES-256-GCM was chosen because:

- It is a symmetric encryption algorithm.
- It is efficient for large files.
- It provides authenticated encryption.
- It is widely used and supported by mature cryptographic libraries.
- The Python `cryptography` library provides a straightforward implementation.

The encryption uses a randomly generated 256-bit key.

A new random 12-byte nonce is generated for each encryption operation. The nonce does not need
to remain secret and is stored together with the encrypted data.

The encrypted file therefore contains:

```text
┌──────────────┬──────────────────────┬─────────────────┐
│    Nonce     │     Ciphertext       │  GCM Auth Tag   │
│   12 bytes   │    encrypted data    │     16 bytes    │
└──────────────┴──────────────────────┴─────────────────┘
```

The GCM authentication tag allows the Consumer to detect modifications to the encrypted
artifact during decryption.

### Why not RSA?

An asymmetric algorithm such as RSA was not selected to encrypt the model directly because
asymmetric encryption is not designed for efficiently encrypting large files.

A common production architecture would use hybrid encryption:

```text
Model
  │
  ▼
AES encryption
  │
  ├── encrypted model
  │
  └── AES key
          │
          ▼
   asymmetric encryption
          │
          ▼
 protected AES key
```

For this PoC, the AES key is distributed separately through a Kubernetes Secret, so adding
asymmetric key wrapping would introduce additional complexity without being required by
Layer 1.

Asymmetric cryptography becomes relevant in Layer 2 for signing and verifying the encrypted
artifact.


## 🤗 Model Selection

`google/bert_uncased_L-2-H-128-A-2` was selected as the reference model for the PoC.

It is a compact BERT model with 4.43 million parameters and a model size of approximately
17.7 MB in Safetensors format.

The model was intentionally selected to be small because model size is not relevant to the
security properties being demonstrated.

A smaller model provides several practical benefits during development:

- Faster downloads.
- Lower resource requirements.
- Faster encryption and packaging.
- Faster test and development cycles.

The model can be selected from the command line, allowing the Producer to be tested with a
different Hugging Face model without changing the application code.

The default model is defined in the root `Makefile`:

```makefile
MODEL_ID ?= google/bert_uncased_L-2-H-128-A-2
```

It can be overridden when running the Producer:

```bash
make run-producer MODEL_ID=distilbert/distilbert-base-uncased
```

Keeping the model selection outside the application logic avoids duplicating the default model
identifier in multiple places.


## 📦 Artifact Packaging

A Hugging Face model is normally composed of multiple files.

Instead of encrypting each file individually, the model directory is first packaged into a
single `tar.gz` archive:

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

This approach provides a single artifact for distribution and ensures that all files required to
reconstruct the model are protected by the same encryption operation.

The encrypted artifact is therefore the unit that is published to Hugging Face Hub.

The archive contains the model files at its root:

```text
model.tar.gz
├── config.json
├── model.safetensors
├── tokenizer.json
└── ...
```

This avoids introducing an unnecessary extra directory level when the Consumer extracts the
archive.

### Memory considerations

For this PoC, the complete archive is read into memory during encryption and decryption.

This is acceptable for the selected small model and keeps the implementation simple and easy to
reason about.

A production implementation handling multi-gigabyte models should consider streaming or
chunked encryption and decryption to avoid requiring the entire artifact to fit in memory.


## ⚙️ Producer

The Producer is responsible for preparing the model and creating the encrypted distribution
artifact.

The workflow is:

1. Download the selected model from Hugging Face.
2. Package the model files into a `tar.gz` archive.
3. Generate a cryptographically secure AES-256 key.
4. Encrypt the archive using AES-256-GCM.
5. Keep the generated key separate from the encrypted artifact.
6. Publish the encrypted artifact to Hugging Face Hub.

The local Producer workflow produces artifacts similar to:

```text
producer/output/
├── model/
├── model.tar.gz
├── model.tar.gz.enc
└── encryption.key
```

The plaintext model and intermediate archive are local Producer artifacts used during the
preparation process.

The encryption key is sensitive and must never be committed to the repository.

### Producer and Kubernetes separation

The Producer does not contain Kubernetes-specific deployment logic.

The Producer is responsible for generating the encrypted artifact and encryption key, while
Kubernetes configuration is handled separately.

This separation avoids giving the Producer unnecessary access to the Kubernetes API and keeps
the model preparation logic independent from the deployment environment.

The intended Layer 1 flow is:

```text
Producer
   │
   ├── encrypted artifact ──────► Hugging Face Hub
   │
   └── encryption key ──────────► Kubernetes Secret
                                      │
                                      ▼
                                   Consumer
```

The Producer therefore does not need Kubernetes credentials just to prepare and publish the
model artifact.


## 👤 Consumer

The Consumer is responsible for retrieving the protected model and loading it locally.

The Consumer workflow is:

```text
Hugging Face Hub
       │
       ▼
model.tar.gz.enc
       │
       ▼
download_model_file()
       │
       ▼
decrypt_file()
       │
       ▼
model.tar.gz
       │
       ▼
extract_file()
       │
       ▼
model/
       │
       ▼
load_model()
       │
       ▼
Hugging Face model
```

The individual responsibilities are kept separate:

- `download_model_file()` retrieves the encrypted artifact.
- `decrypt_file()` decrypts the artifact using AES-256-GCM.
- `extract_file()` extracts the `tar.gz` archive.
- `load_model()` loads the resulting model using Transformers.

The model is loaded using:

```python
AutoModel.from_pretrained(
    path_model,
    local_files_only=True,
)
```

The `local_files_only=True` option is intentional.

Once the artifact has been downloaded and decrypted, the Consumer should load the model from
the local decrypted files rather than contacting Hugging Face again to retrieve model data.

This keeps the Consumer workflow explicit:

```text
Download encrypted artifact
        │
        ▼
Decrypt locally
        │
        ▼
Extract locally
        │
        ▼
Load locally
```

### Model filename

The Consumer receives the encrypted artifact filename explicitly.

The default filename is defined in the root `Makefile`:

```makefile
MODEL_FILE ?= google-bert_uncased_L-2-H-128-A-2.tar.gz.enc
```

This allows the Consumer to work with different encrypted artifacts without changing the
application code.


## 🔑 Key Management

The encryption key is generated by the Producer.

The key is not embedded in the encrypted artifact and is not published to Hugging Face.

The intended Layer 1 architecture is:

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
                                 ▼
                              Consumer
```

The Consumer receives the key through the Kubernetes Secret rather than downloading it from
Hugging Face.

This separation is fundamental to the confidentiality model of the PoC.

An attacker who can access the encrypted artifact but does not have access to the encryption key
cannot directly recover the model contents.

### Kubernetes Secret

The Kubernetes Secret is the Layer 1 mechanism required by the assignment.

The Consumer Pod will consume the Secret as a mounted file or environment-provided value,
depending on the final Kubernetes manifest.

The key must not be stored directly in the Git repository.

In a production environment, Kubernetes Secrets should also be considered carefully because
their security depends on the Kubernetes configuration, access controls and underlying secret
storage.


## ☸️ Kubernetes

Kubernetes is used to provide the runtime environment for the Consumer and to distribute the
encryption key.

The intended Layer 1 deployment is:

```text
                  Kubernetes Cluster
┌─────────────────────────────────────────────────────┐
│                                                     │
│  ┌──────────────────────┐                           │
│  │ Kubernetes Secret    │                           │
│  │                      │                           │
│  │ AES encryption key   │                           │
│  └──────────┬───────────┘                           │
│             │                                       │
│             │ mounted into                          │
│             ▼                                       │
│  ┌──────────────────────┐                           │
│  │ Consumer Pod         │                           │
│  │                      │                           │
│  │ 1. Download artifact │                           │
│  │ 2. Read key          │                           │
│  │ 3. Decrypt           │                           │
│  │ 4. Extract model     │                           │
│  │ 5. Load model        │                           │
│  └──────────┬───────────┘                           │
│             │                                       │
└─────────────┼───────────────────────────────────────┘
              │
              │ HTTPS
              ▼
       Hugging Face Hub
```

The Producer does not need to run inside the Kubernetes cluster.

It can run independently to prepare and publish the artifact. Kubernetes is then responsible
for providing the secret to the Consumer workload.

This keeps the Producer independent from the cluster and avoids granting it unnecessary
permissions.


## 🐳 Docker

The Producer and Consumer are packaged as independent Docker images.

Each application has its own dependency definition and lock file.

The Docker images use `uv` to install the exact locked dependencies.

The images are built from the repository root so that the Dockerfiles can access the
corresponding application directory.

### Build Producer image

```bash
docker build -f producer/Dockerfile -t capacity-producer .
```

### Build Consumer image

```bash
docker build -f consumer/Dockerfile -t capacity-consumer .
```

The two workloads are kept in separate images because they have different responsibilities and
different runtime dependencies.

The Producer does not need the full Consumer runtime, and the Consumer does not need the
Producer's model preparation functionality.


## 🧪 Testing Strategy

The project uses `pytest` for automated tests.

The testing strategy focuses on validating the application's own responsibilities while avoiding
unnecessary dependence on external services.

### Producer tests

Producer tests cover the main model preparation operations, including:

- Model download handling.
- Model packaging.
- Encryption.
- Encryption key generation.
- Error handling.
- Artifact creation.

External Hugging Face operations are mocked where appropriate so that unit tests do not require
network access.

### Consumer tests

Consumer tests cover:

- Downloading the encrypted artifact.
- Handling a missing model file.
- Decrypting a valid encrypted artifact.
- Rejecting an invalid encryption key.
- Command-line argument parsing.

The decryption tests use a real encrypted fixture generated by the Producer.

This verifies that the Consumer encryption logic is compatible with the actual artifact format
produced by the Producer.

### Model loading

The Consumer contains the actual model loading implementation using Transformers.

Model loading depends on third-party libraries such as Transformers and PyTorch and is
significantly more expensive than the other unit tests.

For this reason, the primary verification of the model loading step is performed as part of the
Consumer execution rather than relying exclusively on a slow unit test.

A small local Transformers-compatible model fixture can be used when an isolated model-loading
test is required.


## 🗂️ Repository Structure

The repository is organized by responsibility, keeping the model distribution logic separated
from the Kubernetes deployment configuration.

The structure is:

```text
.
├── producer/
│   ├── src/
│   │   ├── main.py
│   │   ├── model.py
│   │   ├── archive.py
│   │   ├── encryption.py
│   │   └── publishing.py
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
│
├── consumer/
│   ├── src/
│   │   ├── main.py
│   │   ├── downloading.py
│   │   ├── encryption.py
│   │   ├── archive.py
│   │   └── model.py
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
│
├── kubernetes/
│   ├── ...
│
├── .pre-commit-config.yaml
├── Makefile
├── README.md
└── LICENSE
```

The exact Kubernetes manifests may evolve as the Layer 1 deployment is completed.


## 🚀 Local Installation

### Prerequisites

The following tools are required for local development:

- Python
- `uv`
- Docker
- `kubectl`
- A Kubernetes cluster for the deployment phase
- A Hugging Face account and access token for private repository access

### Python environment

Using a virtual environment keeps the development environment isolated.

The root Makefile provides a convenient installation command:

```bash
make install
```

To remove local virtual environments and temporary files:

```bash
make clean
```

Each application maintains its own dependency definition and lock file because the Producer and
Consumer have different responsibilities and dependency requirements.


## ▶️ Running the Pipeline

### Run the Producer locally

The Producer can be executed using:

```bash
make run-producer
```

The model can be overridden:

```bash
make run-producer MODEL_ID=distilbert/distilbert-base-uncased
```

The resulting encrypted artifact can then be published to the configured Hugging Face
repository.

### Run the Consumer locally

The Consumer receives the encrypted model filename explicitly:

```bash
make run-consumer MODEL_FILE=google-bert_uncased_L-2-H-128-A-2.tar.gz.enc
```

The Consumer requires the encryption key and Hugging Face configuration through runtime
configuration.

Secrets and access tokens must be supplied through environment variables or Kubernetes Secrets
and must never be committed to the repository.

### Kubernetes deployment

The final Layer 1 deployment will follow this sequence:

```text
1. Prepare model
       │
       ▼
2. Encrypt model
       │
       ▼
3. Publish encrypted artifact
       │
       ▼
4. Create Kubernetes Secret
       │
       ▼
5. Deploy Consumer Pod
       │
       ▼
6. Consumer downloads artifact
       │
       ▼
7. Consumer reads encryption key
       │
       ▼
8. Consumer decrypts artifact
       │
       ▼
9. Consumer extracts model
       │
       ▼
10. Consumer loads model
```

The deployment should be considered successful only when the Consumer can load the decrypted
model inside the Kubernetes Pod.


## 🛡️ Security Considerations

This project is a proof-of-concept and intentionally focuses on demonstrating the core
confidential model delivery flow.

### Encryption key confidentiality

The encryption key is the most sensitive value in the system.

It must:

- Never be committed to Git.
- Never be published alongside the encrypted artifact.
- Only be provided to the Consumer through the configured secret mechanism.

### AES-GCM integrity

AES-256-GCM provides authenticated encryption.

If the encrypted artifact is modified, the authentication tag verification fails during
decryption.

The Consumer therefore does not silently accept corrupted encrypted data.

### Integrity is not producer authenticity

AES-GCM provides integrity and authenticity of the ciphertext with respect to the secret key,
but it does not prove who originally produced the artifact.

If an attacker could replace the encrypted artifact in the distribution repository, AES-GCM can
detect that the ciphertext is not valid for the original encryption operation when the Consumer
attempts decryption.

However, the encryption mechanism alone does not provide cryptographic proof of the Producer's
identity.

This is one of the reasons the assignment provides Layer 2 as an optional extension.

### Kubernetes Secret limitations

Kubernetes Secrets provide the required Layer 1 mechanism for distributing the encryption key.

They do not provide hardware-backed confidentiality or remote attestation.

An environment where the Kubernetes host or privileged cluster components are fully trusted is
therefore assumed for Layer 1.

Layer 3 addresses this limitation by introducing attested key release using Confidential
Containers and Trustee KBS.


## 🔮 Future Extensions

### Layer 2 ... Model Signing

Layer 2 can extend the current implementation with asymmetric signing.

The Producer would:

```text
Encrypted artifact
       │
       ▼
Sign with private key
       │
       ├── encrypted artifact
       │
       └── signature
```

The Consumer would verify the signature before attempting decryption:

```text
Encrypted artifact
       │
       ▼
Verify signature
       │
   ┌───┴────┐
   │        │
 valid    invalid
   │        │
   ▼        ▼
decrypt    abort
```

This provides a separate security property from AES-GCM ... cryptographic verification of the
artifact's provenance.

### Layer 3 ... Attested Key Release

Layer 3 can replace the Kubernetes Secret with an attested key release mechanism using
Confidential Containers and Trustee KBS.

The conceptual flow becomes:

```text
Consumer Pod
     │
     │ attestation
     ▼
Trustee KBS
     │
     │ release key only after policy check
     ▼
Consumer
     │
     ▼
Decrypt model
```

This removes the need to distribute the encryption key directly through a Kubernetes Secret and
allows key release to depend on an attestation result.


## 🛠️ Contribution Guide

### Pre-commit Hooks

This project uses pre-commit hooks to enforce code quality and formatting.

Install the hooks from the repository root:

```bash
make pre-commit-install
```

Run the checks manually:

```bash
make pre-commit
```

### Tests

Run the complete test suite using:

```bash
make test
```

### Code style

The project uses Ruff for linting and formatting.

The repository follows the configuration defined in the corresponding `pyproject.toml` files.

Changes should keep the Producer and Consumer responsibilities clearly separated and avoid adding
complexity that is not required by the current layer of the PoC.
