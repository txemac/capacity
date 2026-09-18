from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import settings


def generate_key_pair() -> tuple[Path, Path]:
    """Create the Producer signing key pair if it does not already exist."""
    path_private_key = settings.OUTPUT_DIRECTORY / settings.PRIVATE_KEY_FILENAME
    path_public_key = settings.OUTPUT_DIRECTORY / settings.PUBLIC_KEY_FILENAME

    if path_private_key.exists() and path_public_key.exists():
        return path_private_key, path_public_key

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

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


def sign_file(
    path_enc: Path,
    path_private_key: Path,
) -> Path:
    """Create an Ed25519 signature for an encrypted file."""
    private_key = serialization.load_pem_private_key(
        path_private_key.read_bytes(),
        password=None,
    )

    signature = private_key.sign(path_enc.read_bytes())

    path_sig = Path(f"{path_enc}.sig")
    path_sig.write_bytes(signature)

    return path_sig
