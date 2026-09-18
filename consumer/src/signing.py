from pathlib import Path

from cryptography.hazmat.primitives import serialization


def verify_file(
    path_enc: Path,
    path_sig: Path,
    path_public_key: Path,
) -> None:
    """Verify the Ed25519 signature of an encrypted file."""
    public_key = serialization.load_pem_public_key(
        path_public_key.read_bytes(),
    )

    public_key.verify(
        path_sig.read_bytes(),
        path_enc.read_bytes(),
    )
