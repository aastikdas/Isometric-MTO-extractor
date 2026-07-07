"""
Pydantic models for the MTO extraction API.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class MtoLineItem(BaseModel):
    """Single extracted MTO item."""

    category: str = Field(..., description="Component category")
    description: str = Field(..., description="Engineering description")
    size_nps: str = Field(..., description="Nominal pipe size")
    schedule_rating: str = Field(..., description="Schedule or pressure class")
    material_spec: str = Field(..., description="Material specification")
    end_type: str = Field(..., description="Connection/end type")
    quantity: float = Field(..., ge=0)
    unit: str = Field(...)
    length_m: Optional[float] = Field(default=None)
    remarks: str = Field(default="Unknown")
    confidence: float = Field(..., ge=0.0, le=1.0)


class ExtractionMetadata(BaseModel):
    drawing_number: str = Field(default="Unknown")
    line_number: str = Field(default="Unknown")
    revision: str = Field(default="Unknown")
    material_class: str = Field(default="Unknown")
    nps: str = Field(default="Unknown")
    service: str = Field(default="Unknown")
    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    model: str = Field(default="gemini-2.5-flash")


class ExtractionResponse(BaseModel):
    success: bool
    filename: str
    items: list[MtoLineItem] = Field(default_factory=list)
    metadata: ExtractionMetadata