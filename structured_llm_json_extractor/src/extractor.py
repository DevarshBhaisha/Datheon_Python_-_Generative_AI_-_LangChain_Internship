import json
import os
import time

from pydantic import BaseModel, ValidationError
from google import genai
from google.genai import types

from src.prompts import build_extraction_prompt
from src.schemas import InvoiceExtraction, ResumeExtraction


# Supported document types and their Pydantic models.
SCHEMAS = {
    "invoice": InvoiceExtraction,
    "resume": ResumeExtraction,
}


class ExtractionError(RuntimeError):
    """Raised when document extraction fails."""


def _is_retryable_error(exc: Exception) -> bool:
    """
    Determine whether an extraction error should be retried.

    Retry:
    - Invalid JSON returned by the model.
    - Pydantic validation errors.
    - Extraction errors, such as an empty model response.
    - API rate limits (HTTP 429).
    - Server-side API errors (HTTP 5xx).

    Do not automatically retry other unexpected errors.
    """
    if isinstance(
        exc,
        (json.JSONDecodeError, ValidationError, ExtractionError),
    ):
        return True

    status_code = getattr(exc, "status_code", None)

    if isinstance(status_code, int):
        return status_code == 429 or 500 <= status_code <= 599

    return False


def _gemini_response_schema(schema_model):
    """
    Convert a Pydantic JSON Schema into a simpler schema for Gemini.

    Gemini's structured-output API supports a subset of JSON Schema.
    This helper removes unsupported metadata and expands local references
    where possible. Pydantic remains responsible for final validation.
    """
    original_schema = schema_model.model_json_schema()

    definitions = original_schema.pop("$defs", {})
    original_schema.pop("title", None)

    unsupported_keys = {
        "$schema",
        "$id",
        "$defs",
        "$ref",
        "additionalProperties",
        "default",
        "examples",
        "title",
        "format",
        "pattern",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
    }

    def clean(value):
        if isinstance(value, list):
            return [clean(item) for item in value]

        if not isinstance(value, dict):
            return value

        # Expand local references such as #/$defs/InvoiceItem.
        if "$ref" in value:
            reference = value["$ref"]

            if reference.startswith("#/$defs/"):
                definition_name = reference.rsplit("/", 1)[-1]
                definition = definitions.get(definition_name)

                if definition is not None:
                    expanded = clean(definition)

                    # Preserve sibling constraints or metadata.
                    siblings = {
                        key: item
                        for key, item in value.items()
                        if key != "$ref"
                    }

                    if siblings:
                        expanded.update(clean(siblings))

                    return expanded

        cleaned = {}

        for key, item in value.items():
            if key in unsupported_keys:
                continue

            cleaned[key] = clean(item)

        # Keep only required fields that exist in properties.
        if cleaned.get("type") == "object":
            properties = cleaned.get("properties", {})

            if "required" in cleaned:
                cleaned["required"] = [
                    name
                    for name in cleaned["required"]
                    if name in properties
                ]

                if not cleaned["required"]:
                    cleaned.pop("required")

        return cleaned

    return clean(original_schema)


class GeminiExtractor:
    """Extract structured invoice or resume data using Gemini."""

    def __init__(self, api_key=None, model=None, max_retries=2):
        """
        Initialize the Gemini client.

        The API key is read from the supplied argument or GEMINI_API_KEY.
        The model can be configured through GEMINI_MODEL.
        """
        key = api_key or os.getenv("GEMINI_API_KEY")

        if not key:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Copy .env.example to .env and add your API key."
            )

        self.client = genai.Client(api_key=key)

        self.model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

        self.max_retries = max(0, max_retries)

    def extract(self, document_text: str, document_type: str) -> BaseModel:
        """
        Extract structured information from a document.

        Args:
            document_text: Raw text from an invoice or resume.
            document_type: Either "invoice" or "resume".

        Returns:
            A validated Pydantic model containing the extracted data.

        Raises:
            ValueError: If the input is empty or the document type is invalid.
            ExtractionError: If extraction or validation fails.
        """
        if not document_text or not document_text.strip():
            raise ValueError("Document text cannot be empty.")

        kind = document_type.lower().strip()

        if kind not in SCHEMAS:
            raise ValueError(
                "document_type must be either 'invoice' or 'resume'."
            )

        schema_model = SCHEMAS[kind]

        prompt = build_extraction_prompt(
            document_text,
            schema_model,
            kind,
        )

        response_schema = _gemini_response_schema(schema_model)

        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=response_schema,
                        temperature=0,
                    ),
                )

                if not response.text:
                    raise ExtractionError(
                        "Gemini returned an empty response."
                    )

                payload = json.loads(response.text)

                # Validate against the complete Pydantic model.
                validated_data = schema_model.model_validate(payload)

                return validated_data

            except Exception as exc:
                last_error = exc

                # Stop when retries are exhausted or the error is not
                # considered recoverable.
                if (
                    attempt >= self.max_retries
                    or not _is_retryable_error(exc)
                ):
                    break

                delay = 0.8 * (2 ** attempt)
                time.sleep(delay)

        raise ExtractionError(
            f"Extraction failed after {attempt + 1} attempt(s): "
            f"{last_error}"
        ) from last_error