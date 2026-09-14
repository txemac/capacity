import tarfile
from pathlib import Path

from packaging import create_archive


def test_create_archive_creates_archive(
    tmp_path: Path,
) -> None:
    source_directory = tmp_path / "model"
    output_path = tmp_path / "model.tar.gz"

    source_directory.mkdir()
    (source_directory / "config.json").write_text('{"model": "test"}')
    (source_directory / "model.txt").write_text("test model")

    create_archive(
        source_directory=source_directory,
        output_path=output_path,
    )

    assert output_path.exists()
    assert output_path.is_file()
    assert tarfile.is_tarfile(output_path)


def test_create_archive_contains_source_files(
    tmp_path: Path,
) -> None:
    source_directory = tmp_path / "model"
    output_path = tmp_path / "model.tar.gz"

    source_directory.mkdir()

    (source_directory / "config.json").write_text('{"model": "test"}')
    (source_directory / "model.txt").write_text("test model")

    create_archive(
        source_directory=source_directory,
        output_path=output_path,
    )

    with tarfile.open(output_path, mode="r:gz") as archive:
        members = archive.getnames()

    assert "model/config.json" in members
    assert "model/model.txt" in members


def test_create_archive_preserves_file_content(
    tmp_path: Path,
) -> None:
    source_directory = tmp_path / "model"
    output_path = tmp_path / "model.tar.gz"

    source_directory.mkdir()

    original_content = "test model content"
    (source_directory / "model.txt").write_text(original_content)

    create_archive(
        source_directory=source_directory,
        output_path=output_path,
    )

    extraction_directory = tmp_path / "extracted"

    with tarfile.open(output_path, mode="r:gz") as archive:
        archive.extractall(extraction_directory)

    extracted_content = (extraction_directory / "model" / "model.txt").read_text()

    assert extracted_content == original_content
