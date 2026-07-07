"""
Gemini Vision service for structured MTO extraction from isometric drawings.

Uses Gemini 2.5 Flash with JSON schema enforcement, then validates the parsed
payload against the existing Pydantic extraction schemas.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel, Field, ValidationError

from app.schemas.extraction import ExtractionMetadata, ExtractionResponse, MtoLineItem

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"

EXTRACTION_PROMPT = """
You are an expert piping engineer.

Extract the material take-off (MTO) from the drawing.

Return ONLY valid JSON.

Extract a maximum of 20 line items.

JSON format:

{
  "drawing_number": "...",
  "line_number": "...",
  "items": [
    {
      "item_code": "...",
      "description": "...",
      "size": "...",
      "schedule": "...",
      "quantity": 0,
      "unit": "...",
      "confidence": 0.95
    }
  ]
}
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

        client = genai.Client(api_key=api_key)

        contents: list[object] = [EXTRACTION_PROMPT, *images]

        try:
            print("Calling Gemini...")
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=GeminiMtoPayload,
                ),
            )
            print("Gemini returned a response")
            print(response.text.count('"item_code"'))
        except Exception as exc:
            import traceback

            traceback.print_exc()
            print("=" * 80)
            print("ACTUAL GEMINI ERROR:")
            print(type(exc))
            print(exc)
            print("=" * 80)

            raise
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        if response.parsed is None:
            logger.error("Raw Gemini response: %s", response.text)
            raise RuntimeError("Gemini did not return valid structured JSON.")

        payload = response.parsed
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
