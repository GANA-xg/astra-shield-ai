"use client";

import {
  PieChart,
  Pie,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from "recharts";

const COLORS = ["#10b981", "#f59e0b", "#f97316", "#ff385c"];

interface ChartData {
  name: string;
  value: number;
}

export default function RiskPieChart({ data }: { data: ChartData[] }) {
  return (
    <div className="card-flat p-6">
      <h2 className="text-lg font-semibold text-[var(--ink)] mb-4">Risk Distribution</h2>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" outerRadius={110}>
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "#222222",
              border: "1px solid #333333",
              borderRadius: "8px",
              color: "#f5f5f5",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
