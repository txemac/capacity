from pathlib import Path

import pytest
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from encryption import encrypt_file
from encryption import generate_key


def test_generate_key_returns_256_bit_key() -> None:
    key = generate_key()

    assert len(key) == 32


def test_encrypt_file_creates_encrypted_file(tmp_path: Path) -> None:
    input_path = tmp_path / "model.tar.gz"
    output_path = tmp_path / "model.tar.gz.enc"
    key = generate_key()

    plaintext = b"test model content"
    input_path.write_bytes(plaintext)

    encrypt_file(
        input_path=input_path,
        output_path=output_path,
        key=key,
    )

    assert output_path.exists()
    assert output_path.is_file()


def test_encrypt_file_does_not_store_plaintext(tmp_path: Path) -> None:
    input_path = tmp_path / "model.tar.gz"
    output_path = tmp_path / "model.tar.gz.enc"
    key = generate_key()

    plaintext = b"test model content"
    input_path.write_bytes(plaintext)

    encrypt_file(
        input_path=input_path,
        output_path=output_path,
        key=key,
    )

    ciphertext = output_path.read_bytes()

    assert plaintext not in ciphertext


def test_encrypt_file_can_be_decrypted(
    encrypted_file: tuple[Path, Path, bytes],
) -> None:
    _, output_path, key = encrypted_file

    encrypted_data = output_path.read_bytes()

    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]

    decrypted = AESGCM(key).decrypt(
        nonce,
        ciphertext,
        None,
    )

    assert decrypted == b"test model content"


def test_encrypt_file_detects_tampered_ciphertext(
    encrypted_file: tuple[Path, Path, bytes],
) -> None:
    _, output_path, key = encrypted_file

    encrypted_data = bytearray(output_path.read_bytes())

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
    encrypted_file: tuple[Path, Path, bytes],
) -> None:
    _, output_path, _ = encrypted_file
    wrong_key = generate_key()

    encrypted_data = output_path.read_bytes()

    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]

    with pytest.raises(InvalidTag):
        AESGCM(wrong_key).decrypt(
            nonce,
            ciphertext,
            None,
        )
