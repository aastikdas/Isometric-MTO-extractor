"use client";

import { useState } from "react";

import { CsvExportError, downloadCsv } from "@/lib/api/export";
import type { ExtractionResponse } from "@/lib/types/extraction";

interface DownloadCsvButtonProps {
  result: ExtractionResponse;
}

export function DownloadCsvButton({ result }: DownloadCsvButtonProps) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async () => {
    setIsDownloading(true);
    setError(null);

    try {
      await downloadCsv(result);
    } catch (err) {
      if (err instanceof CsvExportError) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred while downloading CSV.");
      }
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="flex flex-col items-end gap-2">
      <button
        type="button"
        onClick={handleDownload}
        disabled={isDownloading}
        className="inline-flex items-center justify-center rounded-xl border border-zinc-200 bg-white px-4 py-2 text-sm font-semibold text-zinc-900 transition-colors hover:bg-zinc-50 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isDownloading ? "Downloading..." : "Download CSV"}
      </button>
      {error && (
        <p className="text-xs text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
