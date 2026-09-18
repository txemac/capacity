import tarfile
from pathlib import Path

from zip import create_zip_file


def test_create_zip_file_creates_archive(
    path_model: Path,
) -> None:
    path_zip = create_zip_file(path_model=path_model)

    assert path_zip.exists()
    assert path_zip.is_file()
    assert tarfile.is_tarfile(path_zip)


def test_create_zip_file_contains_source_files(
    path_model: Path,
) -> None:
    path_zip = create_zip_file(path_model=path_model)

    with tarfile.open(path_zip, mode="r:gz") as archive:
        members = archive.getnames()

    assert "config.json" in members
    assert "model.txt" in members


def test_create_zip_file_preserves_file_content(
    path_model: Path,
) -> None:
    original_content = (path_model / "model.txt").read_text()
    path_zip = create_zip_file(path_model=path_model)

    extraction_directory = path_model.parent / "extracted"

    with tarfile.open(path_zip, mode="r:gz") as archive:
        archive.extractall(extraction_directory)

    extracted_content = (extraction_directory / "model.txt").read_text()

    assert extracted_content == original_content
