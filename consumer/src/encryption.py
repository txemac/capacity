from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import settings


def decrypt_file(
    key: bytes,
    path_encrypted_file: Path,
) -> bytes:
    """Decrypt an encrypted file using AES-256-GCM."""
    encrypted_data = path_encrypted_file.read_bytes()

    nonce = encrypted_data[: settings.NONCE_SIZE]
    ciphertext = encrypted_data[settings.NONCE_SIZE :]

    aesgcm = AESGCM(key)
    decrypted_data = aesgcm.decrypt(
        nonce,
        ciphertext,
        None,
    )

    return decrypted_data
