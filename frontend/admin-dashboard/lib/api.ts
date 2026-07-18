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

<<<<<<< HEAD
  const data = await res.json();

  // Handle DB-unavailable response gracefully
  if (data.error) {
    return [];
  }

  return data;
}
=======
  return res.json();
}

// ==============================
// Fraud Network APIs (Agent 3)
// ==============================

export async function getMoneyMules() {
  const res = await fetch(
    `${BASE_URL}/fraud/money-mules`,
    {
      cache: "no-store",
    }
  );

  if (!res.ok)
    throw new Error("Failed to fetch money mules");

  return res.json();
}

export async function getFraudRings() {
  const res = await fetch(
    `${BASE_URL}/fraud/rings`,
    {
      cache: "no-store",
    }
  );

  if (!res.ok)
    throw new Error("Failed to fetch fraud rings");

  return res.json();
}

export async function getMoneyFlow(
  accountNumber: string
) {
  const res = await fetch(
    `${BASE_URL}/fraud/money-flow/${accountNumber}`,
    {
      cache: "no-store",
    }
  );

  if (!res.ok)
    throw new Error("Failed to fetch money flow");

  return res.json();
}

export async function getShortestPath(
  source: string,
  target: string
) {
  const res = await fetch(
    `${BASE_URL}/fraud/shortest-path/${source}/${target}`,
    {
      cache: "no-store",
    }
  );

  if (!res.ok)
    throw new Error("Failed to fetch shortest path");

  return res.json();
}
>>>>>>> origin/main
