"use client";

import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ChartData {
  day: string;
  count: number;
}

export default function ThreatLineChart({ data }: { data: ChartData[] }) {
  return (
    <div className="card-flat p-6">
      <h2 className="text-lg font-semibold text-[var(--ink)] mb-4">Threat Trend</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid stroke="#333333" />
          <XAxis dataKey="day" stroke="#888888" />
          <YAxis stroke="#888888" />
          <Tooltip
            contentStyle={{
              background: "#222222",
              border: "1px solid #333333",
              borderRadius: "8px",
              color: "#f5f5f5",
            }}
          />
          <Line
            type="monotone"
            dataKey="count"
            stroke="#ff385c"
            strokeWidth={3}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
