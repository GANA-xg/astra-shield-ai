"use client";

import {
  PieChart,
  Pie,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from "recharts";

const COLORS = [
  "#22c55e",
  "#facc15",
  "#fb923c",
  "#ef4444",
];

export default function RiskPieChart({
  data,
}: {
  data: any[];
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/10 backdrop-blur-xl p-6">
      <h2 className="text-xl font-bold text-white mb-5">
        Risk Distribution
      </h2>

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            outerRadius={110}
          >
            {data.map((_, index) => (
              <Cell
                key={index}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>

          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}