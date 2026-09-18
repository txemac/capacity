from pathlib import Path

from huggingface_hub import hf_hub_download
from huggingface_hub.errors import RemoteEntryNotFoundError

import settings


def download_model_file(
    model_file: str,
) -> Path:
    """Download an encrypted model file from Hugging Face Hub."""
    try:
        path_model = hf_hub_download(
            repo_id=settings.HF_REPO_ID,
            filename=model_file,
            local_dir=settings.OUTPUT_DIRECTORY,
        )
    except RemoteEntryNotFoundError as error:
        raise ValueError(f"Model file '{model_file}' not in repository '{settings.HF_REPO_ID}'.") from error

    return Path(path_model)
