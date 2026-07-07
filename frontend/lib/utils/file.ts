import { ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES } from "@/lib/constants";

/**
 * Returns the lowercase file extension including the leading dot.
 */
export function getFileExtension(filename: string): string {
  const dotIndex = filename.lastIndexOf(".");
  if (dotIndex === -1) {
    return "";
  }
  return filename.slice(dotIndex).toLowerCase();
}

/**
 * Validates that a file is an allowed PDF or image type.
 */
export function isAllowedFile(file: File): boolean {
  const extension = getFileExtension(file.name);
  const hasAllowedExtension = ALLOWED_EXTENSIONS.includes(
    extension as (typeof ALLOWED_EXTENSIONS)[number],
  );
  const hasAllowedMime =
    file.type === "" ||
    ALLOWED_MIME_TYPES.includes(file.type as (typeof ALLOWED_MIME_TYPES)[number]);

  return hasAllowedExtension && hasAllowedMime;
}

/**
 * Returns true when the file should be previewed as a raster image.
 */
export function isImageFile(file: File): boolean {
  const extension = getFileExtension(file.name);
  return [".png", ".jpg", ".jpeg"].includes(extension);
}

/**
 * Returns true when the file is a PDF.
 */
export function isPdfFile(file: File): boolean {
  return (
    getFileExtension(file.name) === ".pdf" ||
    file.type === "application/pdf"
  );
}
