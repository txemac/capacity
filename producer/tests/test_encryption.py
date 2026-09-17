from pathlib import Path

import pytest
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from encryption import encrypt_file
from encryption import generate_key


def test_generate_key_returns_256_bit_key(
    key: bytes,
) -> None:
    assert len(key) == 32


def test_encrypt_file_creates_encrypted_file(
    path_zip: Path,
    key: bytes,
) -> None:
    path_enc = encrypt_file(key=key, path_zip=path_zip)

    assert path_enc.exists()
    assert path_enc.is_file()


def test_encrypt_file_does_not_store_plaintext(
    path_zip: Path,
    key: bytes,
) -> None:
    path_enc = encrypt_file(key=key, path_zip=path_zip)

    plaintext = path_zip.read_bytes()
    ciphertext = path_enc.read_bytes()
    assert plaintext not in ciphertext


def test_encrypt_file_can_be_decrypted(
    path_enc: Path,
    path_zip: Path,
    key: bytes,
) -> None:
    encrypted_data = path_enc.read_bytes()

    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]

    decrypted = AESGCM(key).decrypt(
        nonce,
        ciphertext,
        None,
    )

    assert decrypted == path_zip.read_bytes()


def test_encrypt_file_detects_tampered_ciphertext(
    path_enc: Path,
    key: bytes,
) -> None:
    encrypted_data = bytearray(path_enc.read_bytes())

    encrypted_data[-1] ^= 1

    nonce = encrypted_data[:12]
    ciphertext = bytes(encrypted_data[12:])

    with pytest.raises(InvalidTag):
        AESGCM(key).decrypt(
            nonce,
            ciphertext,
            None,
        )


def test_encrypt_file_cannot_be_decrypted_with_wrong_key(
    path_enc: Path,
) -> None:
    wrong_key = generate_key()

    encrypted_data = path_enc.read_bytes()

    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]

    with pytest.raises(InvalidTag):
        AESGCM(wrong_key).decrypt(
            nonce,
            ciphertext,
            None,
        )
