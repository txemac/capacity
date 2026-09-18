from pathlib import Path

from huggingface_hub import snapshot_download
from huggingface_hub.errors import RepositoryNotFoundError


def download_model(
    model_id: str,
    path_model: Path,
) -> None:
    """Download a model from Hugging Face Hub."""
    try:
        snapshot_download(
            repo_id=model_id,
            local_dir=path_model,
        )
    except RepositoryNotFoundError as error:
        raise ValueError(f"Model '{model_id}' was not found on Hugging Face Hub.") from error
