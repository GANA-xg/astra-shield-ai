interface Props {
  signals: string[];
}

export default function SignalList({ signals }: Props) {
  if (!signals.length) {
    return <p className="text-[var(--muted)] text-sm">No signals detected.</p>;
  }

  return (
    <div>
      <h4 className="mb-3 text-base font-semibold text-[var(--ink)]">Detection Signals</h4>
      <ul className="space-y-2">
        {signals.map((signal, index) => (
          <li key={index} className="card-flat p-3 text-sm text-[var(--ink)]">
            ✅ {signal}
          </li>
        ))}
      </ul>
    </div>
  );
}
