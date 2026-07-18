"use client";

import { useEffect, useState } from "react";
import AdminLayout from "@/components/AdminLayout";
import ThreatLineChart from "@/components/charts/LineChart";
import RiskPieChart from "@/components/charts/PieChart";
import ScanBarChart from "@/components/charts/BarChart";
import { getHistory, getStats } from "@/lib/api";
import { DashboardStats, Detection } from "@/types/dashboard";

export default function AnalyticsPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [history, setHistory] = useState<Detection[]>([]);

  useEffect(() => {
    async function load() {
      try {
        const [statsData, historyData] = await Promise.all([
          getStats(),
          getHistory(),
        ]);
        setStats(statsData);
        setHistory(historyData);
      } catch (err) {
        console.error(err);
      }
    }
    load();
  }, []);

  if (!stats) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center text-[var(--body)]">
          Loading analytics...
        </div>
      </AdminLayout>
    );
  }

  const scanData = [
    { name: "URL", value: stats.scan_types.url ?? 0 },
    { name: "SMS", value: stats.scan_types.sms ?? 0 },
  ];

  const riskData = Object.entries(stats.risk_levels).map(([name, value]) => ({
    name,
    value,
  }));

  const trendMap = new Map<string, number>();
  history.forEach((item) => {
    const day = new Date(item.created_at).toLocaleDateString();
    trendMap.set(day, (trendMap.get(day) ?? 0) + 1);
  });
  const trendData = Array.from(trendMap.entries()).map(([day, count]) => ({
    day,
    count,
  }));

  return (
    <AdminLayout>
      <h1 className="mb-6 text-2xl font-semibold text-[var(--ink)]">Threat Analytics</h1>

      <div className="grid gap-6 xl:grid-cols-2 mb-6">
        <ThreatLineChart data={trendData} />
        <RiskPieChart data={riskData} />
      </div>

      <ScanBarChart data={scanData} />
    </AdminLayout>
  );
}
