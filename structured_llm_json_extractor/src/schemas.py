from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class InvoiceItem(StrictSchema):
    description: str = Field(
        min_length=1,
        description="Non-empty description of the invoice line item.",
    )
    quantity: float | None = Field(default=None, ge=0)
    unit_price: Decimal | None = Field(default=None, ge=0)
    amount: Decimal | None = Field(default=None, ge=0)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Invoice item description cannot be blank.")
        return value

class InvoiceExtraction(StrictSchema):
    document_type: Literal["invoice"] = "invoice"
    vendor_name: str | None = None
    invoice_number: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    subtotal: Decimal | None = Field(default=None, ge=0)
    tax: Decimal | None = Field(default=None, ge=0)
    total: Decimal | None = Field(default=None, ge=0)
    customer_name: str | None = None
    items: list[InvoiceItem] = Field(default_factory=list)
    payment_terms: str | None = None
    notes: list[str] = Field(default_factory=list)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value):
        return value.upper() if value else value

class ResumeExperience(StrictSchema):
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    location: str | None = None
    highlights: list[str] = Field(default_factory=list)

class ResumeEducation(StrictSchema):
    institution: str | None = None
    qualification: str | None = None
    field_of_study: str | None = None
    graduation_date: str | None = None

class ResumeExtraction(StrictSchema):
    document_type: Literal["resume"] = "resume"
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    headline: str | None = None
    skills: list[str] = Field(default_factory=list)
    years_experience: float | None = Field(default=None, ge=0)
    experience: list[ResumeExperience] = Field(default_factory=list)
    education: list[ResumeEducation] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
