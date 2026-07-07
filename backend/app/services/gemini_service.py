"""
Gemini Vision service for structured MTO extraction from isometric drawings.

Uses Gemini 2.5 Flash with JSON schema enforcement, then validates the parsed
payload against the existing Pydantic extraction schemas.
"""

from __future__ import annotations

import logging
import json
from datetime import datetime, timezone

from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel, Field, ValidationError

from app.schemas.extraction import ExtractionMetadata, ExtractionResponse, MtoLineItem

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"

EXTRACTION_PROMPT = """
You are a senior piping engineer with expertise in interpreting industrial piping isometric drawings.

Your task is to extract the Material Take-Off (MTO) from the uploaded drawing.

Instructions:

1. Read ONLY information visible in the drawing.
2. Do NOT invent components.
3. If a value is missing, return "N/A".
4. Extract every material item visible.
5. Confidence must be between 0.0 and 1.0.

For every item return:

- item_code
- description
- size
- schedule
- quantity
- unit
- confidence

Also extract:

- drawing_number
- line_number

Return ONLY valid JSON matching the schema.
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
            logger.exception("Gemini request failed.")
            raise RuntimeError("Gemini request failed.") from exc
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        try:
            payload_dict = json.loads(response.text)
            payload = GeminiMtoPayload.model_validate(payload_dict)

        except json.JSONDecodeError as exc:
            logger.exception("Gemini returned invalid JSON.")
            raise RuntimeError("Gemini returned invalid JSON.") from exc

        except ValidationError as exc:
            logger.exception("Gemini returned JSON that does not match the schema.")
            logger.error("Raw Gemini response:\n%s", response.text)
            raise RuntimeError("Gemini returned invalid structured JSON.") from exc
        
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
