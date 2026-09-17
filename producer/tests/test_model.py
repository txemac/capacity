from pathlib import Path
from unittest.mock import MagicMock

import pytest

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
