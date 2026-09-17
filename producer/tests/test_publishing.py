from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import settings
from publishing import publish_artifact


def test_publish_artifact_uploads_file(
    path_enc: Path,
) -> None:
    with patch("publishing.HfApi") as mock_hf_api:
        api = MagicMock()
        mock_hf_api.return_value = api

        publish_artifact(path_enc=path_enc)

    mock_hf_api.assert_called_once_with(token=settings.HF_TOKEN)
    api.upload_file.assert_called_once_with(
        path_or_fileobj=path_enc,
        path_in_repo=path_enc.name,
        repo_id=settings.HF_REPO_ID,
        repo_type="model",
    )
