from pathlib import Path
from unittest.mock import MagicMock

import pytest
from model import download_model


def test_download_model_calls_snapshot_download(
    mock_snapshot_download: MagicMock,
    tmp_path: Path,
) -> None:
    model_id = "test/model"
    output_directory = tmp_path / "model"

    download_model(
        model_id=model_id,
        output_directory=output_directory,
    )

    mock_snapshot_download.assert_called_once_with(
        repo_id=model_id,
        local_dir=output_directory,
    )


def test_download_model_returns_output_directory(
    mock_snapshot_download: MagicMock,
    tmp_path: Path,
) -> None:
    output_directory = tmp_path / "model"

    result = download_model(
        model_id="test/model",
        output_directory=output_directory,
    )

    assert result == output_directory


def test_download_model_propagates_download_error(
    mock_snapshot_download: MagicMock,
    tmp_path: Path,
) -> None:
    mock_snapshot_download.side_effect = RuntimeError(
        "Download failed",
    )

    output_directory = tmp_path / "model"

    with pytest.raises(RuntimeError, match="Download failed"):
        download_model(
            model_id="test/model",
            output_directory=output_directory,
        )
