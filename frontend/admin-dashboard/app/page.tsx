"use client";

import { useEffect, useState } from "react";

import Sidebar from "@/components/Sidebar";
import Topbar from "@/components/Topbar";
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
        console.log("Loading dashboard...");

        const statsData = await getStats();
        console.log("Stats:", statsData);

        const historyData = await getHistory();
        console.log("History:", historyData);

        setStats(statsData);
        setHistory(historyData);
      } catch (err) {
        console.error("Dashboard Error:", err);
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        console.log("Finished loading");
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
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950">

      <div className="flex">

        <Sidebar />

        <div className="flex-1 p-8">

          <Topbar />

          {loading ? (
            <div className="mt-8 rounded-3xl border border-white/20 bg-white/10 p-10 text-center text-white backdrop-blur-xl">
              Loading Dashboard...
            </div>
          ) : error ? (
            <div className="mt-8 rounded-3xl border border-red-500/30 bg-red-500/10 p-8 text-red-200 backdrop-blur-xl">
              <h2 className="text-xl font-bold">Failed to load dashboard</h2>
              <p className="mt-2">{error}</p>
            </div>
          ) : (
            <>
              <div className="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-4">

                <MetricCard
                  title="Total Scans"
                  value={stats?.total_scans ?? 0}
                  icon="📊"
                  color="bg-blue-500/20"
                />

                <MetricCard
                  title="URL Scans"
                  value={stats?.scan_types.url ?? 0}
                  icon="🌐"
                  color="bg-cyan-500/20"
                />

                <MetricCard
                  title="SMS Scans"
                  value={stats?.scan_types.sms ?? 0}
                  icon="📱"
                  color="bg-emerald-500/20"
                />

                <MetricCard
                  title="Critical Alerts"
                  value={stats?.risk_levels.CRITICAL ?? 0}
                  icon="🚨"
                  color="bg-red-500/20"
                />

              </div>

              <div className="mt-10 rounded-3xl border border-white/20 bg-white/10 p-8 backdrop-blur-xl">

                <h2 className="mb-6 text-3xl font-bold text-white">
                  Live Threat Feed
                </h2>

                <div className="space-y-4">

                  {history.slice(0, 10).map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between rounded-2xl border border-white/10 bg-slate-900/30 p-5"
                    >
                      <div>

                        <p className="font-semibold text-white">
                          {item.scan_type.toUpperCase()}
                        </p>

                        <p className="text-sm text-white/60 truncate max-w-lg">
                          {item.input_text}
                        </p>

                      </div>

                      <div className="text-right">

                        <p className="font-bold text-red-300">
                          {item.risk_level}
                        </p>

                        <p className="text-white/60">
                          {item.risk_score}/100
                        </p>

                      </div>
                    </div>
                  ))}

                </div>

              </div>
            </>
          )}

        </div>

      </div>

    </main>
  );
}