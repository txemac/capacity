from pathlib import Path

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from signing import generate_key_pair
from signing import sign_file

PRIVATE_KEY_FILENAME = "signing-private-key.pem"
PUBLIC_KEY_FILENAME = "signing-public-key.pem"


def test_generate_key_pair(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "settings.OUTPUT_DIRECTORY",
        tmp_path,
    )

    path_private_key, path_public_key = generate_key_pair()

    assert isinstance(path_private_key, Path)
    assert isinstance(path_public_key, Path)
    assert path_private_key == tmp_path / PRIVATE_KEY_FILENAME
    assert path_public_key == tmp_path / PUBLIC_KEY_FILENAME
    assert path_private_key.exists()
    assert path_public_key.exists()

    private_key = serialization.load_pem_private_key(
        path_private_key.read_bytes(),
        password=None,
    )
    public_key = serialization.load_pem_public_key(
        path_public_key.read_bytes(),
    )

    assert isinstance(private_key, Ed25519PrivateKey)
    assert isinstance(public_key, Ed25519PublicKey)
    assert public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ) == private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def test_generate_key_pair_reuses_existing_keys(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "settings.OUTPUT_DIRECTORY",
        tmp_path,
    )

    first_private_key, first_public_key = generate_key_pair()

    first_private_key_content = first_private_key.read_bytes()
    first_public_key_content = first_public_key.read_bytes()

    second_private_key, second_public_key = generate_key_pair()

    assert second_private_key == first_private_key
    assert second_public_key == first_public_key
    assert second_private_key.read_bytes() == first_private_key_content
    assert second_public_key.read_bytes() == first_public_key_content


def test_sign_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "settings.OUTPUT_DIRECTORY",
        tmp_path,
    )

    path_private_key, path_public_key = generate_key_pair()

    path_enc = tmp_path / "model.tar.gz.enc"
    path_enc.write_bytes(b"encrypted model content")

    path_sig = sign_file(
        path_enc=path_enc,
        path_private_key=path_private_key,
    )

    assert isinstance(path_sig, Path)
    assert path_sig == Path(f"{path_enc}.sig")
    assert path_sig.exists()

    public_key = serialization.load_pem_public_key(
        path_public_key.read_bytes(),
    )

    public_key.verify(
        path_sig.read_bytes(),
        path_enc.read_bytes(),
    )


def test_sign_file_detects_tampered_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "settings.OUTPUT_DIRECTORY",
        tmp_path,
    )

    path_private_key, path_public_key = generate_key_pair()

    path_enc = tmp_path / "model.tar.gz.enc"
    path_enc.write_bytes(b"encrypted model content")

    path_sig = sign_file(
        path_enc=path_enc,
        path_private_key=path_private_key,
    )

    path_enc.write_bytes(b"tampered model content")

    public_key = serialization.load_pem_public_key(
        path_public_key.read_bytes(),
    )

    with pytest.raises(InvalidSignature):
        public_key.verify(
            path_sig.read_bytes(),
            path_enc.read_bytes(),
        )
