/** Matches backend `MtoLineItem` schema. */
export interface MtoLineItem {
  item_code: string;
  description: string;
  size: string;
  schedule: string;
  quantity: number;
  unit: string;
  confidence: number;
}

/** Matches backend `ExtractionMetadata` schema. */
export interface ExtractionMetadata {
  drawing_number: string;
  line_number: string;
  extracted_at: string;
  model: string;
}

/** Matches backend `ExtractionResponse` schema. */
export interface ExtractionResponse {
  success: boolean;
  filename: string;
  items: MtoLineItem[];
  metadata: ExtractionMetadata;
}
