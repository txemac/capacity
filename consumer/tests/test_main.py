import sys

import pytest

from main import parse_arguments


def test_parse_arguments_requires_artifact() -> None:
    with pytest.raises(SystemExit):
        sys.argv = ["main.py"]

        parse_arguments()


def test_parse_arguments_returns_model_file() -> None:
    sys.argv = [
        "main.py",
        "--model",
        "google-bert_uncased_L-2_H-128_A-2.tar.gz.enc",
    ]

    args = parse_arguments()

    assert args.model == "google-bert_uncased_L-2_H-128_A-2.tar.gz.enc"
