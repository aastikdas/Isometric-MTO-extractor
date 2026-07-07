import { DownloadCsvButton } from "@/components/results/DownloadCsvButton";
import type { ExtractionResponse } from "@/lib/types/extraction";

interface ExtractionResultCardProps {
  result: ExtractionResponse;
}

export function ExtractionResultCard({ result }: ExtractionResultCardProps) {
  const extractedAt = new Date(result.metadata.extracted_at).toLocaleString();

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

      <div className="grid gap-4 px-6 py-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetadataItem label="Drawing Number" value={result.metadata.drawing_number} />
        <MetadataItem label="Line Number" value={result.metadata.line_number} />
        <MetadataItem label="Revision" value={result.metadata.revision} />
        <MetadataItem label="Material Class" value={result.metadata.material_class} />
        <MetadataItem label="NPS" value={result.metadata.nps} />
        <MetadataItem label="Service" value={result.metadata.service} />
        <MetadataItem label="Model" value={result.metadata.model} />
        <MetadataItem label="Items Found" value={String(result.items.length)} />
      </div>
      {result.items.length === 0 ? (
  <div className="border-t border-zinc-100 px-6 py-10">
    <div className="rounded-2xl border border-dashed border-zinc-300 bg-zinc-50 p-10 text-center">
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
  <div className="overflow-x-auto border-t border-zinc-100 px-6 py-4">
    <table className="min-w-full text-left text-sm">
      <thead>
        <tr className="border-b border-zinc-100 text-xs uppercase tracking-wide text-zinc-500">
          <th className="px-3 py-2 font-medium">Category</th>
          <th className="px-3 py-2 font-medium">Description</th>
          <th className="px-3 py-2 font-medium">Size (NPS)</th>
          <th className="px-3 py-2 font-medium">Schedule/Rating</th>
          <th className="px-3 py-2 font-medium">Material Spec</th>
          <th className="px-3 py-2 font-medium">End Type</th>
          <th className="px-3 py-2 font-medium">Qty</th>
          <th className="px-3 py-2 font-medium">Unit</th>
          <th className="px-3 py-2 font-medium">Confidence</th>
        </tr>
      </thead>

      <tbody>
        {result.items.map((item, index) => (
          <tr
            key={`${item.category}-${item.description}-${index}`}
            className="border-b border-zinc-50 last:border-0"
          >
            <td className="px-3 py-3 font-medium text-zinc-900">
              {item.category}
            </td>

            <td className="px-3 py-3 text-zinc-700">
              {item.description}
            </td>

            <td className="px-3 py-3 text-zinc-700">{item.size_nps}</td>

            <td className="px-3 py-3 text-zinc-700">
              {item.schedule_rating}
            </td>

            <td className="px-3 py-3 text-zinc-700">
              {item.material_spec}
            </td>

            <td className="px-3 py-3 text-zinc-700">{item.end_type}</td>

            <td className="px-3 py-3 text-zinc-700">
              {item.quantity}
            </td>

            <td className="px-3 py-3 text-zinc-700">{item.unit}</td>

            <td className="px-3 py-3 text-zinc-700">
              {(item.confidence * 100).toFixed(0)}%
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
)}
      <div className="border-t border-zinc-100 px-6 py-4">
        <p className="mb-2 text-sm font-medium text-zinc-700">Raw JSON Response</p>
        <pre className="overflow-x-auto rounded-xl bg-zinc-950 p-4 text-xs leading-relaxed text-zinc-100">
          {JSON.stringify(result, null, 2)}
        </pre>
      </div>
    </div>
  );
}

function MetadataItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-zinc-50 px-4 py-3 ring-1 ring-zinc-100">
      <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-zinc-900">{value}</p>
    </div>
  );
}