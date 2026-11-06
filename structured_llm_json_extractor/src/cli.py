import argparse
import json
import logging
from pathlib import Path

from dotenv import load_dotenv

from src.extractor import GeminiExtractor, ExtractionError


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Extract validated JSON from invoice or resume text."
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["invoice", "resume"],
        help="Type of document to extract.",
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to the input text file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path where the JSON output will be saved.",
    )

    args = parser.parse_args()

    try:
        # Read the source document.
        text = args.input.read_text(encoding="utf-8")

        # Extract information and validate it using Pydantic.
        result = GeminiExtractor().extract(text, args.type)

        # Serialize the validated model into properly formatted JSON.
        rendered = json.dumps(
            result.model_dump(mode="json"),
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

        # Verify that the serialized output is valid JSON.
        json.loads(rendered)

        if args.output:
            # Create the destination directory if necessary.
            args.output.parent.mkdir(parents=True, exist_ok=True)

            # Write a real newline, not the literal characters "\n".
            args.output.write_text(
                rendered + "\n",
                encoding="utf-8",
                newline="\n",
            )

            print(f"Validated JSON written to {args.output}")
        else:
            print(rendered)

        return 0

    except (OSError, ValueError, ExtractionError) as exc:
        logging.error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
