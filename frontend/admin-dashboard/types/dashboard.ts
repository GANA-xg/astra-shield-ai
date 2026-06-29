export interface Detection {
  id: number;
  scan_type: string;
  input_text: string;
  risk_score: number;
  risk_level: string;
  recommendation: string;
  created_at: string;
}

export interface DashboardStats {
  total_scans: number;
  scan_types: Record<string, number>;
  risk_levels: Record<string, number>;
}