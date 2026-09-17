import base64
from pathlib import Path

import pytest
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import settings
from encryption import decrypt_file


def test_decrypt_file(
    path_example_encrypted_file: Path,
) -> None:
    key = base64.b64decode(settings.KEY_BASE64)
    file = decrypt_file(key=key, path_encrypted_file=path_example_encrypted_file)

    assert isinstance(file, bytes)


def test_decrypt_file_fails_with_invalid_key(
    path_example_encrypted_file: Path,
) -> None:
    invalid_key = AESGCM.generate_key(bit_length=settings.KEY_SIZE)

    with pytest.raises(InvalidTag):
        decrypt_file(key=invalid_key, path_encrypted_file=path_example_encrypted_file)
