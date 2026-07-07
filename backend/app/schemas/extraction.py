# """
# Pydantic models for the MTO extraction API.

# These schemas define the contract between the frontend and backend.
# The mock `/extract` endpoint returns `ExtractionResponse` until Gemini
# vision integration is implemented.
# """

# from datetime import datetime, timezone

# from pydantic import BaseModel, Field


# class MtoLineItem(BaseModel):
#     """A single material take-off line extracted from an isometric drawing."""

#     item_code: str = Field(..., description="Unique item or part identifier")
#     description: str = Field(..., description="Human-readable item description")
#     size: str = Field(..., description='Nominal size, e.g. 4" NPS')
#     schedule: str = Field(..., description="Pipe schedule or wall thickness class")
#     quantity: float = Field(..., ge=0, description="Quantity of the item")
#     unit: str = Field(..., description="Unit of measure, e.g. m, ea, kg")
#     confidence: float = Field(
#         ...,
#         ge=0.0,
#         le=1.0,
#         description="Model confidence score for this line item",
#     )


# class ExtractionMetadata(BaseModel):
#     """Metadata about the extraction run."""

#     drawing_number: str = Field(..., description="Drawing number from the isometric")
#     line_number: str = Field(..., description="Piping line identifier")
#     extracted_at: datetime = Field(
#         default_factory=lambda: datetime.now(timezone.utc),
#         description="UTC timestamp when extraction completed",
#     )
#     model: str = Field(..., description="Model or pipeline used for extraction")


# class ExtractionResponse(BaseModel):
#     """Successful response payload for POST /extract."""

#     success: bool = Field(..., description="Whether extraction completed successfully")
#     filename: str = Field(..., description="Original uploaded filename")
#     items: list[MtoLineItem] = Field(
#         default_factory=list,
#         description="Extracted material take-off line items",
#     )
#     metadata: ExtractionMetadata = Field(
#         ...,
#         description="Contextual metadata about the drawing and extraction",
#     )

"""
Pydantic models for the MTO extraction API.

These schemas define the contract between the frontend and backend.
The mock `/extract` endpoint returns `ExtractionResponse` until Gemini
vision integration is implemented.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

UNKNOWN = "Unknown"


class MtoLineItem(BaseModel):
    """A single material take-off line extracted from an isometric drawing."""

    category: str = Field(
        default=UNKNOWN,
        description=(
            "Component type/category, e.g. Pipe, Elbow 90, Elbow 45, Tee, "
            "Reducer, Flange, Gasket, Bolt/Nut Set, Valve, Cap, Olet, Support, "
            "Instrument. Use 'Unknown' if it cannot be determined."
        ),
    )
    description: str = Field(
        default=UNKNOWN,
        description="Human-readable item description exactly as shown on the drawing/BOM.",
    )
    size_nps: str = Field(
        default=UNKNOWN,
        description='Nominal pipe size of this item, e.g. 4", 2"x1", DN100.',
    )
    schedule_rating: str = Field(
        default=UNKNOWN,
        description=(
            "Pipe schedule or pressure/flange rating, e.g. SCH 40, SCH 80, "
            "STD, XS, 150#, 300#, 600#."
        ),
    )
    material_spec: str = Field(
        default=UNKNOWN,
        description="Material specification/grade, e.g. A106 Gr B, A234 WPB, A105, SS316.",
    )
    end_type: str = Field(
        default=UNKNOWN,
        description="End connection type, e.g. BW (Butt Weld), SW (Socket Weld), THD (Threaded), FLG (Flanged).",
    )
    quantity: float = Field(
        default=0,
        ge=0,
        description="Quantity of the item. Use 0 if not determinable.",
    )
    unit: str = Field(
        default=UNKNOWN,
        description="Unit of measure, e.g. m, ea, kg, ft.",
    )
    length_m: Optional[float] = Field(
        default=None,
        ge=0,
        description="Length of the item in meters, if applicable (e.g. pipe runs). Null if not applicable/visible.",
    )
    remarks: str = Field(
        default=UNKNOWN,
        description="Any additional notes, callouts, or field annotations relevant to this item.",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Model confidence score for this line item, between 0.0 and 1.0.",
    )


class ExtractionMetadata(BaseModel):
    """Metadata about the drawing and the extraction run."""

    drawing_number: str = Field(default=UNKNOWN, description="Drawing number from the isometric")
    line_number: str = Field(default=UNKNOWN, description="Piping line identifier")
    revision: str = Field(default=UNKNOWN, description="Drawing revision, e.g. Rev A, Rev 2")
    material_class: str = Field(
        default=UNKNOWN, description="Piping material class/spec code, e.g. A1A, B31.3 Class 150"
    )
    nps: str = Field(default=UNKNOWN, description="Overall/header nominal pipe size of the line")
    service: str = Field(
        default=UNKNOWN, description="Process service/fluid, e.g. Cooling Water, Steam, Crude Oil"
    )
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