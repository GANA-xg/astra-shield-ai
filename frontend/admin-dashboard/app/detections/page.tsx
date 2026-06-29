"use client";

import { useEffect, useMemo, useState } from "react";

import Sidebar from "@/components/Sidebar";
import Topbar from "@/components/Topbar";
import DetectionModal from "@/components/DetectionModal";

import { getHistory } from "@/lib/api";
import { Detection } from "@/types/dashboard";

export default function DetectionsPage() {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [search, setSearch] = useState("");
  const [risk, setRisk] = useState("ALL");
  const [type, setType] = useState("ALL");
  const [selectedDetection, setSelectedDetection] = useState<Detection | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await getHistory();
        setDetections(data);
      } catch (err) {
        console.error(err);
      }
    }

    load();
  }, []);

  const filtered = useMemo(() => {
    return detections.filter((d) => {
      const matchesSearch = d.input_text
        .toLowerCase()
        .includes(search.toLowerCase());

      const matchesRisk =
        risk === "ALL" || d.risk_level === risk;

      const matchesType =
        type === "ALL" ||
        d.scan_type.toUpperCase() === type;

      return (
        matchesSearch &&
        matchesRisk &&
        matchesType
      );
    });
  }, [detections, search, risk, type]);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950">
      <div className="flex">

        <Sidebar />

        <div className="flex-1 p-8">

          <Topbar />

          <h1 className="mt-8 mb-8 text-4xl font-bold text-white">
            🛡 Detection Management
          </h1>

          <div className="mb-8 grid gap-4 md:grid-cols-3">

            <input
              placeholder="Search URL or SMS..."
              value={search}
              onChange={(e) =>
                setSearch(e.target.value)
              }
              className="rounded-xl border border-white/20 bg-white/10 p-4 text-white placeholder:text-white/50"
            />

            <select
              value={risk}
              onChange={(e) =>
                setRisk(e.target.value)
              }
              className="rounded-xl border border-white/20 bg-slate-900 p-4 text-white"
            >
              <option>ALL</option>
              <option>LOW</option>
              <option>MEDIUM</option>
              <option>HIGH</option>
              <option>CRITICAL</option>
            </select>

            <select
              value={type}
              onChange={(e) =>
                setType(e.target.value)
              }
              className="rounded-xl border border-white/20 bg-slate-900 p-4 text-white"
            >
              <option>ALL</option>
              <option>URL</option>
              <option>SMS</option>
            </select>

          </div>

          <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/10 backdrop-blur-xl">

            <table className="w-full">

              <thead className="bg-white/10">

                <tr className="text-left text-white">

                  <th className="p-5">Type</th>
                  <th className="p-5">Input</th>
                  <th className="p-5">Risk</th>
                  <th className="p-5">Score</th>
                  <th className="p-5">Time</th>

                </tr>

              </thead>

              <tbody>

                {filtered.map((item) => (
                  <tr
                    key={item.id}
                    onClick={() => {
                      setSelectedDetection(item);
                      setModalOpen(true);
                    }}
                    className="cursor-pointer border-t border-white/10 transition hover:bg-cyan-500/10"
                  >
                    <td className="p-5 text-white">
                      {item.scan_type.toUpperCase()}
                    </td>

                    <td className="max-w-md truncate p-5 text-white/70">
                      {item.input_text}
                    </td>

                    <td className="p-5">
                      <span
                        className={`rounded-full px-3 py-1 text-sm font-bold ${
                          item.risk_level === "CRITICAL"
                            ? "bg-red-500/30 text-red-200"
                            : item.risk_level === "HIGH"
                            ? "bg-orange-500/30 text-orange-200"
                            : item.risk_level === "MEDIUM"
                            ? "bg-yellow-500/30 text-yellow-100"
                            : "bg-emerald-500/30 text-emerald-100"
                        }`}
                      >
                        {item.risk_level}
                      </span>
                    </td>

                    <td className="p-5 text-white">
                      {item.risk_score}
                    </td>

                    <td className="p-5 text-white/60">
                      {new Date(
                        item.created_at
                      ).toLocaleString()}
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>

        </div>

      </div>
      <DetectionModal
        detection={selectedDetection}
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedDetection(null);
        }}
      />
    </main>
  );
}