import argparse
from pathlib import Path

from encryption import encrypt_file
from encryption import generate_key
from model import download_model
from packaging import create_archive

OUTPUT_DIRECTORY = Path(__file__).parents[1] / "output"
MODEL_DIRECTORY = OUTPUT_DIRECTORY / "model"
ARCHIVE_PATH = OUTPUT_DIRECTORY / "model.tar.gz"
ENCRYPTED_PATH = OUTPUT_DIRECTORY / "model.tar.gz.enc"
KEY_PATH = OUTPUT_DIRECTORY / "encryption.key"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download, package and encrypt a Hugging Face model.",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Hugging Face model ID",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    download_model(
        model_id=args.model,
        output_directory=MODEL_DIRECTORY,
    )

    create_archive(
        source_directory=MODEL_DIRECTORY,
        output_path=ARCHIVE_PATH,
    )

    key = generate_key()

    encrypt_file(
        input_path=ARCHIVE_PATH,
        output_path=ENCRYPTED_PATH,
        key=key,
    )

    KEY_PATH.write_bytes(key)

    print(f"Encrypted artifact created at: {ENCRYPTED_PATH}")


if __name__ == "__main__":
    main()
