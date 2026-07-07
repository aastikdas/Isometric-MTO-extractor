"""
Gemini Vision service for structured MTO extraction from isometric drawings.

Uses Gemini 2.5 Flash with JSON schema enforcement, then validates the parsed
payload against the existing Pydantic extraction schemas.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from PIL import Image
from pydantic import BaseModel, Field, ValidationError

from app.schemas.extraction import ExtractionMetadata, ExtractionResponse, MtoLineItem

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"

EXTRACTION_PROMPT = """
You are an expert piping engineer analyzing an isometric piping drawing.

Extract a material take-off (MTO) bill of materials from the drawing image(s).
Identify every distinct piping component visible in the material list or BOM table,
including pipes, fittings, flanges, valves, gaskets, bolts, supports, and instruments.

Return ONLY valid JSON matching the required schema with these fields:
- drawing_number: the drawing number shown on the title block
- line_number: the primary piping line identifier
- items: array of line items, each with item_code, description, size, schedule,
  quantity, unit, and confidence (0.0 to 1.0)

Use engineering-standard units (m, ft, ea, kg, etc.).
If a value is not visible, infer a reasonable placeholder and lower the confidence score.
""".strip()


class GeminiMtoPayload(BaseModel):
    """Intermediate schema used for Gemini structured JSON output."""

    drawing_number: str = Field(..., description="Drawing number from the isometric")
    line_number: str = Field(..., description="Piping line identifier")
    items: list[MtoLineItem] = Field(
        default_factory=list,
        description="Extracted material take-off line items",
    )


class GeminiService:
    """Calls Gemini Vision and returns validated MTO extraction results."""

    @staticmethod
    def extract_mto(
        images: list[Image.Image],
        filename: str,
        api_key: str,
    ) -> ExtractionResponse:
        """
        Run Gemini Vision extraction on one or more drawing page images.

        Args:
            images: PIL images prepared from the uploaded PDF or image file.
            filename: Original uploaded filename (included in the API response).
            api_key: Gemini API key.

        Returns:
            Validated `ExtractionResponse` populated from Gemini output.

        Raises:
            ValueError: If no images are supplied or Gemini returns invalid data.
            RuntimeError: If the Gemini API call fails or returns an empty response.
        """
        if not images:
            raise ValueError("At least one drawing image is required for extraction.")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)

        contents: list[object] = [EXTRACTION_PROMPT, *images]

        try:
            response = model.generate_content(
                contents,
                generation_config=GenerationConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=GeminiMtoPayload,
                ),
            )
        except Exception as exc:
            logger.exception("Gemini API request failed for file %s", filename)
            raise RuntimeError("Gemini extraction request failed.") from exc

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        try:
            payload = GeminiMtoPayload.model_validate_json(response.text)
        except ValidationError as exc:
            logger.exception(
                "Gemini JSON failed schema validation for file %s: %s",
                filename,
                response.text,
            )
            raise ValueError("Gemini response did not match the expected MTO schema.") from exc

        # Re-validate line items individually through the canonical API schema.
        validated_items = [MtoLineItem.model_validate(item.model_dump()) for item in payload.items]

        metadata = ExtractionMetadata(
            drawing_number=payload.drawing_number,
            line_number=payload.line_number,
            extracted_at=datetime.now(timezone.utc),
            model=GEMINI_MODEL,
        )

        result = ExtractionResponse(
            success=True,
            filename=filename,
            items=validated_items,
            metadata=metadata,
        )

        # Final guard — ensures the full response conforms to the public API schema.
        ExtractionResponse.model_validate(result.model_dump())
        logger.info(
            "Gemini extraction succeeded for %s with %d item(s)",
            filename,
            len(validated_items),
        )
        return result
