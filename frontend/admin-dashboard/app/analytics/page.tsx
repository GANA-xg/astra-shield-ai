"use client";

import { useEffect, useState } from "react";

import Sidebar from "@/components/Sidebar";
import Topbar from "@/components/Topbar";

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

  if (!stats)
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
        Loading analytics...
      </main>
    );

  const scanData = [
    {
      name: "URL",
      value: stats.scan_types.url ?? 0,
    },
    {
      name: "SMS",
      value: stats.scan_types.sms ?? 0,
    },
  ];

  const riskData = Object.entries(stats.risk_levels).map(
    ([name, value]) => ({
      name,
      value,
    })
  );

  const trendMap = new Map<string, number>();

  history.forEach((item) => {
    const day = new Date(item.created_at).toLocaleDateString();

    trendMap.set(day, (trendMap.get(day) ?? 0) + 1);
  });

  const trendData = Array.from(trendMap.entries()).map(
    ([day, count]) => ({
      day,
      count,
    })
  );

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950">

      <div className="flex">

        <Sidebar />

        <div className="flex-1 p-8">

          <Topbar />

          <h1 className="mt-8 mb-8 text-4xl font-extrabold text-white">
            📈 Threat Analytics
          </h1>

          <div className="grid gap-8 xl:grid-cols-2">

            <ThreatLineChart data={trendData} />

            <RiskPieChart data={riskData} />

          </div>

          <div className="mt-8">

            <ScanBarChart data={scanData} />

          </div>

        </div>

      </div>

    </main>
  );
}