import { URLAnalysisResponse } from "@/types/phishing";
import RiskBadge from "./RiskBadge";
import ProgressBar from "./ProgressBar";
import SignalList from "./SignalList";

interface ResultCardProps {
  result: URLAnalysisResponse;
}

export default function ResultCard({ result }: ResultCardProps) {
  return (
    <div className="mt-8 rounded-3xl border border-white/20 bg-white/10 p-8 shadow-2xl backdrop-blur-2xl">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-extrabold text-white">
          Threat Analysis Report
        </h2>

        <RiskBadge level={result.risk_level} />
      </div>

      <div className="mt-6 rounded-2xl border border-white/20 bg-white/10 p-5 backdrop-blur-xl">
        <ProgressBar score={result.risk_score} />
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-cyan-400/20 bg-cyan-500/20 p-6 backdrop-blur-xl">
          <p className="text-sm font-semibold text-white/80">
            ML Confidence
          </p>

          <p className="mt-2 text-4xl font-extrabold text-white">
            {(result.ml_probability * 100).toFixed(2)}%
          </p>
        </div>

        <div className="rounded-2xl border border-emerald-400/20 bg-emerald-500/20 p-6 backdrop-blur-xl">
          <p className="text-sm font-semibold text-white">
            Recommendation
          </p>

          <p className="mt-2 text-xl font-bold text-white">
            {result.recommendation}
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-violet-400/20 bg-violet-500/20 p-6 backdrop-blur-xl">
          <p className="text-sm font-semibold text-white">
            Google Safe Browsing
          </p>

          <p className="mt-3 text-lg font-bold text-white">
            {result.safe_browsing?.malicious
              ? "🔴 Threat Detected"
              : "🟢 Safe"}
          </p>
        </div>

        <div className="rounded-2xl border border-orange-400/20 bg-orange-500/20 p-6 backdrop-blur-xl">
          <p className="text-sm font-semibold text-white">
            Blacklist Matches
          </p>

          <div className="mt-3 space-y-2">
            {Object.entries(result.blacklists).map(
              ([name, value]) => (
                <div
                  key={name}
                  className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-900/30 px-3 py-3"
                >
                  <span className="font-medium text-white capitalize">
                    {name.replaceAll("_", " ")}
                  </span>

                  <span
                    className={
                      value
                        ? "font-bold text-red-300"
                        : "font-bold text-emerald-300"
                    }
                  >
                    {value ? "Matched" : "Clear"}
                  </span>
                </div>
              )
            )}
          </div>
        </div>
      </div>

      <div className="mt-6 rounded-2xl border border-white/20 bg-white/10 p-5 backdrop-blur-xl">
        <SignalList signals={result.signals} />
      </div>
    </div>
  );
}