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
    """Get the fixed encryption key used for local execution."""
    return base64.b64decode(get_required_setting("KEY_BASE64"))


# required environment variables
HF_TOKEN = get_required_setting("HF_TOKEN")
HF_REPO_ID = get_required_setting("HF_REPO_ID")

# app settings
PRODUCER_DIRECTORY = Path(__file__).parents[1]
OUTPUT_DIRECTORY = PRODUCER_DIRECTORY / "output"

KEY_SIZE = 256
NONCE_SIZE = 12
