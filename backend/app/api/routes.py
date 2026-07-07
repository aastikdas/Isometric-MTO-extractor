"""
HTTP route definitions for the Isometric MTO Extractor API.

Routes are kept thin — business logic lives in the services layer.
"""

from typing import Any

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import ValidationError

from app.schemas.extraction import ExtractionResponse
from app.services.extraction_service import ExtractionService
from app.utils.csv_utils import build_csv_filename, extraction_to_csv

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Liveness probe — confirms the API process is running.

    Returns:
        A simple JSON payload with status and service name.
    """
    return {
        "status": "ok",
        "service": "isometric-mto-extractor",
    }


@router.post("/extract", response_model=ExtractionResponse)
async def extract_mto(
    file: UploadFile = File(..., description="Isometric drawing (PDF or image)"),
) -> ExtractionResponse:
    """
    Extract a material take-off (MTO) from an uploaded isometric drawing.

    Accepts a PDF or image upload. Uses Gemini Vision when configured and falls
    back to mock data if the API key is missing or extraction fails.

    Args:
        file: The uploaded isometric drawing file.

    Returns:
        Structured MTO line items and extraction metadata.
    """
    filename = file.filename or "unknown"
    content = await file.read()

    try:
        return await ExtractionService.extract_mto(
            filename=filename,
            content=content,
            content_type=file.content_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/export/csv")
async def export_csv(
    payload: str = Query(
        ...,
        description="URL-encoded JSON representation of an ExtractionResponse",
    ),
) -> Response:
    """
    Export a material take-off extraction result as a downloadable CSV file.

    Args:
        payload: JSON-encoded `ExtractionResponse` from a prior `/extract` call.

    Returns:
        CSV file attachment containing metadata and line items.
    """
    try:
        extraction = ExtractionResponse.model_validate_json(payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid extraction payload for CSV export.",
        ) from exc

    csv_content = extraction_to_csv(extraction)
    download_name = build_csv_filename(extraction)

    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
    )
