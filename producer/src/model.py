from pathlib import Path

from huggingface_hub import snapshot_download


def download_model(
    model_id: str,
    path_model: Path,
) -> None:
    """Download a model from Hugging Face Hub."""
    snapshot_download(
        repo_id=model_id,
        local_dir=path_model,
    )
