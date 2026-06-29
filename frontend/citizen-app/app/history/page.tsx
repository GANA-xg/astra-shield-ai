"use client";

import { useEffect, useState } from "react";

import Navbar from "@/components/Navbar";
import HistoryTable from "@/components/HistoryTable";

import { getHistory } from "@/lib/api";
import { DetectionHistory } from "@/types/phishing";

export default function HistoryPage() {
  const [history, setHistory] = useState<DetectionHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await getHistory();
        setHistory(data);
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-8">
      <div className="mx-auto max-w-7xl">

        <Navbar />

        <div className="rounded-3xl border border-white/20 bg-white/10 p-8 shadow-2xl backdrop-blur-2xl">

          <h2 className="mb-2 text-4xl font-extrabold text-white">
            📜 Detection History
          </h2>
          <p className="mb-8 text-white/70">
            Review all URL and SMS phishing scans stored in the platform.
          </p>

          <div className="mb-8 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-blue-400/20 bg-blue-500/20 p-5 backdrop-blur-xl">
              <p className="text-sm text-white/70">Total Records</p>
              <h3 className="mt-2 text-4xl font-bold text-white">{history.length}</h3>
            </div>

            <div className="rounded-2xl border border-emerald-400/20 bg-emerald-500/20 p-5 backdrop-blur-xl">
              <p className="text-sm text-white/70">URL + SMS Logs</p>
              <h3 className="mt-2 text-4xl font-bold text-white">Live</h3>
            </div>

            <div className="rounded-2xl border border-violet-400/20 bg-violet-500/20 p-5 backdrop-blur-xl">
              <p className="text-sm text-white/70">Database</p>
              <h3 className="mt-2 text-4xl font-bold text-white">Supabase</h3>
            </div>
          </div>

          {loading ? (
            <div className="rounded-2xl border border-white/20 bg-white/10 p-6 text-center text-white backdrop-blur-xl">
              Loading history...
            </div>
          ) : (
            <HistoryTable history={history} />
          )}

        </div>

      </div>
    </main>
  );
}