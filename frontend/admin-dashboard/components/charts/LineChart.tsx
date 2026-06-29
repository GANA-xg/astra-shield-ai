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

export default function ThreatLineChart({
  data,
}: {
  data: any[];
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/10 backdrop-blur-xl p-6">
      <h2 className="text-xl font-bold text-white mb-5">
        Threat Trend
      </h2>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid stroke="#334155" />
          <XAxis dataKey="day" stroke="#cbd5e1" />
          <YAxis stroke="#cbd5e1" />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="count"
            stroke="#38bdf8"
            strokeWidth={3}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}