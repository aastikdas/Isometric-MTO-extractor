"""
Pydantic models for the MTO extraction API.

These schemas define the contract between the frontend and backend.
The mock `/extract` endpoint returns `ExtractionResponse` until Gemini
vision integration is implemented.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class MtoLineItem(BaseModel):
    """A single material take-off line extracted from an isometric drawing."""

    item_code: str = Field(..., description="Unique item or part identifier")
    description: str = Field(..., description="Human-readable item description")
    size: str = Field(..., description='Nominal size, e.g. 4" NPS')
    schedule: str = Field(..., description="Pipe schedule or wall thickness class")
    quantity: float = Field(..., ge=0, description="Quantity of the item")
    unit: str = Field(..., description="Unit of measure, e.g. m, ea, kg")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence score for this line item",
    )


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction run."""

    drawing_number: str = Field(..., description="Drawing number from the isometric")
    line_number: str = Field(..., description="Piping line identifier")
    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when extraction completed",
    )
    model: str = Field(..., description="Model or pipeline used for extraction")


class ExtractionResponse(BaseModel):
    """Successful response payload for POST /extract."""

    success: bool = Field(..., description="Whether extraction completed successfully")
    filename: str = Field(..., description="Original uploaded filename")
    items: list[MtoLineItem] = Field(
        default_factory=list,
        description="Extracted material take-off line items",
    )
    metadata: ExtractionMetadata = Field(
        ...,
        description="Contextual metadata about the drawing and extraction",
    )
