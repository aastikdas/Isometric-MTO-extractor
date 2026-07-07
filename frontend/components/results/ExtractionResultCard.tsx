"use client";

import { useEffect, useMemo } from "react";

import { DownloadCsvButton } from "@/components/results/DownloadCsvButton";
import { PdfIcon } from "@/components/ui/PdfIcon";
import { isImageFile, isPdfFile } from "@/lib/utils/file";
import type { ExtractionResponse, MtoLineItem } from "@/lib/types/extraction";

interface ExtractionResultCardProps {
  result: ExtractionResponse;
  file?: File | null;
}

type ComponentGroup =
  | "pipe"
  | "fitting"
  | "flange"
  | "valve"
  | "bolt"
  | "gasket"
  | "other";

function classifyItem(category: string): ComponentGroup {
  const normalized = category.toLowerCase();

  if (normalized.includes("gasket")) return "gasket";
  if (normalized.includes("bolt")) return "bolt";
  if (normalized.includes("valve")) return "valve";
  if (normalized.includes("flange")) return "flange";
  if (normalized === "pipe" || normalized.includes("pipe run")) return "pipe";
  if (normalized.includes("support") || normalized.includes("instrument")) {
    return "other";
  }

  // Elbows, tees, reducers, caps, weldolets, etc. fall back to fittings.
  return "fitting";
}

function summarizeItems(items: MtoLineItem[]) {
  const totals = {
    pipeLength: 0,
    fittings: 0,
    flanges: 0,
    valves: 0,
    boltSets: 0,
    gaskets: 0,
  };

  for (const item of items) {
    const group = classifyItem(item.category);
    const qty = Number.isFinite(item.quantity) ? item.quantity : 0;

    switch (group) {
      case "pipe":
        totals.pipeLength += item.length_m ?? 0;
        break;
      case "fitting":
        totals.fittings += qty;
        break;
      case "flange":
        totals.flanges += qty;
        break;
      case "valve":
        totals.valves += qty;
        break;
      case "bolt":
        totals.boltSets += qty;
        break;
      case "gasket":
        totals.gaskets += qty;
        break;
      default:
        break;
    }
  }

  return totals;
}

export function ExtractionResultCard({ result, file }: ExtractionResultCardProps) {
  const extractedAt = new Date(result.metadata.extracted_at).toLocaleString();
  const totals = useMemo(() => summarizeItems(result.items), [result.items]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white shadow-sm">
      <div className="flex flex-col gap-4 border-b border-zinc-100 px-6 py-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-zinc-900">Extraction Result</h2>
          <p className="mt-1 text-sm text-zinc-500">
            {result.filename} · {result.metadata.model} · {extractedAt}
          </p>
        </div>
        <DownloadCsvButton result={result} />
      </div>

      {/* Core summary cards */}
      <div className="grid gap-4 px-6 pt-4 sm:grid-cols-2 lg:grid-cols-4">
        <SummaryCard label="Drawing Number" value={result.metadata.drawing_number} />
        <SummaryCard label="Line Number" value={result.metadata.line_number} />
        <SummaryCard label="Model" value={result.metadata.model} />
        <SummaryCard label="Items Found" value={String(result.items.length)} accent="blue" />
      </div>

      {/* Component quantity summary cards */}
      <div className="grid gap-4 px-6 pt-4 sm:grid-cols-3 lg:grid-cols-6">
        <SummaryCard
          label="Pipe Length"
          value={`${totals.pipeLength.toFixed(2)} m`}
          icon="📏"
        />
        <SummaryCard label="Fittings" value={String(totals.fittings)} icon="🔧" />
        <SummaryCard label="Flanges" value={String(totals.flanges)} icon="⭕" />
        <SummaryCard label="Valves" value={String(totals.valves)} icon="🔩" />
        <SummaryCard label="Bolt Sets" value={String(totals.boltSets)} icon="🔗" />
        <SummaryCard label="Gaskets" value={String(totals.gaskets)} icon="⭗" />
      </div>

      {result.items.length === 0 ? (
        <div className="px-6 py-10">
          <div className="mt-4 rounded-2xl border border-dashed border-zinc-300 bg-zinc-50 p-10 text-center">
            <div className="mb-3 text-4xl">📄</div>

            <h3 className="text-lg font-semibold text-zinc-900">
              No MTO items detected
            </h3>

            <p className="mt-2 text-sm text-zinc-600">
              Try another drawing or upload a higher-quality isometric drawing.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 px-6 py-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
          <DrawingPreview file={file} filename={result.filename} />

          <div className="min-w-0 overflow-hidden rounded-xl border border-zinc-100">
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-zinc-100 bg-zinc-50 text-xs uppercase tracking-wide text-zinc-500">
                    <th className="px-3 py-2 font-medium">Category</th>
                    <th className="px-3 py-2 font-medium">Description</th>
                    <th className="px-3 py-2 font-medium">Size</th>
                    <th className="px-3 py-2 font-medium">Schedule</th>
                    <th className="px-3 py-2 font-medium">Material</th>
                    <th className="px-3 py-2 font-medium">End Type</th>
                    <th className="px-3 py-2 font-medium">Quantity</th>
                    <th className="px-3 py-2 font-medium">Unit</th>
                    <th className="px-3 py-2 font-medium">Length</th>
                    <th className="px-3 py-2 font-medium">Confidence</th>
                  </tr>
                </thead>

                <tbody>
                  {result.items.map((item, index) => (
                    <tr
                      key={`${item.category}-${item.description}-${index}`}
                      className="border-b border-zinc-50 last:border-0 hover:bg-zinc-50/60"
                    >
                      <td className="px-3 py-3 font-medium text-zinc-900">
                        {item.category}
                      </td>

                      <td className="px-3 py-3 text-zinc-700">{item.description}</td>

                      <td className="px-3 py-3 text-zinc-700">{item.size_nps}</td>

                      <td className="px-3 py-3 text-zinc-700">
                        {item.schedule_rating}
                      </td>

                      <td className="px-3 py-3 text-zinc-700">
                        {item.material_spec}
                      </td>

                      <td className="px-3 py-3 text-zinc-700">{item.end_type}</td>

                      <td className="px-3 py-3 text-zinc-700">{item.quantity}</td>

                      <td className="px-3 py-3 text-zinc-700">{item.unit}</td>

                      <td className="px-3 py-3 text-zinc-700">
                        {item.length_m != null ? `${item.length_m.toFixed(2)} m` : "—"}
                      </td>

                      <td className="px-3 py-3">
                        <ConfidenceBadge value={item.confidence} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SummaryCard({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: string;
  icon?: string;
  accent?: "blue";
}) {
  return (
    <div
      className={`rounded-xl px-4 py-3 ring-1 ${
        accent === "blue"
          ? "bg-blue-50 ring-blue-100"
          : "bg-zinc-50 ring-zinc-100"
      }`}
    >
      <p className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-zinc-500">
        {icon && <span aria-hidden="true">{icon}</span>}
        {label}
      </p>
      <p
        className={`mt-1 truncate text-sm font-semibold ${
          accent === "blue" ? "text-blue-700" : "text-zinc-900"
        }`}
        title={value}
      >
        {value || "—"}
      </p>
    </div>
  );
}

function ConfidenceBadge({ value }: { value: number }) {
  const percent = Math.round(value * 100);

  let tone: "green" | "yellow" | "red";
  if (value >= 0.85) {
    tone = "green";
  } else if (value >= 0.6) {
    tone = "yellow";
  } else {
    tone = "red";
  }

  const toneClasses: Record<typeof tone, string> = {
    green: "bg-emerald-50 text-emerald-700 ring-emerald-200",
    yellow: "bg-amber-50 text-amber-700 ring-amber-200",
    red: "bg-red-50 text-red-700 ring-red-200",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${toneClasses[tone]}`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          tone === "green"
            ? "bg-emerald-500"
            : tone === "yellow"
              ? "bg-amber-500"
              : "bg-red-500"
        }`}
        aria-hidden="true"
      />
      {percent}%
    </span>
  );
}

function DrawingPreview({
  file,
  filename,
}: {
  file: File | null | undefined;
  filename: string;
}) {
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

  return (
    <div className="flex h-fit flex-col gap-3 rounded-xl border border-zinc-100 bg-zinc-50/50 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
        Uploaded Drawing
      </p>

      {file && isImageFile(file) && previewUrl ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={previewUrl}
          alt={`Preview of ${file.name}`}
          className="w-full rounded-lg border border-zinc-200 bg-white object-contain"
        />
      ) : file && isPdfFile(file) ? (
        <div className="flex flex-col items-center gap-2 rounded-lg border border-zinc-200 bg-white py-8">
          <PdfIcon />
          <p className="text-sm font-medium text-zinc-700">{file.name}</p>
          <p className="text-xs text-zinc-400">PDF document</p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed border-zinc-300 bg-white py-10 text-center">
          <div className="text-3xl">📄</div>
          <p className="text-sm font-medium text-zinc-700">{filename}</p>
          <p className="max-w-[16rem] px-2 text-xs text-zinc-400">
            Original drawing preview is unavailable in this session.
          </p>
        </div>
      )}
    </div>
  );
}