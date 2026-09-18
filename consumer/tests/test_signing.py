from pathlib import Path

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from signing import verify_file


def create_key_pair(
    tmp_path: Path,
) -> tuple[Path, Path]:
    """Create an Ed25519 key pair for testing."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    path_private_key = tmp_path / "private-key.pem"
    path_public_key = tmp_path / "public-key.pem"

    path_private_key.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )

    path_public_key.write_bytes(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ),
    )

    return path_private_key, path_public_key


def test_verify_file(
    tmp_path: Path,
) -> None:
    path_private_key, path_public_key = create_key_pair(tmp_path)

    path_enc = tmp_path / "model.tar.gz.enc"
    path_sig = tmp_path / "model.tar.gz.enc.sig"

    path_enc.write_bytes(b"encrypted model content")

    private_key = serialization.load_pem_private_key(
        path_private_key.read_bytes(),
        password=None,
    )

    path_sig.write_bytes(
        private_key.sign(path_enc.read_bytes()),
    )

    verify_file(
        path_enc=path_enc,
        path_sig=path_sig,
        path_public_key=path_public_key,
    )


def test_verify_file_detects_tampered_file(
    tmp_path: Path,
) -> None:
    path_private_key, path_public_key = create_key_pair(tmp_path)

    path_enc = tmp_path / "model.tar.gz.enc"
    path_sig = tmp_path / "model.tar.gz.enc.sig"

    path_enc.write_bytes(b"encrypted model content")

    private_key = serialization.load_pem_private_key(
        path_private_key.read_bytes(),
        password=None,
    )

    path_sig.write_bytes(
        private_key.sign(path_enc.read_bytes()),
    )

    path_enc.write_bytes(b"tampered model content")

    with pytest.raises(InvalidSignature):
        verify_file(
            path_enc=path_enc,
            path_sig=path_sig,
            path_public_key=path_public_key,
        )
