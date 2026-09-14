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
3. Decrypt the model using the key.
4. Load the model.

## Layer 2 (Optional): Model Signing & Verification
Extend Layer 1 by adding a signing step to the producer and a verification step to the consumer,
ensuring the model artifact was not tampered with between publication and use.

### Additional steps on top of Layer 1:
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

### Additional steps on top of Layer 1:
1. Deploy the CoCo operator and Trustee KBS on the cluster using the
“kata-qemu-coco-dev” runtime class.
2. Store the decryption key in KBS via “kbs-client set-resource” under a defined resource
path (e.g. default/key/my-model) instead of a Kubernetes Secret.
3. Configure a permissive resource policy in KBS allowing key release to sample TEE
attestation.
4. Run the consumer pod with the KBS address configured via the “agent.aa_kbc_params” parameter annotation.
5. Fetch the decryption key from KBS through the Confidential Data Hub (CDH) endpoint at
127.0.0.1:8006/cdh/resource/..., relying on the full attestation flow.

## General Notes:
● Layers 2 and 3 are independent: a candidate may implement Layer 1 + Layer 3 (attested
delivery without signing) or Layer 1 + Layer 2 + Layer 3 (the full stack).
● The choice of model, encryption library, and tooling is left to the candidate (justification
might be asked during the discussion of the solution).

## Deliverables
A public Git repository containing:
● Dockerfiles for the producer and consumer workloads.
● Kubernetes manifests for all workloads (Pods, Secrets, or any other resources used).
● A README covering prerequisites, how to build and deploy the full pipeline, and how to
verify each layer works.

Reference: [Confidential Containers without confidential hardware](https://confidentialcontainers.org/blog/2024/12/03/confidential-containers-without-confidential-hardware/)


# SOLUTION

## 📖 Table of Contents

- [🏗️ Solution Overview](#-solution-overview)
- [🔐 Encryption Approach](#-encryption-approach)
- [🤗 Model Selection](#-model-selection)
- [📦 Artifact Packaging](#-artifact-packaging)
- [⚙️ Producer](#-producer)
- [🗂️ Repository Structure](#-repository-structure)
- [🚀 Local Installation](#-local-installation)
- [🧪 Run Tests](#-run-tests)
- [🛠️ Contribution Guide](#-contribution-guide)

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
                    │ Load model          │
                    └─────────────────────┘
```

The implementation follows the three layers defined in the assignment. Layer 1 is the required scope, while Layers 2 and 3 are optional extensions.

The current implementation focuses first on building and testing the Producer locally before introducing the Kubernetes deployment and Consumer components.

This approach keeps the individual responsibilities small and makes it possible to validate each part of the pipeline independently.

## 🔐 Encryption Approach

The model artifact is encrypted using AES-256-GCM, an authenticated symmetric encryption scheme.

Symmetric encryption was selected because the model artifact can potentially be large and symmetric algorithms provide efficient encryption and decryption.

AES-GCM was selected because it provides both:

- **Confidentiality** ... the encrypted artifact does not expose the model contents.
- **Integrity** ... modifications to the encrypted artifact are detected during decryption.

The encryption key is generated by the Producer and is kept separate from the encrypted artifact.

For Layer 1, the key will ultimately be distributed to the Consumer through a Kubernetes Secret, as required by the assignment.

### Why AES-256-GCM?

AES-256-GCM was chosen because:

- It is a symmetric encryption algorithm.
- It is efficient for large data.
- It provides authenticated encryption.
- It is widely used and supported by mature cryptographic libraries.
- The Python `cryptography` library provides a straightforward implementation.

An asymmetric algorithm such as RSA was not selected to encrypt the model directly because asymmetric encryption is considerably less suitable for large files due to its computational cost and size limitations.

A hybrid encryption scheme would be a common production approach ... using symmetric encryption for the model and asymmetric cryptography to protect the symmetric key.

For this PoC, however, the encryption key is distributed separately through a Kubernetes Secret, so introducing asymmetric key wrapping would add complexity without being required by Layer 1.

## 🤗 Model Selection

`google/bert_uncased_L-2-H-128-A-2` was selected as the reference model for the PoC.

It is a compact BERT model with 4.43 million parameters and a model size of approximately 17.7 MB in Safetensors format.

The model was intentionally selected to be small because model size is not relevant to the security properties being demonstrated.

A smaller model provides several practical benefits during development:

- Faster downloads.
- Lower resource requirements.
- Faster encryption and packaging.
- Faster test and development cycles.

The model can also be selected from the command line, allowing the Producer to be tested with a different Hugging Face model without changing the application code.

The default model is defined in the `Makefile`:

```makefile
MODEL_ID ?= google/bert_uncased_L-2-H-128-A-2
```

It can be overridden when running the Producer:

```bash
make run-producer MODEL_ID=distilbert/distilbert-base-uncased
```

Keeping the model selection outside the application logic avoids duplicating the default model identifier in multiple places.

## 📦 Artifact Packaging

A Hugging Face model is normally composed of multiple files.

Instead of encrypting each file individually, the model directory is first packaged into a single `tar.gz` archive:

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

This approach provides a single artifact for distribution and ensures that all files required to reconstruct the model are protected by the same encryption operation.

The encrypted artifact is therefore the unit that will be published to Hugging Face Hub.

For this PoC, the complete archive is read into memory during encryption. This is acceptable for the selected small model, but a production implementation handling multi-gigabyte models should consider streaming or chunked encryption to avoid requiring the entire artifact to fit in memory.

## ⚙️ Producer

The Producer is responsible for preparing the model and creating the encrypted distribution artifact.

The current workflow is:

1. Download the selected model from Hugging Face.
2. Package the model files into a `tar.gz` archive.
3. Generate a cryptographically secure AES-256 key.
4. Encrypt the archive using AES-256-GCM.
5. Store the generated key separately from the encrypted artifact.

The current implementation produces:

```text
producer/output/
├── model/
├── model.tar.gz
├── model.tar.gz.enc
└── encryption.key
```

The plaintext model and intermediate archive are local Producer artifacts used during the preparation process.

The encryption key is not committed to the repository and will later be provided to the Consumer through a Kubernetes Secret.

### Producer and Kubernetes separation

The Producer does not contain Kubernetes-specific deployment logic.

The Producer is responsible for generating the encrypted artifact and encryption key, while Kubernetes configuration is handled separately.

This separation avoids giving the Producer unnecessary access to the Kubernetes API and keeps the model preparation logic independent from the deployment environment.

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

The Hugging Face publication and Kubernetes Secret creation will be added as the next steps of the Layer 1 implementation.

## 🗂️ Repository Structure

The repository is organized by responsibility, keeping the model distribution logic separated from the Kubernetes deployment configuration.

The structure will evolve as the implementation progresses.

Current structure:

```text
.
├── producer/                   # the model preparation logic
│   ├── src/
│   │   ├── main.py             # orchestrates the Producer workflow and command-line interface
│   │   ├── model.py            # downloads models from Hugging Face Hub
│   │   ├── packaging.py        # creates the `tar.gz` model archive
│   │   └── encryption.py       # generates encryption keys and encrypts artifacts using AES-256-GCM
│   └── tests/
├── consumer/                   # the workload responsible for retrieving, decrypting and loading the protected model
├── kubernetes/                 # the Kubernetes manifests required to deploy the Producer and Consumer workloads and the Kubernetes Secret containing the decryption key.
├── README.md                   # Project documentation
├── pyproject.toml              # Project dependencies and tool configurations
├── uv.lock                     # UV lock file for managing dependencies
├── Makefile                    # CLI shortcuts: install, build, test, pre-commit, clean...
└── LICENSE                     # license
```

## 🚀 Local Installation

### 🐍 Use a Virtual Environment

Using a virtual environment helps your IDE with development and allows you to run commands in an isolated environment.

* Create a virtual environment and install the dependencies:
```bash
make install
```

* Clean environment: (delete the environment and temporal files):
```bash
make clean
```

## 🧪 Run Tests

The Producer is covered by unit tests using `pytest`.

External Hugging Face downloads are mocked in the tests so that the test suite remains deterministic and does not require network access.

The current test suite can be executed with:

```bash
make test
```

Code quality checks are executed using pre-commit:

```bash
make pre-commit
```

## 🛠️ Contribution Guide

### Pre-commit Hooks:
This project uses pre-commit hooks to enforce code quality and formatting before commits.
* Install Pre-Commit:
```bash
make pre-commit-install
```

* Running pre-Commit manually:
```bash
make pre-commit
```
