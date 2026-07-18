"use client";

import { useState } from "react";
import { URLAnalysisResponse } from "@/types/phishing";
import AgentPage from "@/components/AgentPage";
import URLScanner from "@/components/URLScanner";

export default function PhishingPage() {
  const [result, setResult] = useState<URLAnalysisResponse | null>(null);

  return (
    <AgentPage
      title="Phishing Detection"
      description="Scan websites and links in real time to detect phishing attempts using AI, Google Safe Browsing, and threat intelligence."
    >
      <div className="card-flat p-6">
        <URLScanner onResult={setResult} />

        {result && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className={`text-xl font-semibold ${
                result.risk_level === "LOW" ? "text-[var(--success)]"
                : result.risk_level === "MEDIUM" ? "text-[var(--warning)]"
                : result.risk_level === "HIGH" ? "text-[#f97316]"
                : "text-[var(--error)]"
              }`}>
                {result.risk_level === "LOW" ? "✅ " : "⚠️ "}
                {result.risk_level} Risk
              </h3>
              <span className="text-sm text-[var(--muted)] font-mono">{result.domain}</span>
            </div>

            <p className="text-[var(--body)] mb-4">{result.recommendation}</p>

            {result.signals.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-medium text-[var(--muted)] mb-2">Signals</p>
                <div className="flex flex-wrap gap-2">
                  {result.signals.map((s, i) => (
                    <span key={i} className="badge badge-low">{s}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div className="card-flat p-3">
                <p className="text-[var(--muted)] text-xs">Risk Score</p>
                <p className={`text-lg font-semibold ${
                  result.risk_level === "LOW" ? "text-[var(--success)]"
                  : result.risk_level === "MEDIUM" ? "text-[var(--warning)]"
                  : result.risk_level === "HIGH" ? "text-[#f97316]"
                  : "text-[var(--error)]"
                }`}>{result.risk_score}</p>
              </div>
              <div className="card-flat p-3">
                <p className="text-[var(--muted)] text-xs">ML Probability</p>
                <p className="text-lg font-semibold text-[var(--ink)]">{(result.ml_probability * 100).toFixed(2)}%</p>
              </div>
              <div className="card-flat p-3">
                <p className="text-[var(--muted)] text-xs">Safe Browsing</p>
                <p className={`text-lg font-semibold ${result.safe_browsing?.malicious ? "text-[var(--error)]" : "text-[var(--success)]"}`}>
                  {result.safe_browsing?.malicious ? "Malicious" : "Clean"}
                </p>
              </div>
              <div className="card-flat p-3">
                <p className="text-[var(--muted)] text-xs">Blacklists</p>
                <p className={`text-lg font-semibold ${Object.values(result.blacklists ?? {}).some(Boolean) ? "text-[var(--error)]" : "text-[var(--success)]"}`}>
                  {Object.values(result.blacklists ?? {}).some(Boolean) ? "Flagged" : "None"}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        <div className="card p-5">
          <h4 className="text-base font-semibold text-[var(--ink)] mb-2">Google Safe Browsing</h4>
          <p className="text-sm text-[var(--body)] leading-relaxed">Live reputation checks against Google&apos;s threat intelligence database.</p>
        </div>
        <div className="card p-5">
          <h4 className="text-base font-semibold text-[var(--ink)] mb-2">Machine Learning</h4>
          <p className="text-sm text-[var(--body)] leading-relaxed">XGBoost phishing classifier trained on real-world phishing URL datasets.</p>
        </div>
        <div className="card p-5">
          <h4 className="text-base font-semibold text-[var(--ink)] mb-2">Threat Intelligence</h4>
          <p className="text-sm text-[var(--body)] leading-relaxed">OpenPhish feed integration with automatic refresh for latest threats.</p>
        </div>
      </div>
    </AgentPage>
  );
}
