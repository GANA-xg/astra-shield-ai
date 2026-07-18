interface Props {
  score: number;
}

export default function RiskMeter({ score }: Props) {
  const level = score >= 80 ? "critical" : score >= 50 ? "medium" : "low";
  return (
    <div className="card-flat p-6">
      <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Risk Score</h3>
      <div className="risk-meter">
        <div className={`risk-meter-fill ${level}`} style={{ width: `${score}%` }} />
      </div>
      <div className="mt-2 flex justify-between text-sm text-[var(--muted)]">
        <span>0</span>
        <span>{score}/100</span>
        <span>100</span>
      </div>
    </div>
  );
}
