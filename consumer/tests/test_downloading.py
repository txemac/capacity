from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from huggingface_hub.errors import RemoteEntryNotFoundError

from downloading import download_model_file
from downloading import download_sig_file


def test_download_model_file(
    example_encrypted_file: str,
    mock_download_model_file: Path,
) -> None:
    path_model_file = download_model_file(model_file=example_encrypted_file)

    assert isinstance(path_model_file, Path)
    assert path_model_file == mock_download_model_file


def test_download_model_file_download_error() -> None:
    model_file = "does-not-exist.tar.gz.enc"
    response = MagicMock()
    response.status_code = 404
    response.request = MagicMock()

    with patch(
        "downloading.hf_hub_download",
        side_effect=RemoteEntryNotFoundError(
            message="Entry not found",
            response=response,
        ),
    ):
        with pytest.raises(ValueError, match=f"Model file '{model_file}' not in repository"):
            download_model_file(model_file=model_file)


def test_download_sig_file(
    example_sig_file: str,
    mock_download_model_file: Path,
) -> None:
    path_sig_file = download_sig_file(sig_file=example_sig_file)

    assert isinstance(path_sig_file, Path)
    assert path_sig_file == mock_download_model_file


def test_download_sig_file_download_error() -> None:
    sig_file = "does-not-exist.tar.gz.enc.sig"
    response = MagicMock()
    response.status_code = 404
    response.request = MagicMock()

    with patch(
        "downloading.hf_hub_download",
        side_effect=RemoteEntryNotFoundError(
            message="Entry not found",
            response=response,
        ),
    ):
        with pytest.raises(ValueError, match=f"Signature '{sig_file}' not in repository"):
            download_sig_file(sig_file=sig_file)
