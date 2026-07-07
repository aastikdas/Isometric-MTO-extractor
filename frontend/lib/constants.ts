/** Backend base URL — override via NEXT_PUBLIC_API_URL in .env.local */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";

/** MIME types accepted by the upload page. */
export const ALLOWED_MIME_TYPES = [
  "application/pdf",
  "image/png",
  "image/jpeg",
] as const;

/** File extensions accepted by the upload page. */
export const ALLOWED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg"] as const;

/** Human-readable accept string for the hidden file input. */
export const FILE_INPUT_ACCEPT = ".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg";
