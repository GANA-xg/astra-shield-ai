"use client";

import { useEffect, useState } from "react";
import AdminLayout from "@/components/AdminLayout";
import MetricCard from "@/components/MetricCard";
import { getHistory, getStats } from "@/lib/api";
import { DashboardStats, Detection } from "@/types/dashboard";

export default function DashboardHome() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [history, setHistory] = useState<Detection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      setError(null);
      try {
        const statsData = await getStats();
        const historyData = await getHistory();
        setStats(statsData);
        setHistory(historyData);
      } catch (err) {
        console.error("Dashboard Error:", err);
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();

    const interval = setInterval(() => {
      loadDashboard();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <AdminLayout>
      {loading ? (
        <div className="card-flat p-10 text-center text-[var(--body)]">
          Loading Dashboard...
        </div>
      ) : error ? (
        <div className="card-flat p-8 border-[var(--error)]">
          <h2 className="text-lg font-semibold text-[var(--error)]">Failed to load dashboard</h2>
          <p className="mt-2 text-[var(--body)]">{error}</p>
        </div>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4 mb-8">
            <MetricCard
              title="Total Scans"
              value={stats?.total_scans ?? 0}
              icon="📊"
              color="bg-[var(--info)]"
            />
            <MetricCard
              title="URL Scans"
              value={stats?.scan_types.url ?? 0}
              icon="🌐"
              color="bg-[#8b5cf6]"
            />
            <MetricCard
              title="SMS Scans"
              value={stats?.scan_types.sms ?? 0}
              icon="📱"
              color="bg-[var(--success)]"
            />
            <MetricCard
              title="Critical Alerts"
              value={stats?.risk_levels.CRITICAL ?? 0}
              icon="🚨"
              color="bg-[var(--error)]"
            />
          </div>

          <div className="card-flat p-6">
            <h2 className="mb-4 text-lg font-semibold text-[var(--ink)]">Live Threat Feed</h2>
            <div className="space-y-3">
              {history.slice(0, 10).map((item) => (
                <div key={item.id} className="flex items-center justify-between card-flat p-4">
                  <div>
                    <p className="font-semibold text-[var(--ink)]">{item.scan_type.toUpperCase()}</p>
                    <p className="text-sm text-[var(--muted)] truncate max-w-lg">{item.input_text}</p>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold ${
                      item.risk_level === "CRITICAL" ? "text-[var(--error)]"
                      : item.risk_level === "HIGH" ? "text-[#f97316]"
                      : item.risk_level === "MEDIUM" ? "text-[var(--warning)]"
                      : "text-[var(--success)]"
                    }`}>{item.risk_level}</p>
                    <p className="text-xs text-[var(--muted)]">{item.risk_score}/100</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </AdminLayout>
  );
}
