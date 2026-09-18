from pathlib import Path

from transformers import BertForPreTraining


def load_model(path_model: Path) -> BertForPreTraining:
    """Load a Hugging Face pre-training model from a local directory."""
    return BertForPreTraining.from_pretrained(
        path_model,
        local_files_only=True,
    )
