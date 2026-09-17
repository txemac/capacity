import argparse
import base64

import settings
from downloading import download_model_file
from encryption import decrypt_file


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download, decrypt and load a Hugging Face model.",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Hugging Face repository model file",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    # create output dir
    settings.OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    # download model encrypted file
    path_encrypted_file = download_model_file(model_file=args.model)
    print(f"Model encrypted file downloaded at: {path_encrypted_file}")

    # zip decrypted file
    key = base64.b64decode(settings.KEY_BASE64)
    file = decrypt_file(key=key, path_encrypted_file=path_encrypted_file)
    path_zip_file = path_encrypted_file.with_suffix("")
    path_zip_file.write_bytes(file)
    print(f"Model zip decrypted file downloaded at: {path_zip_file}")


if __name__ == "__main__":
    main()
