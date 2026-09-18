from pathlib import Path

from model import load_model


def test_load_model(
    path_example_model: Path,
) -> None:
    model = load_model(path_model=path_example_model)

    assert model.config.model_type == "bert"
