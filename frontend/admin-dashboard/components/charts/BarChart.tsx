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

interface ChartData {
  name: string;
  value: number;
}

export default function ScanBarChart({ data }: { data: ChartData[] }) {
  return (
    <div className="card-flat p-6">
      <h2 className="text-lg font-semibold text-[var(--ink)] mb-4">Scan Types</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid stroke="#333333" />
          <XAxis dataKey="name" stroke="#888888" />
          <YAxis stroke="#888888" />
          <Tooltip
            contentStyle={{
              background: "#222222",
              border: "1px solid #333333",
              borderRadius: "8px",
              color: "#f5f5f5",
            }}
          />
          <Bar dataKey="value" fill="#ff385c" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
