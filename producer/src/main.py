import argparse
import base64
from pathlib import Path

import settings
from encryption import encrypt_file
from encryption import generate_key
from model import download_model
from publishing import publish_artifact
from signing import generate_key_pair
from signing import sign_file
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
    parser.add_argument(
        "--generate-key",
        action="store_true",
        help="Generate a new encryption key instead of using KEY_BASE64",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    model_name = args.model.replace("/", "-")

    # create output dir
    settings.OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    # download model
    path_model = Path(settings.OUTPUT_DIRECTORY / model_name)
    try:
        download_model(model_id=args.model, path_model=path_model)
    except ValueError as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"Model downloaded at: {path_model}")

    # zip folder
    path_zip = create_zip_file(path_model=path_model)
    print(f"Zip created at: {path_zip}")

    # encrypt zip file
    key = generate_key() if args.generate_key else settings.get_encryption_key()
    path_enc = encrypt_file(key=key, path_zip=path_zip)
    print(f"Encrypted artifact created at: {path_enc}")

    if args.generate_key:
        path_key = settings.OUTPUT_DIRECTORY / ".key"
        path_key.write_text(base64.b64encode(key).decode("ascii"))
        print(f"Key created at: {path_key}")

    # generate signing key pair
    path_private_key, path_public_key = generate_key_pair()
    print(f"Signing private key available at: {path_private_key}")
    print(f"Signing public key available at: {path_public_key}")

    # sign encrypted file
    path_sig = sign_file(
        path_private_key=path_private_key,
        path_enc=path_enc,
    )
    print(f"Signature created at: {path_sig}")

    # upload encrypted file and signature
    publish_artifact(path_enc=path_enc)
    publish_artifact(path_enc=path_sig)

    print(f"Files uploaded to: {settings.HF_REPO_ID}")


if __name__ == "__main__":
    main()
