import { API_BASE_URL } from "@/lib/constants";
import type { ExtractionResponse } from "@/lib/types/extraction";

export class ExtractApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ExtractApiError";
  }
}

export class NetworkError extends Error {
  constructor(message = "Network error — could not reach the backend.") {
    super(message);
    this.name = "NetworkError";
  }
}

/**
 * Parse a FastAPI-style error body into a readable message.
 */
function parseErrorMessage(status: number, responseText: string): string {
  try {
    const body = JSON.parse(responseText) as { detail?: string | { msg: string }[] };

    if (typeof body.detail === "string") {
      return body.detail;
    }

    if (Array.isArray(body.detail) && body.detail.length > 0) {
      return body.detail.map((entry) => entry.msg).join(", ");
    }
  } catch {
    // Fall through to generic message.
  }

  return `Extraction failed with status ${status}.`;
}

/**
 * Upload a drawing to POST /extract with multipart/form-data.
 * Uses XMLHttpRequest so upload progress can be reported.
 */
export function extractMto(
  file: File,
  onProgress: (percent: number) => void,
  signal?: AbortSignal,
): Promise<ExtractionResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append("file", file);

    const handleAbort = () => {
      xhr.abort();
    };

    if (signal) {
      if (signal.aborted) {
        reject(new DOMException("Upload aborted.", "AbortError"));
        return;
      }
      signal.addEventListener("abort", handleAbort);
    }

    xhr.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    });

    xhr.addEventListener("load", () => {
      if (signal) {
        signal.removeEventListener("abort", handleAbort);
      }

      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText) as ExtractionResponse);
        } catch {
          reject(new ExtractApiError("Invalid JSON returned by the backend."));
        }
        return;
      }

      reject(
        new ExtractApiError(parseErrorMessage(xhr.status, xhr.responseText), xhr.status),
      );
    });

    xhr.addEventListener("error", () => {
      if (signal) {
        signal.removeEventListener("abort", handleAbort);
      }
      reject(new NetworkError());
    });

    xhr.addEventListener("abort", () => {
      if (signal) {
        signal.removeEventListener("abort", handleAbort);
      }
      reject(new DOMException("Upload aborted.", "AbortError"));
    });

    xhr.open("POST", `${API_BASE_URL}/extract`);
    xhr.send(formData);
  });
}
