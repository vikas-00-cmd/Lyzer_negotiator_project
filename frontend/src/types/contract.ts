export interface ContractPayload {
  id: string;
  session_id: string;
  final_price: number;
  final_delivery_days: number;
  final_sla_percent: number;
  pdf_file_path: string;
  created_at: string;
}

export interface ContractDetails {
  id: string;
  session_id: string;
  final_price: number;
  final_delivery_days: number;
  final_sla_percent: number;
  pdf_file_path: string;
  created_at: string;
}
