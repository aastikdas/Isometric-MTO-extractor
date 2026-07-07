"""
CSV conversion utilities for MTO extraction exports.
"""

import csv
import io

from app.schemas.extraction import ExtractionResponse


def extraction_to_csv(extraction: ExtractionResponse) -> str:
    """
    Convert an extraction response into an industry-style CSV report.
    """

    output = io.StringIO()
    writer = csv.writer(output)

    # Report Header
    writer.writerow(["Drawing Number", extraction.metadata.drawing_number])
    writer.writerow(["Line Number", extraction.metadata.line_number])
    writer.writerow(
        [
            "Generated At",
            extraction.metadata.extracted_at.strftime("%Y-%m-%d %H:%M:%S"),
        ]
    )
    writer.writerow(["Model", extraction.metadata.model])
    writer.writerow(["Source File", extraction.filename])

    writer.writerow([])

    # MTO Table
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
                f"{item.confidence:.2%}",
            ]
        )

    return "\ufeff" + output.getvalue()
def build_csv_filename(extraction: ExtractionResponse) -> str:
    """Build a safe download filename from the extraction response."""
    stem = extraction.filename.rsplit(".", 1)[0] if "." in extraction.filename else extraction.filename
    safe_stem = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in stem)
    return f"{safe_stem or 'mto'}_export.csv"
