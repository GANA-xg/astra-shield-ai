"use client";

import { useEffect, useState } from "react";

import Sidebar from "@/components/Sidebar";
import Topbar from "@/components/Topbar";

import { getHistory, getStats } from "@/lib/api";
import { DashboardStats, Detection } from "@/types/dashboard";

export default function ReportsPage() {
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

  const exportCSV = () => {
    const headers = [
      "ID",
      "Type",
      "Risk",
      "Score",
      "Input",
      "Recommendation",
      "Created At",
    ];

    const rows = history.map((d) => [
      d.id,
      d.scan_type,
      d.risk_level,
      d.risk_score,
      `"${d.input_text.replace(/"/g, '""')}"`,
      `"${d.recommendation.replace(/"/g, '""')}"`,
      d.created_at,
    ]);

    const csv = [headers, ...rows]
      .map((r) => r.join(","))
      .join("\n");

    const blob = new Blob([csv], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = "astra-shield-report.csv";

    link.click();

    URL.revokeObjectURL(url);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950">

      <div className="flex">

        <Sidebar />

        <div className="flex-1 p-8">

          <Topbar />

          <h1 className="mt-8 text-4xl font-bold text-white">
            📄 Reports
          </h1>

          <p className="mt-2 text-white/60">
            Export detection reports and view platform statistics.
          </p>

          <div className="mt-10 grid gap-6 md:grid-cols-3">

            <div className="rounded-3xl bg-white/10 border border-white/10 p-8 backdrop-blur-xl">
              <p className="text-white/60">
                Total Scans
              </p>

              <h2 className="mt-3 text-5xl font-bold text-white">
                {stats?.total_scans ?? 0}
              </h2>
            </div>

            <div className="rounded-3xl bg-white/10 border border-white/10 p-8 backdrop-blur-xl">
              <p className="text-white/60">
                URL Scans
              </p>

              <h2 className="mt-3 text-5xl font-bold text-white">
                {stats?.scan_types.url ?? 0}
              </h2>
            </div>

            <div className="rounded-3xl bg-white/10 border border-white/10 p-8 backdrop-blur-xl">
              <p className="text-white/60">
                SMS Scans
              </p>

              <h2 className="mt-3 text-5xl font-bold text-white">
                {stats?.scan_types.sms ?? 0}
              </h2>
            </div>

          </div>

          <div className="mt-10 rounded-3xl border border-white/10 bg-white/10 p-8 backdrop-blur-xl">

            <h2 className="text-2xl font-bold text-white">
              Export Reports
            </h2>

            <p className="mt-2 text-white/60">
              Download the complete phishing detection history.
            </p>

            <button
              onClick={exportCSV}
              className="mt-6 rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-500 px-8 py-4 font-semibold text-white transition hover:scale-105"
            >
              📥 Export CSV
            </button>

          </div>

        </div>

      </div>

    </main>
  );
}