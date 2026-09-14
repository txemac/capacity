import tarfile
from pathlib import Path


def create_archive(
    source_directory: Path,
    output_path: Path,
) -> None:
    """Create a gzip-compressed tar archive from a directory."""
    with tarfile.open(output_path, mode="w:gz") as archive:
        archive.add(
            source_directory,
            arcname=source_directory.name,
        )
