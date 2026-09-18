from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import settings
from encryption import encrypt_file
from encryption import generate_key
from zip import create_zip_file


@pytest.fixture(autouse=True)
def test_settings(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OUTPUT_DIRECTORY", tmp_path)


@pytest.fixture(scope="session")
def model_id() -> str:
    return "capacity/test-model"


@pytest.fixture()
def path_model(
    model_id: str,
) -> Path:
    model_name = model_id.replace("/", "-")

    path_model = Path(settings.OUTPUT_DIRECTORY / model_name)

    path_model.mkdir()
    (path_model / "config.json").write_text('{"model": "test"}')
    (path_model / "model.txt").write_text("test model")

    return path_model


@pytest.fixture()
def path_zip(
    path_model: Path,
) -> Path:
    return create_zip_file(path_model=path_model)


@pytest.fixture()
def key() -> bytes:
    return generate_key()


@pytest.fixture()
def path_enc(
    path_zip: Path,
    key: bytes,
) -> Path:
    return encrypt_file(key=key, path_zip=path_zip)


@pytest.fixture
def mock_snapshot_download() -> Iterator[MagicMock]:
    with patch("model.snapshot_download") as mock:
        yield mock
