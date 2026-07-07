import { API_BASE_URL } from "@/lib/constants";
import type { ExtractionResponse } from "@/lib/types/extraction";

export class CsvExportError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CsvExportError";
  }
}

/**
 * Download the current extraction result as CSV from GET /export/csv.
 */
export async function downloadCsv(result: ExtractionResponse): Promise<void> {
  const url = `${API_BASE_URL}/export/csv?payload=${encodeURIComponent(JSON.stringify(result))}`;

  let response: Response;

  try {
    response = await fetch(url);
  } catch {
    throw new CsvExportError("Network error — could not download CSV from the backend.");
  }

  if (!response.ok) {
    let message = "CSV export failed.";

    try {
      const body = (await response.json()) as { detail?: string };
      if (typeof body.detail === "string") {
        message = body.detail;
      }
    } catch {
      // Keep generic message when error body is not JSON.
    }

    throw new CsvExportError(message);
  }

  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;

  const contentDisposition = response.headers.get("Content-Disposition");
  const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
  link.download = filenameMatch?.[1] ?? `${result.filename.replace(/\.[^.]+$/, "")}_export.csv`;

  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}
