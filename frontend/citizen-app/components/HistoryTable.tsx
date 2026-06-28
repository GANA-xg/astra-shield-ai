import { DetectionHistory } from "@/types/phishing";

interface Props {
  history: DetectionHistory[];
}

export default function HistoryTable({ history }: Props) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-lg">
      <table className="min-w-full bg-white text-slate-900">
        <thead className="bg-slate-900 text-white">
          <tr>
            <th className="px-4 py-3 text-left">Type</th>
            <th className="px-4 py-3 text-left">Input</th>
            <th className="px-4 py-3 text-center">Risk</th>
            <th className="px-4 py-3 text-center">Score</th>
            <th className="px-4 py-3 text-center">Time</th>
          </tr>
        </thead>

        <tbody className="bg-white text-slate-900">
          {history.map((item) => (
            <tr
              key={item.id}
              className="border-b border-gray-200 bg-white text-slate-900 hover:bg-slate-100"
            >
              <td className="px-4 py-4 font-bold uppercase text-slate-900">
                {item.scan_type}
              </td>

              <td className="max-w-sm truncate px-4 py-4 font-medium text-slate-900">
                {item.input_text}
              </td>

              <td
                className={`px-4 py-4 text-center font-bold ${
                  item.risk_level === "CRITICAL"
                    ? "text-red-700"
                    : item.risk_level === "HIGH"
                    ? "text-orange-700"
                    : item.risk_level === "MEDIUM"
                    ? "text-yellow-700"
                    : "text-green-700"
                }`}
              >
                {item.risk_level}
              </td>

              <td className="px-4 py-4 text-center font-bold text-slate-900">
                {item.risk_score}
              </td>

              <td className="px-4 py-4 text-center text-slate-900">
                {new Date(item.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}