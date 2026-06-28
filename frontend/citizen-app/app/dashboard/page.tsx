"use client";

import { useEffect, useState } from "react";

import Navbar from "@/components/Navbar";
import StatsCard from "@/components/StatsCard";

import { getStats } from "@/lib/api";
import { DetectionStats } from "@/types/phishing";

export default function DashboardPage() {
  const [stats, setStats] =
    useState<DetectionStats | null>(null);

  useEffect(() => {
    async function load() {
      const data = await getStats();
      setStats(data);
    }

    load();
  }, []);

  if (!stats) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-8">
        <div className="mx-auto max-w-7xl">

          <Navbar />

          <div className="rounded-3xl border border-white/20 bg-white/10 p-10 text-center text-white backdrop-blur-xl shadow-2xl">
            Loading dashboard...
          </div>

        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-8">
      <div className="mx-auto max-w-7xl">

        <Navbar />

        <div className="rounded-3xl border border-white/20 bg-white/10 p-8 shadow-2xl backdrop-blur-2xl">

          <h1 className="mb-8 text-4xl font-extrabold text-white">
            📊 Threat Intelligence Dashboard
          </h1>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">

            <StatsCard
              title="Total Scans"
              value={stats.total_scans}
              color="bg-blue-600"
            />

            <StatsCard
              title="URL Scans"
              value={stats.scan_types.url ?? 0}
              color="bg-purple-600"
            />

            <StatsCard
              title="SMS Scans"
              value={stats.scan_types.sms ?? 0}
              color="bg-green-600"
            />

            <StatsCard
              title="Critical Threats"
              value={stats.risk_levels.CRITICAL ?? 0}
              color="bg-red-600"
            />

          </div>

          <div className="mt-10 rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur-xl">

            <h2 className="mb-6 text-2xl font-bold text-white">Risk Distribution</h2>

            <div className="space-y-4">

              {Object.entries(stats.risk_levels).map(
                ([level, count]) => (
                  <div key={level} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-800/40 px-5 py-4 backdrop-blur">
                    <span className="font-semibold text-white">{level}</span>
                    <span className="rounded-full bg-white/20 px-4 py-2 font-bold text-white">{count}</span>
                  </div>
                )
              )}

            </div>

          </div>

        </div>

      </div>
    </main>
  );
}