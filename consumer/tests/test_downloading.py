from pathlib import Path

from downloading import download_model_file


def test_download_model_file(
    example_encrypted_file: str,
    mock_download_model_file: Path,
) -> None:
    path_model_file = download_model_file(model_file=example_encrypted_file)

    assert isinstance(path_model_file, Path)
    assert path_model_file == mock_download_model_file
