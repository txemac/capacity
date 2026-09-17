import pytest

from main import parse_arguments


def test_parse_arguments_requires_model(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["main.py"],
    )

    with pytest.raises(SystemExit):
        parse_arguments()


def test_parse_arguments_returns_model(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--model",
            "test/model",
        ],
    )

    args = parse_arguments()

    assert args.model == "test/model"
