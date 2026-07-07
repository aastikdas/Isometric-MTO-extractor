"use client";

import { useRef, useState, type ChangeEvent, type DragEvent } from "react";

import { FILE_INPUT_ACCEPT } from "@/lib/constants";
import { isAllowedFile } from "@/lib/utils/file";

interface FileDropzoneProps {
  selectedFile: File | null;
  onFileSelect: (file: File) => void;
  onInvalidFile: (message: string) => void;
  disabled?: boolean;
}

export function FileDropzone({
  selectedFile,
  onFileSelect,
  onInvalidFile,
  disabled = false,
}: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const validateAndSelect = (file: File | undefined) => {
    if (!file) {
      return;
    }

    if (!isAllowedFile(file)) {
      onInvalidFile("Invalid file type. Please upload a PDF, PNG, JPG, or JPEG.");
      return;
    }

    onFileSelect(file);
  };

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    validateAndSelect(event.target.files?.[0]);
    event.target.value = "";
  };

  const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);

    if (disabled) {
      return;
    }

    validateAndSelect(event.dataTransfer.files?.[0]);
  };

  const openFilePicker = () => {
    if (!disabled) {
      inputRef.current?.click();
    }
  };

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label="Upload isometric drawing"
      aria-disabled={disabled}
      onClick={openFilePicker}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          openFilePicker();
        }
      }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={[
        "flex min-h-52 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition-all",
        isDragging
          ? "border-blue-500 bg-blue-50/80"
          : "border-zinc-300 bg-zinc-50 hover:border-zinc-400 hover:bg-zinc-100",
        disabled ? "pointer-events-none cursor-not-allowed opacity-60" : "",
      ].join(" ")}
    >
      <input
        ref={inputRef}
        type="file"
        accept={FILE_INPUT_ACCEPT}
        className="hidden"
        disabled={disabled}
        onChange={handleInputChange}
      />

      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-white shadow-sm ring-1 ring-zinc-200">
        <svg
          className="h-7 w-7 text-zinc-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M12 16V4m0 0l-4 4m4-4l4 4M4 20h16"
          />
        </svg>
      </div>

      <p className="text-base font-medium text-zinc-900">
        Drag & drop your isometric drawing here
      </p>
      <p className="mt-1 text-sm text-zinc-500">or click to browse files</p>
      <p className="mt-4 text-xs text-zinc-400">PDF, PNG, JPG, JPEG</p>

      {selectedFile && (
        <p className="mt-4 rounded-full bg-white px-4 py-1.5 text-sm font-medium text-zinc-700 ring-1 ring-zinc-200">
          Selected: {selectedFile.name}
        </p>
      )}
    </div>
  );
}
