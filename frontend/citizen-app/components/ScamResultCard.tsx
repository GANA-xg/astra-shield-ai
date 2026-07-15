interface Props {
  result: any;
}

export default function ScamResultCard({ result }: Props) {
  if (!result) return null;

  return (
    <div className="rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur-xl">

      <h2 className="text-3xl font-bold text-white mb-5">

        {result.is_scam ? "🚨 Scam Detected" : "✅ Safe Call"}

      </h2>

      <div className="space-y-3 text-white">

        <p>
          <strong>Scam Type:</strong> {result.scam_type}
        </p>

        <p>
          <strong>Confidence:</strong> {result.confidence}
        </p>

        <p>
          <strong>Reason:</strong>
        </p>

        <p className="text-white/80">
          {result.reason}
        </p>

        <div>

          <h3 className="font-bold mt-5">
            Detected Keywords
          </h3>

          <div className="flex flex-wrap gap-2 mt-2">

            {result.detected_keywords?.map((k: string) => (
              <span
                key={k}
                className="bg-red-600 rounded-full px-3 py-1 text-sm"
              >
                {k}
              </span>
            ))}

          </div>

        </div>

        <div>

          <h3 className="font-bold mt-5">
            Recommendations
          </h3>

          <ul className="list-disc ml-6 mt-2">

            {result.recommendation?.map((r: string) => (
              <li key={r}>{r}</li>
            ))}

          </ul>

        </div>

      </div>

    </div>
  );
}