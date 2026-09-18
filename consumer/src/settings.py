import base64
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_required_setting(
    name: str,
) -> str:
    """Get a required setting from the environment."""
    value = os.getenv(name)

    if not value:
        raise ValueError(f"Required setting '{name}' is not configured.")

    return value


def get_encryption_key() -> bytes:
    """Get the encryption key from Kubernetes Secret or local environment."""
    if KEY_FILE.exists():
        key_base64 = KEY_FILE.read_text().strip()
    else:
        key_base64 = get_required_setting("KEY_BASE64")

    return base64.b64decode(key_base64)


# required environment variables
HF_TOKEN = get_required_setting("HF_TOKEN")
HF_REPO_ID = get_required_setting("HF_REPO_ID")

# Kubernetes Secret
KEY_FILE = Path("/run/secrets/model-encryption-key/KEY_BASE64")

# app settings
CONSUMER_DIRECTORY = Path(__file__).parents[1]
OUTPUT_DIRECTORY = CONSUMER_DIRECTORY / "output"

NONCE_SIZE = 12
KEY_SIZE = 256
