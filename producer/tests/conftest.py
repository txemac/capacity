from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from encryption import encrypt_file
from encryption import generate_key


@pytest.fixture
def encrypted_file(tmp_path: Path) -> tuple[Path, Path, bytes]:
    input_path = tmp_path / "model.tar.gz"
    output_path = tmp_path / "model.tar.gz.enc"
    key = generate_key()

    input_path.write_bytes(b"test model content")

    encrypt_file(
        input_path=input_path,
        output_path=output_path,
        key=key,
    )

    return input_path, output_path, key


@pytest.fixture
def mock_snapshot_download() -> Iterator[MagicMock]:
    with patch("model.snapshot_download") as mock:
        yield mock
