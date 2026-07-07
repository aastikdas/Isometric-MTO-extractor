"""
CSV conversion utilities for MTO extraction exports.
"""

import csv
import io

from app.schemas.extraction import ExtractionResponse


def extraction_to_csv(extraction: ExtractionResponse) -> str:
    """
    Convert an extraction response into a downloadable CSV string.

    Includes drawing metadata followed by MTO line items.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Filename", extraction.filename])
    writer.writerow(["Drawing Number", extraction.metadata.drawing_number])
    writer.writerow(["Line Number", extraction.metadata.line_number])
    writer.writerow(["Model", extraction.metadata.model])
    writer.writerow(["Extracted At", extraction.metadata.extracted_at.isoformat()])
    writer.writerow([])

    writer.writerow(
        [
            "Item Code",
            "Description",
            "Size",
            "Schedule",
            "Quantity",
            "Unit",
            "Confidence",
        ]
    )

    for item in extraction.items:
        writer.writerow(
            [
                item.item_code,
                item.description,
                item.size,
                item.schedule,
                item.quantity,
                item.unit,
                item.confidence,
            ]
        )

    # UTF-8 BOM helps Excel open the file with correct encoding.
    return f"\ufeff{output.getvalue()}"


def build_csv_filename(extraction: ExtractionResponse) -> str:
    """Build a safe download filename from the extraction response."""
    stem = extraction.filename.rsplit(".", 1)[0] if "." in extraction.filename else extraction.filename
    safe_stem = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in stem)
    return f"{safe_stem or 'mto'}_export.csv"
