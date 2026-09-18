import argparse

from cryptography.exceptions import InvalidSignature

import settings
from downloading import download_model_file
from downloading import download_sig_file
from encryption import decrypt_file
from model import load_model
from signing import verify_file
from zip import extract_file


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download, verify, decrypt and load a Hugging Face model.",
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
    try:
        path_encrypted_file = download_model_file(model_file=args.model)
    except ValueError as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"Model encrypted file downloaded at: {path_encrypted_file}")

    # download model signature file
    try:
        path_signature = download_sig_file(sig_file=f"{args.model}.sig")
    except ValueError as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)

    print(f"Model signature file downloaded at: {path_signature}")

    # verify model signature
    try:
        verify_file(
            path_enc=path_encrypted_file,
            path_sig=path_signature,
            path_public_key=settings.PUBLIC_KEY_FILE,
        )
    except InvalidSignature:
        print("ERROR: Model signature verification failed.")
        raise SystemExit(1)
    except ValueError as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)

    print("Model signature verified successfully")

    # zip decrypted file
    file = decrypt_file(key=settings.get_encryption_key(), path_encrypted_file=path_encrypted_file)
    path_zip_file = path_encrypted_file.with_suffix("")
    path_zip_file.write_bytes(file)
    print(f"Model zip decrypted file downloaded at: {path_zip_file}")

    # extract file
    path_model = extract_file(path_zip_file=path_zip_file)
    print(f"Model extracted file downloaded at: {path_model}")

    # load model
    model = load_model(path_model=path_model)
    print(f"Model loaded successfully: {model.__class__.__name__}")


if __name__ == "__main__":
    main()
