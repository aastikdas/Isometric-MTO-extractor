/** Matches backend `MtoLineItem` schema. */
export interface MtoLineItem {
  category: string;
  description: string;
  size_nps: string;
  schedule_rating: string;
  material_spec: string;
  end_type: string;
  quantity: number;
  unit: string;
  length_m: number | null;
  remarks: string;
  confidence: number;
}

/** Matches backend `ExtractionMetadata` schema. */
export interface ExtractionMetadata {
  drawing_number: string;
  line_number: string;
  revision: string;
  material_class: string;
  nps: string;
  service: string;
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