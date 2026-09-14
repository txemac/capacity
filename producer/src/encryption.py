import secrets
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_SIZE = 256
NONCE_SIZE = 12


def generate_key() -> bytes:
    """Generate a cryptographically secure AES-256 key."""
    return AESGCM.generate_key(bit_length=KEY_SIZE)


def encrypt_file(
    input_path: Path,
    output_path: Path,
    key: bytes,
) -> None:
    """Encrypt a file using AES-256-GCM."""
    plaintext = input_path.read_bytes()

    nonce = secrets.token_bytes(NONCE_SIZE)

    ciphertext = AESGCM(key).encrypt(
        nonce,
        plaintext,
        None,
    )

    output_path.write_bytes(nonce + ciphertext)
