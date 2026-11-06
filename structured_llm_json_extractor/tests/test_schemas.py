import pytest
from pydantic import ValidationError
from src.schemas import InvoiceExtraction, ResumeExtraction

def test_currency_is_normalized():
    assert InvoiceExtraction(currency="usd").currency == "USD"

def test_negative_invoice_total_is_rejected():
    with pytest.raises(ValidationError):
        InvoiceExtraction(total="-10")

def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        InvoiceExtraction(unexpected="nope")

def test_resume_negative_experience_is_rejected():
    with pytest.raises(ValidationError):
        ResumeExtraction(years_experience=-1)

def test_missing_lists_default_to_empty():
    assert ResumeExtraction().skills == []
