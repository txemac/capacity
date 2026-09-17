import secrets
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import settings


def generate_key() -> bytes:
    """Generate a cryptographically secure AES-256 key."""
    return AESGCM.generate_key(bit_length=settings.KEY_SIZE)


def encrypt_file(
    key: bytes,
    path_zip: Path,
) -> Path:
    """Encrypt a file using AES-256-GCM."""
    plaintext = path_zip.read_bytes()

    nonce = secrets.token_bytes(settings.NONCE_SIZE)

    ciphertext = AESGCM(key).encrypt(
        nonce=nonce,
        data=plaintext,
        associated_data=None,
    )

    path_enc = path_zip.with_name(path_zip.name + ".enc")
    path_enc.write_bytes(nonce + ciphertext)

    return path_enc
