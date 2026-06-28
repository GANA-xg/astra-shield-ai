import {
  URLAnalysisResponse,
  SMSResponse,
  DetectionHistory,
  DetectionStats,
} from "@/types/phishing";

const BASE_URL = "http://127.0.0.1:8000";

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
  const response = await fetch(
    `${BASE_URL}/api/phishing/history`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch history");
  }

  return response.json();
}

export async function getStats(): Promise<DetectionStats> {
  const response = await fetch(
    `${BASE_URL}/api/phishing/stats`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch stats");
  }

  return response.json();
}