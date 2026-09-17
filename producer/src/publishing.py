from pathlib import Path

from huggingface_hub import HfApi

import settings


def publish_artifact(
    path_enc: Path,
) -> None:
    """Upload an encrypted artifact to a Hugging Face model repository."""
    api = HfApi(token=settings.HF_TOKEN)

    api.upload_file(
        path_or_fileobj=path_enc,
        path_in_repo=path_enc.name,
        repo_id=settings.HF_REPO_ID,
        repo_type="model",
    )
