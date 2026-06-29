export interface URLAnalysisResponse {
  url: string;
  domain: string;

  features: Record<string, any>;

  safe_browsing: Record<string, any>;

  blacklists: Record<string, boolean>;

  ml_probability: number;

  risk_score: number;

  risk_level: string;

  recommendation: string;

  signals: string[];
}

export interface SMSResponse {
  message: string;

  contains_url: boolean;

  urls: string[];

  keyword_count: number;

  risk_score: number;

  risk_level: string;

  recommendation: string;

  signals: string[];
}

export interface DetectionHistory {
  id: number;

  scan_type: string;

  input_text: string;

  risk_score: number;

  risk_level: string;

  recommendation: string;

  ml_probability: number;

  signals: string[];

  created_at: string;
}

export interface DetectionStats {
  total_scans: number;

  scan_types: Record<string, number>;

  risk_levels: Record<string, number>;
}