import tarfile
from pathlib import Path


def create_zip_file(
    path_model: Path,
) -> Path:
    """Create a gzip-compressed tar archive from a directory."""
    path_zip = path_model.with_suffix(".tar.gz")
    with tarfile.open(path_zip, mode="w:gz") as archive:
        for path_file in path_model.iterdir():
            archive.add(
                path_file,
                arcname=path_file.name,
            )

    return path_zip
