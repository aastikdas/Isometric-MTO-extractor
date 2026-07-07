"use client";

import { useEffect, useMemo } from "react";

import { PdfIcon } from "@/components/ui/PdfIcon";
import { isImageFile, isPdfFile } from "@/lib/utils/file";

interface FilePreviewProps {
  file: File | null;
}

export function FilePreview({ file }: FilePreviewProps) {
  const previewUrl = useMemo(() => {
    if (!file || !isImageFile(file)) {
      return null;
    }

    return URL.createObjectURL(file);
  }, [file]);

  useEffect(() => {
    if (!previewUrl) {
      return;
    }

    return () => {
      URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  if (!file) {
    return null;
  }

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
      <p className="mb-4 text-sm font-medium text-zinc-500">Preview</p>

      {isPdfFile(file) && (
        <div className="flex flex-col items-center gap-3 py-6">
          <PdfIcon />
          <p className="text-sm font-medium text-zinc-700">{file.name}</p>
          <p className="text-xs text-zinc-400">PDF document ready for extraction</p>
        </div>
      )}

      {isImageFile(file) && previewUrl && (
        <div className="flex flex-col items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={previewUrl}
            alt={`Preview of ${file.name}`}
            className="max-h-72 w-full rounded-xl border border-zinc-200 object-contain bg-zinc-50"
          />
          <p className="text-sm font-medium text-zinc-700">{file.name}</p>
        </div>
      )}
    </div>
  );
}
