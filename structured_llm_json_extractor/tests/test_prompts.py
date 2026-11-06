from src.prompts import build_extraction_prompt
from src.schemas import InvoiceExtraction, ResumeExtraction


def test_prompt_includes_schema_and_document():
    prompt = build_extraction_prompt(
        "Total: 12 USD",
        InvoiceExtraction,
        "invoice",
    )

    assert "TARGET JSON SCHEMA" in prompt
    assert "Total: 12 USD" in prompt
    assert "INVOICE-SPECIFIC EXTRACTION RULES" in prompt
    assert "every identifiable line item" in prompt.lower()
    assert "description" in prompt.lower()


def test_invoice_prompt_includes_complete_example():
    prompt = build_extraction_prompt(
        "Invoice Number: INV-123",
        InvoiceExtraction,
        "invoice",
    )

    assert "NORTHSTAR OFFICE SUPPLIES" in prompt
    assert "Black Toner Cartridge" in prompt
    assert "INV-123" in prompt


def test_resume_prompt_includes_resume_rules():
    prompt = build_extraction_prompt(
        "Name: Alex Example",
        ResumeExtraction,
        "resume",
    )

    assert "RESUME-SPECIFIC EXTRACTION RULES" in prompt
    assert "Alex Example" in prompt
    assert "experience" in prompt.lower()


def test_unsupported_document_type_is_rejected():
    try:
        build_extraction_prompt(
            "Some document",
            InvoiceExtraction,
            "contract",
        )
    except ValueError as exc:
        assert "document_type" in str(exc)
    else:
        raise AssertionError(
            "Unsupported document types should raise ValueError."
        )