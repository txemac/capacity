import argparse
import base64
from pathlib import Path

import settings
from encryption import encrypt_file
from model import download_model
from publishing import publish_artifact
from zip import create_zip_file


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
    model_name = args.model.replace("/", "-")

    # create output dir
    settings.OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    # download model
    path_model = Path(settings.OUTPUT_DIRECTORY / model_name)
    download_model(model_id=args.model, path_model=path_model)
    print(f"Model downloaded at: {path_model}")

    # zip folder
    path_zip = create_zip_file(path_model=path_model)
    print(f"Zip created at: {path_zip}")

    # encrypt zip file
    key = base64.b64decode(settings.KEY_BASE64)
    path_enc = encrypt_file(key=key, path_zip=path_zip)
    print(f"Encrypted artifact created at: {path_enc}")

    # upload encrypted file
    publish_artifact(path_enc=path_enc)
    print(f"File uploaded to: {settings.HF_REPO_ID}")


if __name__ == "__main__":
    main()
