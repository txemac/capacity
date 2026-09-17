import tarfile
from pathlib import Path


def extract_file(
    path_zip_file: Path,
) -> Path:
    """Extract a tar.gz archive into a directory next to the archive."""
    path_model = path_zip_file.with_name(path_zip_file.name.removesuffix(".tar.gz"))
    path_model.mkdir(parents=True, exist_ok=True)

    with tarfile.open(path_zip_file, mode="r:gz") as archive:
        archive.extractall(path_model)

    return path_model
