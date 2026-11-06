import json
from unittest.mock import Mock, patch

import pytest

from src.extractor import GeminiExtractor, ExtractionError
from src.schemas import InvoiceExtraction


@pytest.fixture
def mocked_gemini():
    """Create an extractor with a mocked Gemini client."""
    with patch("src.extractor.genai.Client") as client_class:
        client = Mock()
        client_class.return_value = client

        extractor = GeminiExtractor(
            api_key="test-api-key",
            max_retries=0,
        )

        yield extractor, client


def test_successful_invoice_extraction(mocked_gemini):
    """A valid Gemini response should produce a validated invoice."""
    extractor, client = mocked_gemini

    expected_data = InvoiceExtraction(
        currency="USD",
    ).model_dump(mode="json")

    client.models.generate_content.return_value.text = json.dumps(
        expected_data
    )

    result = extractor.extract(
        "Invoice total: 100 USD",
        "invoice",
    )

    assert isinstance(result, InvoiceExtraction)
    assert result.currency == "USD"
    client.models.generate_content.assert_called_once()


def test_empty_document_is_rejected(mocked_gemini):
    """Empty document text should fail before calling Gemini."""
    extractor, client = mocked_gemini

    with pytest.raises(ValueError, match="cannot be empty"):
        extractor.extract("", "invoice")

    client.models.generate_content.assert_not_called()


def test_whitespace_document_is_rejected(mocked_gemini):
    """Whitespace-only input should also be rejected."""
    extractor, client = mocked_gemini

    with pytest.raises(ValueError, match="cannot be empty"):
        extractor.extract("   \n\t  ", "invoice")

    client.models.generate_content.assert_not_called()


def test_unsupported_document_type_is_rejected(mocked_gemini):
    """Unsupported document types should fail before calling Gemini."""
    extractor, client = mocked_gemini

    with pytest.raises(ValueError, match="document_type"):
        extractor.extract("Some document text", "contract")

    client.models.generate_content.assert_not_called()


def test_invalid_json_response_raises_extraction_error(mocked_gemini):
    """Malformed JSON from Gemini should produce a clear error."""
    extractor, client = mocked_gemini

    client.models.generate_content.return_value.text = "{invalid json"

    with pytest.raises(ExtractionError, match="Extraction failed"):
        extractor.extract("Invoice total: 100 USD", "invoice")

    client.models.generate_content.assert_called_once()


def test_invalid_invoice_data_raises_extraction_error(mocked_gemini):
    """Data that violates the invoice schema should be rejected."""
    extractor, client = mocked_gemini

    invalid_data = InvoiceExtraction(
        currency="USD",
    ).model_dump(mode="json")

    invalid_data["total"] = "-10"

    client.models.generate_content.return_value.text = json.dumps(
        invalid_data
    )

    with pytest.raises(ExtractionError, match="Extraction failed"):
        extractor.extract("Invoice total: 100 USD", "invoice")

    client.models.generate_content.assert_called_once()


def test_api_failure_raises_extraction_error(mocked_gemini):
    """An API failure should be wrapped in ExtractionError."""
    extractor, client = mocked_gemini

    client.models.generate_content.side_effect = RuntimeError(
        "Simulated API failure"
    )

    with pytest.raises(ExtractionError, match="Simulated API failure"):
        extractor.extract("Invoice total: 100 USD", "invoice")

    client.models.generate_content.assert_called_once()


def test_retry_attempts_are_made_without_real_delays():
    """The extractor retries temporary server errors."""
    with (
        patch("src.extractor.genai.Client") as client_class,
        patch("src.extractor.time.sleep") as sleep_mock,
    ):
        client = Mock()
        client_class.return_value = client

        temporary_error = RuntimeError("Temporary server failure")
        temporary_error.status_code = 503

        client.models.generate_content.side_effect = temporary_error

        extractor = GeminiExtractor(
            api_key="test-api-key",
            max_retries=2,
        )

        with pytest.raises(ExtractionError, match="3 attempt"):
            extractor.extract("Invoice total: 100 USD", "invoice")

        assert client.models.generate_content.call_count == 3
        assert sleep_mock.call_count == 2


def test_non_retryable_error_is_not_retried():
    """Unexpected non-retryable errors should fail immediately."""
    with (
        patch("src.extractor.genai.Client") as client_class,
        patch("src.extractor.time.sleep") as sleep_mock,
    ):
        client = Mock()
        client_class.return_value = client

        client.models.generate_content.side_effect = RuntimeError(
            "Unexpected programming error"
        )

        extractor = GeminiExtractor(
            api_key="test-api-key",
            max_retries=2,
        )

        with pytest.raises(
            ExtractionError,
            match="Unexpected programming error",
        ):
            extractor.extract("Invoice total: 100 USD", "invoice")

        assert client.models.generate_content.call_count == 1
        sleep_mock.assert_not_called()