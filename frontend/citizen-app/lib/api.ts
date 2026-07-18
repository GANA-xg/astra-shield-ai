import {
  URLAnalysisResponse,
  SMSResponse,
  DetectionHistory,
  DetectionStats,
} from "@/types/phishing";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function analyzeURL(
  url: string
): Promise<URLAnalysisResponse> {
  const response = await fetch(
    `${BASE_URL}/api/phishing/analyze-url`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        url,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to analyze URL");
  }

  return response.json();
}

export async function analyzeSMS(
  message: string
): Promise<SMSResponse> {
  const response = await fetch(
    `${BASE_URL}/api/phishing/check-sms`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        message,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to analyze SMS");
  }

  return response.json();
}

export async function getHistory(): Promise<DetectionHistory[]> {
  try {
    const response = await fetch(
      `${BASE_URL}/api/phishing/history`
    );

    if (!response.ok) {
      console.warn("Failed to fetch history, returning empty");
      return [];
    }

    const data = await response.json();

    // Handle DB-unavailable response gracefully
    if (data && data.error) {
      return [];
    }

    return data;
  } catch (err) {
    console.error("getHistory error:", err);
    return [];
  }
}

export async function getStats(): Promise<DetectionStats> {
  try {
    const response = await fetch(
      `${BASE_URL}/api/phishing/stats`
    );

    if (!response.ok) {
      console.warn("Failed to fetch stats, returning zeros");
      return { total_scans: 0, scan_types: {}, risk_levels: {} };
    }

    const data = await response.json();

    // Handle DB-unavailable response gracefully
    if (data && data.error) {
      return { total_scans: 0, scan_types: {}, risk_levels: {} };
    }

    return data;
  } catch (err) {
    console.error("getStats error:", err);
    return { total_scans: 0, scan_types: {}, risk_levels: {} };
  }
}