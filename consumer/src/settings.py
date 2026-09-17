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


# required environment variables
HF_TOKEN = get_required_setting("HF_TOKEN")
HF_REPO_ID = get_required_setting("HF_REPO_ID")

# app setting
CONSUMER_DIRECTORY = Path(__file__).parents[1]
OUTPUT_DIRECTORY = CONSUMER_DIRECTORY / "output"
