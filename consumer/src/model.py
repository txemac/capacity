from pathlib import Path

from transformers import AutoModel


def load_model(path_model: Path) -> AutoModel:
    """Load a Hugging Face model from a local directory."""
    return AutoModel.from_pretrained(
        path_model,
        local_files_only=True,
    )
