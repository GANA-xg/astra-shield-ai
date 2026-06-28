interface SignalListProps {
  signals: string[];
}

export default function SignalList({
  signals,
}: SignalListProps) {
  return (
    <div className="mt-6 rounded-lg bg-gray-50 p-4">
      <h3 className="mb-3 text-lg font-semibold text-gray-900">
        Detection Signals
      </h3>

      <ul className="space-y-2">
        {signals.map((signal, index) => (
          <li
            key={index}
            className="rounded bg-white p-2 text-gray-700 shadow-sm"
          >
            ✅ {signal}
          </li>
        ))}
      </ul>
    </div>
  );
}