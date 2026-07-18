"use client";

import { useEffect, useState } from "react";
import AdminLayout from "@/components/AdminLayout";
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
    const headers = ["ID", "Type", "Risk", "Score", "Input", "Recommendation", "Created At"];
    const rows = history.map((d) => [
      d.id,
      d.scan_type,
      d.risk_level,
      d.risk_score,
      `"${d.input_text.replace(/"/g, '""')}"`,
      `"${d.recommendation.replace(/"/g, '""')}"`,
      d.created_at,
    ]);
    const csv = [headers, ...rows].map((r) => r.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "astra-shield-report.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <AdminLayout>
      <h1 className="mb-2 text-2xl font-semibold text-[var(--ink)]">Reports</h1>
      <p className="mb-8 text-[var(--muted)]">Export detection reports and view platform statistics.</p>

      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <div className="card-flat p-6">
          <p className="text-[var(--muted)]">Total Scans</p>
          <h2 className="mt-3 text-4xl font-bold text-[var(--ink)]">{stats?.total_scans ?? 0}</h2>
        </div>
        <div className="card-flat p-6">
          <p className="text-[var(--muted)]">URL Scans</p>
          <h2 className="mt-3 text-4xl font-bold text-[var(--ink)]">{stats?.scan_types.url ?? 0}</h2>
        </div>
        <div className="card-flat p-6">
          <p className="text-[var(--muted)]">SMS Scans</p>
          <h2 className="mt-3 text-4xl font-bold text-[var(--ink)]">{stats?.scan_types.sms ?? 0}</h2>
        </div>
      </div>

      <div className="card-flat p-6">
        <h2 className="text-lg font-semibold text-[var(--ink)]">Export Reports</h2>
        <p className="mt-2 text-[var(--muted)]">Download the complete phishing detection history.</p>
        <button onClick={exportCSV} className="btn-primary mt-6">
          📥 Export CSV
        </button>
      </div>
    </AdminLayout>
  );
}
