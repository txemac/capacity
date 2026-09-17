import tarfile
from pathlib import Path


def create_zip_file(
    path_model: Path,
) -> Path:
    """Create a gzip-compressed tar archive from a directory."""
    path_zip = path_model.with_suffix(".tar.gz")
    with tarfile.open(path_zip, mode="w:gz") as archive:
        archive.add(
            path_model,
            arcname=path_model.name,
        )

    return path_zip
