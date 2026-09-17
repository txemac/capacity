from pathlib import Path

import pytest

import settings


@pytest.fixture(autouse=True)
def test_settings(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OUTPUT_DIRECTORY", tmp_path)


@pytest.fixture
def model_file() -> str:
    return "artifact_example.tar.gz.enc"


@pytest.fixture
def path_model_file(
    model_file: str,
) -> Path:
    return Path(__file__).parent / model_file


@pytest.fixture
def mock_download_model_file(
    path_model_file: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    def download_artifact_mock(*args: object, **kwargs: object) -> str:
        return str(path_model_file)

    monkeypatch.setattr("downloading.hf_hub_download", download_artifact_mock)
    return path_model_file
