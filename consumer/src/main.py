import argparse

import settings
from downloading import download_model_file


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

    # download model file
    path_model_file = download_model_file(model_file=args.model)
    print(f"Model encrypted file downloaded at: {path_model_file}")


if __name__ == "__main__":
    main()
