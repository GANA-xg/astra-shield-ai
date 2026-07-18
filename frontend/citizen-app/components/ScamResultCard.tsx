interface ScamResult {
  is_scam: boolean;
  scam_type: string;
  confidence: number;
  reason: string;
  risk_score: number;
  detected_keywords: string[];
  recommendation: string[];
}

interface Props {
  result: ScamResult;
}

export default function ScamResultCard({ result }: Props) {
  if (!result) return null;
  return (
    <div className="mt-6 card-flat p-6">
      <h3 className="text-xl font-semibold text-[var(--ink)] mb-5">
        {result.is_scam ? "🚨 Scam Detected" : "✅ Safe Call"}
      </h3>
      <div className="space-y-3 text-[var(--ink)]">
        <p><span className="text-[var(--muted)]">Scam Type:</span> {result.scam_type}</p>
        <p><span className="text-[var(--muted)]">Confidence:</span> {result.confidence}</p>
        <p><span className="text-[var(--muted)]">Reason:</span></p>
        <p className="text-[var(--body)]">{result.reason}</p>
        <div>
          <h4 className="font-semibold mt-5 text-[var(--ink)]">Detected Keywords</h4>
          <div className="flex flex-wrap gap-2 mt-2">
            {result.detected_keywords?.map((k: string) => (
              <span key={k} className="badge-critical">{k}</span>
            ))}
          </div>
        </div>
        <div>
          <h4 className="font-semibold mt-5 text-[var(--ink)]">Recommendations</h4>
          <ul className="list-disc ml-6 mt-2 text-[var(--body)]">
            {result.recommendation?.map((r: string) => <li key={r}>{r}</li>)}
          </ul>
        </div>
      </div>
    </div>
  );
}
