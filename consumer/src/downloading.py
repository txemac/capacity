from pathlib import Path

from huggingface_hub import hf_hub_download

import settings


def download_model_file(
    model_file: str,
) -> Path:
    """Download an encrypted model file from Hugging Face Hub."""
    return Path(
        hf_hub_download(
            repo_id=settings.HF_REPO_ID,
            filename=model_file,
            token=settings.HF_TOKEN,
            local_dir=settings.OUTPUT_DIRECTORY,
        ),
    )
