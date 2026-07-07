 
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
You are a senior piping engineer with 20+ years of experience reading industrial
piping isometric drawings and producing Material Take-Off (MTO) reports.
 
Your job is to carefully read the attached isometric drawing image(s) and return
a COMPLETE, STRUCTURED extraction. Isometric drawings encode information in
several places — read ALL of them before answering:
 
- The title block / drawing border (drawing number, line number, revision,
  material class, sheet NPS, service/fluid). Drawing numbers are often split
  across a "Dwg No." cell and a separate sheet/format suffix cell — read them
  as one continuous string exactly as printed, preserving internal spaces and
  separators (e.g. "/", "-", "."). Examples of valid formats: "XTPL/F 17",
  "ISO-4521-002", "6\"-P-1234-A1A-H Sh.2". Do not drop the sheet/suffix part
  after a slash or space, and do not silently convert a "/" to a "-" or
  vice versa.
- The line number string itself, which is usually formatted like
  "6"-P-1234-A1A-H" or similar. Decode it: pipe size, sequence number,
  material class code, insulation/other suffix.
- The Bill of Materials / MTO table printed on the sheet, if present. This is
  usually the most reliable source for item, size, spec, and quantity — prefer
  it over inferring from the drawing body when both are present.
- Component bubbles/callouts and leader lines on the isometric body itself
  (elbows, tees, reducers, flanges, valves, gaskets, bolts, supports,
  instruments, weld symbols, end-connection symbols).
- Dimension strings and pipe run lengths along the isometric legs.
 
FIELD-BY-FIELD GUIDANCE (apply this reasoning before writing "Unknown"):
 
- category: the component type, e.g. "Pipe", "Elbow 90", "Elbow 45", "Tee",
  "Reducer", "Flange", "Gasket", "Bolt/Nut Set", "Gate Valve", "Ball Valve",
  "Check Valve", "Cap", "Weldolet", "Support", "Instrument". Infer this from
  the component symbol/shape and any adjacent tag, even if no text label
  exists next to it.
- description: a short, human-readable description as it would appear on an
  MTO line (component + key attributes), not just a repeated code.
- size_nps: the nominal size of THIS SPECIFIC ITEM (e.g. 4", 2"x1" for a
  reducer). If the item shares the header line size and no separate size is
  called out, use the line's NPS.
- schedule_rating: pipe schedule (SCH 40, SCH 80, STD, XS) for pipe, or
  pressure/flange class (150#, 300#, 600#) for flanges/valves.
- material_spec: material grade/spec (e.g. A106 Gr B, A234 WPB, A105, A193
  B7, SS316, LTCS). Piping material classes in the title block (e.g. "A1A")
  often map to a base material spec noted in the drawing legend — use that
  mapping when visible; otherwise use the class code itself rather than
  "Unknown".
- end_type: BW (butt weld), SW (socket weld), THD (threaded), FLG (flanged).
  Infer from the weld symbol drawn at each joint even if not spelled out.
- quantity: a numeric count (or running length count) for this item. Never
  leave this as text — estimate conservatively from the drawing if an exact
  BOM count is not printed, and lower the confidence score accordingly.
- unit: "ea" for discrete components, "m" for pipe measured by length.
- length_m: only for pipe runs where a length dimension is shown or
  computable from dimension strings; convert to meters. Leave null (not the
  string "Unknown") for discrete components with no length dimension.
- remarks: field notes, insulation/PWHT/NDE callouts, or any annotation tied
  to this item. Use "Unknown" only if the field is genuinely inapplicable.
- confidence: 0.0-1.0 reflecting how directly the value was read (1.0 = read
  verbatim from a BOM table or clear label) vs inferred (lower, e.g. 0.4-0.6
  for a visually-inferred quantity or symbol).
 
DRAWING-LEVEL METADATA:
 
- drawing_number: the complete drawing number/format code from the title
  block, transcribed character-for-character (including "/", "-", spaces,
  and any sheet suffix, e.g. "XTPL/F 17"). Check the title block cell(s)
  labelled "Dwg No.", "Drawing No.", "Doc No.", or "Format No." — the value
  may span two adjacent cells (a code plus a sheet/format letter+number);
  concatenate them in the order printed rather than picking only one cell.
  Only fall back to "Unknown" if no such cell is legible anywhere on the sheet.
- line_number: the full piping line number/tag as printed.
- revision: revision letter/number from the title block or revision cloud.
- material_class: the piping class/spec code from the title block or line
  number (e.g. "A1A", "150-CS").
- nps: the overall header nominal size for the line.
- service: the process fluid/service (e.g. "Cooling Water", "Steam",
  "Crude Oil") from the title block or line description.
 
RULES:
 
1. Read ONLY information visible in the drawing (title block, BOM table,
   callouts, symbols, dimensions). Do not invent components that aren't
   depicted.
2. NEVER return "N/A". If a value is genuinely not present or determinable
   anywhere on the sheet after checking the title block, BOM table, and
   drawing body, return the exact string "Unknown" for text fields, or null
   for numeric fields that don't apply (length_m only).
3. Prefer a real value over "Unknown" whenever the information is
   derivable from context (line number decoding, symbol shape, legend,
   standard piping conventions) — only fall back to "Unknown" after
   genuinely checking.
4. Extract every material item visible, in reading order (top-to-bottom,
   left-to-right), up to a maximum of 20 items. Do not summarize omitted
   items if there are more than 20 — just stop at 20.
5. Keep descriptions concise (a short MTO-style phrase, not a sentence).
6. Return ONLY valid JSON matching the provided schema — no commentary.
""".strip()
 
 
class GeminiMtoPayload(BaseModel):
    """Intermediate schema used for Gemini structured JSON output."""
 
    drawing_number: str = Field(
        ...,
        description=(
            "Complete drawing number from the title block, transcribed exactly "
            "as printed including slashes, hyphens, and spaces, and including "
            "any sheet/format suffix (e.g. 'XTPL/F 17')."
        ),
    )
    line_number: str = Field(..., description="Piping line identifier")
    revision: str = Field(..., description="Drawing revision, e.g. Rev A, Rev 2")
    material_class: str = Field(..., description="Piping material class/spec code")
    nps: str = Field(..., description="Overall/header nominal pipe size of the line")
    service: str = Field(..., description="Process service/fluid")
    items: list[MtoLineItem] = Field(
        default_factory=list,
        description="Extracted material take-off line items",
    )
 
 
def _extract_json_text(text: str) -> str:
    """
    Return the JSON payload from a Gemini text response.
 
    Even with `response_mime_type="application/json"`, Gemini occasionally
    wraps the payload in a ```json ... ``` fence or adds surrounding
    whitespace. Strip that defensively so a cosmetic wrapper doesn't cause an
    otherwise-valid response to be treated as a parse failure.
    """
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:]
        stripped = stripped.strip()
    return stripped
 
 
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
            logger.info("Calling Gemini...")
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=GeminiMtoPayload,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    max_output_tokens=65535,
                ),
            )
            logger.info("Gemini usage: %s", response.usage_metadata)
 
            if response.candidates:
                logger.info("Finish reason: %s", response.candidates[0].finish_reason)
            logger.info("Gemini returned a response")
        except Exception as exc:
            logger.exception("Gemini request failed.")
            raise RuntimeError("Gemini request failed.") from exc
 
        # If Gemini hit the token cap before finishing, response.text can be
        # None or a truncated JSON fragment. Surface this distinctly instead of
        # letting it fall through to a generic/confusing JSON-parse error.
        candidates = response.candidates or []
        if candidates and candidates[0].finish_reason == types.FinishReason.MAX_TOKENS:
            logger.error(
                "Gemini hit the max_output_tokens limit before finishing the response."
            )
            raise RuntimeError(
                "Gemini response was truncated (max output tokens reached)."
            )
 
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
 
        raw_text = _extract_json_text(response.text)
 
        try:
            payload_dict = json.loads(raw_text)
            payload = GeminiMtoPayload.model_validate(payload_dict)
 
        except json.JSONDecodeError as exc:
            logger.exception("Gemini returned invalid JSON.")
            logger.error("Raw Gemini response:\n%s", response.text)
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
            revision=payload.revision,
            material_class=payload.material_class,
            nps=payload.nps,
            service=payload.service,
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