"use client";

import { useEffect, useMemo, useState } from "react";
import AdminLayout from "@/components/AdminLayout";
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
      const matchesSearch = d.input_text.toLowerCase().includes(search.toLowerCase());
      const matchesRisk = risk === "ALL" || d.risk_level === risk;
      const matchesType = type === "ALL" || d.scan_type.toUpperCase() === type;
      return matchesSearch && matchesRisk && matchesType;
    });
  }, [detections, search, risk, type]);

  return (
    <AdminLayout>
      <h1 className="mb-6 text-2xl font-semibold text-[var(--ink)]">Detection Management</h1>

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <input
          placeholder="Search URL or SMS..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-field"
        />
        <select
          value={risk}
          onChange={(e) => setRisk(e.target.value)}
          className="input-field"
        >
          <option>ALL</option>
          <option>LOW</option>
          <option>MEDIUM</option>
          <option>HIGH</option>
          <option>CRITICAL</option>
        </select>
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="input-field"
        >
          <option>ALL</option>
          <option>URL</option>
          <option>SMS</option>
        </select>
      </div>

      <div className="card-flat overflow-hidden">
        <table className="data-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Input</th>
              <th>Risk</th>
              <th>Score</th>
              <th>Time</th>
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
                className="cursor-pointer"
              >
                <td className="font-semibold text-[var(--ink)]">{item.scan_type.toUpperCase()}</td>
                <td className="max-w-md truncate text-[var(--body)]">{item.input_text}</td>
                <td>
                  <span className={`badge-${item.risk_level.toLowerCase()}`}>
                    {item.risk_level}
                  </span>
                </td>
                <td className="text-[var(--ink)]">{item.risk_score}</td>
                <td className="text-[var(--muted)]">{new Date(item.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <DetectionModal
        detection={selectedDetection}
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedDetection(null);
        }}
      />
    </AdminLayout>
  );
}
