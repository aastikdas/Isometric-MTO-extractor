"use client";

import { useEffect, useState } from "react";

import { ExtractionResultCard } from "@/components/results/ExtractionResultCard";
import { Spinner } from "@/components/ui/Spinner";
import { FileDropzone } from "@/components/upload/FileDropzone";
import { FilePreview } from "@/components/upload/FilePreview";
import { ExtractApiError, extractMto, NetworkError } from "@/lib/api/extract";
import { API_BASE_URL } from "@/lib/constants";
import type { ExtractionResponse } from "@/lib/types/extraction";
const LOADING_STEPS = [
  "Uploading ...",
  "Converting ...",
  "Analyzing Drawing...",
  "Extracting MTO...",
  "Generating Result...",
];
export function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExtractionResponse | null>(null);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setError(null);
    setResult(null);
    setUploadProgress(0);
  };

  const handleInvalidFile = (message: string) => {
    setError(message);
    setResult(null);
  };

  const handleExtract = async () => {
    if (!selectedFile || isUploading) {
      return;
    }

    setIsUploading(true);
setLoadingStep(0);
setUploadProgress(0);
    setError(null);
    setResult(null);

    try {
      const response = await extractMto(selectedFile, setUploadProgress);
      setResult(response);
      setUploadProgress(100);
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        setError("Upload was cancelled.");
      } else if (err instanceof NetworkError) {
        setError(err.message);
      } else if (err instanceof ExtractApiError) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred during extraction.");
      }
    } finally {
      setIsUploading(false);
      setLoadingStep(0);
    }
  };
  
  const [loadingStep, setLoadingStep] = useState(0);
  
  useEffect(() => {
    if (!isUploading) return;
  
    const interval = setInterval(() => {
      setLoadingStep((prev) =>
        prev < LOADING_STEPS.length - 1 ? prev + 1 : prev
      );
    }, 2800);
  
    return () => clearInterval(interval);
  }, [isUploading]);
  
  return (
    <div className="min-h-full bg-gradient-to-b from-zinc-50 to-zinc-100">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
        <header className="text-center sm:text-left">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">
            Isometric MTO Extractor
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl">
            Upload Drawing
          </h1>
          <p className="mt-3 max-w-2xl text-base text-zinc-600">
            Upload an isometric piping drawing to extract a material take-off (MTO).
            Supported formats: PDF, PNG, JPG, JPEG.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <section className="space-y-6">
            <FileDropzone
              selectedFile={selectedFile}
              onFileSelect={handleFileSelect}
              onInvalidFile={handleInvalidFile}
              disabled={isUploading}
            />

            <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-medium text-zinc-900">Ready to extract</p>
                  <p className="mt-1 text-sm text-zinc-500">
                    {selectedFile
                      ? `Selected file: ${selectedFile.name}`
                      : "Select a drawing to enable extraction."}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={handleExtract}
                  disabled={!selectedFile || isUploading}
                  className="inline-flex min-w-40 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-zinc-300"
                >
                  {isUploading ? (
                    <>
                      <Spinner className="h-4 w-4" label="Extracting" />
                      {LOADING_STEPS[loadingStep]}
                    </>
                  ) : (
                    "Extract MTO"
                  )}
                </button>
              </div>

              {isUploading && (
  <div className="mt-6 rounded-xl border border-blue-100 bg-blue-50 p-5">

    <div className="mb-4 flex items-center gap-3">
      <Spinner className="h-5 w-5" />

      <div>
        <p className="font-semibold text-blue-900">
          {LOADING_STEPS[loadingStep]}
        </p>

        <p className="text-sm text-blue-700">
          AI is processing your drawing...
        </p>
      </div>
    </div>

    <div className="mb-2 flex justify-between text-sm">
      <span>{uploadProgress}%</span>

      <span>
        Step {loadingStep + 1} / {LOADING_STEPS.length}
      </span>
    </div>

    <div className="h-2 overflow-hidden rounded-full bg-blue-100">
      <div
        className="h-full rounded-full bg-blue-600 transition-all duration-500"
        style={{
          width: `${Math.max(
            uploadProgress,
            ((loadingStep + 1) / LOADING_STEPS.length) * 100
          )}%`,
        }}
      />
    </div>

  </div>
)}
            </div>

            {error && (
              <div
                role="alert"
                className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700"
              >
                {error}
              </div>
            )}
          </section>

          <aside>
            <FilePreview file={selectedFile} />
          </aside>
        </div>

        {result && <ExtractionResultCard result={result} />}

        <footer className="text-center text-xs text-zinc-400 sm:text-left">
          Backend: {API_BASE_URL}
        </footer>
      </div>
    </div>
  );
}
