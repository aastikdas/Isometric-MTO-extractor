
"""
Extraction service — orchestrates MTO extraction from isometric drawings.
 
Attempts Gemini Vision extraction when configured; falls back to deterministic
mock data if the API key is missing or Gemini processing fails.
"""
 
from __future__ import annotations
 
import asyncio
import io
import logging
import mimetypes
from datetime import datetime, timezone
 
from pdf2image import convert_from_bytes
from PIL import Image, UnidentifiedImageError
 
from app.config import get_settings
from app.schemas.extraction import ExtractionMetadata, ExtractionResponse, MtoLineItem
from app.services.gemini_service import GeminiService
 
logger = logging.getLogger(__name__)
 
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
ALLOWED_IMAGE_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/gif",
    "image/bmp",
    "image/tiff",
    "image/x-tiff",
}
PDF_MIME_TYPES = {"application/pdf"}
PDF_EXTENSION = ".pdf"
 
 
class ExtractionService:
    """Service layer for isometric drawing MTO extraction."""
 
    @staticmethod
    def generate_mock_extraction(filename: str) -> ExtractionResponse:
        """
        Return a mock extraction result for development and assessment.
 
        Args:
            filename: Original name of the uploaded drawing file.
 
        Returns:
            A fully populated `ExtractionResponse` with sample line items.
        """
        return ExtractionResponse(
            success=True,
            filename=filename,
            items=[
                MtoLineItem(
                    category="Pipe",
                    description="Carbon Steel Pipe",
                    size_nps='4"',
                    schedule_rating="STD",
                    material_spec="A106 Gr B",
                    end_type="BW",
                    quantity=12.5,
                    unit="m",
                    length_m=12.5,
                    confidence=0.95,
                ),
                MtoLineItem(
                    category="Elbow 90",
                    description="90° Long Radius Elbow",
                    size_nps='4"',
                    schedule_rating="STD",
                    material_spec="A234 WPB",
                    end_type="BW",
                    quantity=2,
                    unit="ea",
                    confidence=0.92,
                ),
                MtoLineItem(
                    category="Flange",
                    description="Weld Neck Flange",
                    size_nps='4"',
                    schedule_rating="150#",
                    material_spec="A105",
                    end_type="FLG",
                    quantity=2,
                    unit="ea",
                    confidence=0.88,
                ),
                MtoLineItem(
                    category="Gate Valve",
                    description="Gate Valve",
                    size_nps='4"',
                    schedule_rating="150#",
                    material_spec="A105",
                    end_type="FLG",
                    quantity=1,
                    unit="ea",
                    confidence=0.91,
                ),
            ],
            metadata=ExtractionMetadata(
                drawing_number="ISO-1234-001",
                line_number="L-101",
                extracted_at=datetime.now(timezone.utc),
                model="mock",
            ),
        )
 
    @staticmethod
    def _resolve_content_type(filename: str, content_type: str | None) -> str:
        """Resolve a MIME type from the upload metadata and filename extension."""
        if content_type and content_type != "application/octet-stream":
            return content_type.lower()
 
        guessed_type, _ = mimetypes.guess_type(filename)
        return (guessed_type or "application/octet-stream").lower()
 
    @staticmethod
    def _is_pdf(filename: str, content_type: str) -> bool:
        """Return True when the upload should be treated as a PDF."""
        return filename.lower().endswith(PDF_EXTENSION) or content_type in PDF_MIME_TYPES
 
    @staticmethod
    def _is_image(filename: str, content_type: str) -> bool:
        """Return True when the upload should be treated as a raster image."""
        extension = _file_extension(filename)
        return extension in ALLOWED_IMAGE_EXTENSIONS or content_type in ALLOWED_IMAGE_MIME_TYPES
 
    @staticmethod
    def prepare_images(content: bytes, filename: str, content_type: str | None) -> list[Image.Image]:
        """
        Convert uploaded PDF or image bytes into PIL images for Gemini Vision.
 
        Args:
            content: Raw uploaded file bytes.
            filename: Original uploaded filename.
            content_type: MIME type reported by the client.
 
        Returns:
            A list of PIL images (one per PDF page, or a single image upload).
 
        Raises:
            ValueError: If the file type is unsupported or cannot be decoded.
        """
        resolved_type = ExtractionService._resolve_content_type(filename, content_type)
 
        if ExtractionService._is_pdf(filename, resolved_type):
            try:
                images = convert_from_bytes(
                    content,
                    dpi=200,
                    fmt="png",
                    poppler_path=get_settings().poppler_path or None,
                )
            except Exception as exc:
                logger.exception("Failed to convert PDF to images for file %s", filename)
                raise ValueError("Unable to convert PDF to images.") from exc
 
            if not images:
                raise ValueError("PDF upload did not contain any pages.")
 
            return images
 
        if ExtractionService._is_image(filename, resolved_type):
            try:
                image = Image.open(io.BytesIO(content))
                return [image.convert("RGB")]
            except UnidentifiedImageError as exc:
                raise ValueError("Unable to decode uploaded image file.") from exc
 
        raise ValueError(
            "Unsupported file type. Upload a PDF or image (PNG, JPG, JPEG, WEBP, GIF, BMP, TIFF)."
        )
 
    @staticmethod
    async def extract_mto(
        filename: str,
        content: bytes,
        content_type: str | None,
    ) -> ExtractionResponse:
        """
        Extract MTO data from an uploaded drawing, with Gemini-first fallback logic.
 
        Args:
            filename: Original uploaded filename.
            content: Raw uploaded file bytes.
            content_type: MIME type reported by the client.
 
        Returns:
            Validated extraction response from Gemini or the mock fallback service.
        """
        settings = get_settings()
 
        if not settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY is missing; using mock extraction for %s", filename)
            return ExtractionService.generate_mock_extraction(filename=filename)
 
        try:
            images = ExtractionService.prepare_images(
                content=content,
                filename=filename,
                content_type=content_type,
            )
            return await asyncio.to_thread(
                GeminiService.extract_mto,
                images,
                filename,
                settings.gemini_api_key,
            )
        except ValueError:
            # Propagate client-facing validation errors (unsupported file type, etc.).
            raise
        except Exception:
            logger.exception(
                "Gemini extraction failed for %s; falling back to mock extraction",
                filename,
            )
            return ExtractionService.generate_mock_extraction(filename=filename)
 
 
def _file_extension(filename: str) -> str:
    """Return the lowercase file extension including the leading dot."""
    dot_index = filename.rfind(".")
    if dot_index == -1:
        return ""
    return filename[dot_index:].lower()