import { DashboardStats, Detection } from "@/types/dashboard";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getStats(): Promise<DashboardStats> {
  const res = await fetch(
    `${BASE_URL}/api/phishing/stats`,
    {
      cache: "no-store",
    }
  );

  if (!res.ok)
    throw new Error("Failed to fetch stats");

  const data = await res.json();

  // Handle DB-unavailable response gracefully
  if (data.error) {
    return { total_scans: 0, scan_types: {}, risk_levels: {} };
  }

  return data;
}

export async function getHistory(): Promise<Detection[]> {
  const res = await fetch(
    `${BASE_URL}/api/phishing/history`,
    {
      cache: "no-store",
    }
  );

  if (!res.ok)
    throw new Error("Failed to fetch history");

  const data = await res.json();

  // Handle DB-unavailable response gracefully
  if (data.error) {
    return [];
  }

  return data;
}
