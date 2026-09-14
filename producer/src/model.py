from pathlib import Path

from huggingface_hub import snapshot_download


def download_model(
    model_id: str,
    output_directory: Path,
) -> Path:
    """Download a model from Hugging Face Hub."""
    snapshot_download(
        repo_id=model_id,
        local_dir=output_directory,
    )

    return output_directory
