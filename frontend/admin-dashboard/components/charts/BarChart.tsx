"use client";

import {
  BarChart,
  Bar,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts";

export default function ScanBarChart({
  data,
}: {
  data: any[];
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/10 backdrop-blur-xl p-6">
      <h2 className="text-xl font-bold text-white mb-5">
        Scan Types
      </h2>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid stroke="#334155" />
          <XAxis dataKey="name" stroke="#cbd5e1" />
          <YAxis stroke="#cbd5e1" />
          <Tooltip />
          <Bar dataKey="value" fill="#38bdf8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}