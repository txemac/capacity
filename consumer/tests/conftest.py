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
def example_model_name() -> str:
    return "model_example"


@pytest.fixture
def example_encrypted_file(
    example_model_name: str,
) -> str:
    return f"{example_model_name}.tar.gz.enc"


@pytest.fixture
def path_example_encrypted_file(
    example_encrypted_file: str,
) -> Path:
    return Path(__file__).parent / "files" / example_encrypted_file


@pytest.fixture
def example_sig_file(
    example_model_name: str,
) -> str:
    return f"{example_model_name}.tar.gz.enc.sig"


@pytest.fixture
def path_example_sig_file(
    example_sig_file: str,
) -> Path:
    return Path(__file__).parent / "files" / example_sig_file


@pytest.fixture
def path_example_model(
    example_model_name: str,
    path_example_encrypted_file: str,
) -> Path:
    return Path(__file__).parent / "files" / example_model_name


@pytest.fixture
def mock_download_model_file(
    path_example_encrypted_file: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    def download_artifact_mock(*args: object, **kwargs: object) -> str:
        return str(path_example_encrypted_file)

    monkeypatch.setattr("downloading.hf_hub_download", download_artifact_mock)
    return path_example_encrypted_file
