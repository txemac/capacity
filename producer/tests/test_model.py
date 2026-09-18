from pathlib import Path
from unittest.mock import MagicMock

import pytest
from huggingface_hub.errors import RepositoryNotFoundError

from model import download_model


def test_download_model_calls_snapshot_download(
    mock_snapshot_download: MagicMock,
    model_id: str,
    path_model: Path,
) -> None:
    download_model(model_id=model_id, path_model=path_model)

    mock_snapshot_download.assert_called_once_with(
        repo_id=model_id,
        local_dir=path_model,
    )


def test_download_model_propagates_download_error(
    mock_snapshot_download: MagicMock,
    model_id: str,
    path_model: Path,
) -> None:
    mock_snapshot_download.side_effect = RuntimeError(
        "Download failed",
    )

    with pytest.raises(RuntimeError, match="Download failed"):
        download_model(model_id=model_id, path_model=path_model)


def test_download_model_raises_value_error_when_repository_is_not_found(
    mock_snapshot_download: MagicMock,
    path_model: Path,
) -> None:
    model_id = "does-not-exist/fake-model"
    response = MagicMock()
    response.status_code = 404
    response.request = MagicMock()

    mock_snapshot_download.side_effect = RepositoryNotFoundError(
        "Repository not found",
        response=response,
    )

    with pytest.raises(
        ValueError,
        match=f"Model '{model_id}' was not found on Hugging Face Hub.",
    ):
        download_model(
            model_id=model_id,
            path_model=path_model,
        )
