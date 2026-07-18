"use client";

import { useState } from "react";
import AgentPage from "@/components/AgentPage";

interface CitizenResponse {
  category: string;
  risk_level: string;
  advice: string[];
  recommended_actions: string[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export default function CitizenSafetyPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<CitizenResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const askAssistant = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/citizen/advice`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error(error);
      setResult({
        category: "Connection Error",
        risk_level: "Unknown",
        advice: ["Unable to connect to backend server."],
        recommended_actions: ["Verify the backend server is running.", "Check the API endpoint URL."],
      });
    }
    setLoading(false);
  };

  const riskColor =
    result?.risk_level?.toLowerCase() === "high" ? "text-[var(--error)]"
    : result?.risk_level?.toLowerCase() === "medium" ? "text-[var(--warning)]"
    : "text-[var(--success)]";

  return (
    <AgentPage
      title="Citizen Bot"
      description="Ask any safety-related question and receive personalized AI-powered guidance and recommendations."
    >
      <div className="card-flat p-6">
        <textarea
          rows={5}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Example: Someone called me asking for my OTP and bank details..."
          className="input-field h-auto min-h-[120px] resize-none"
        />
        <button onClick={askAssistant} disabled={loading || !query.trim()} className="btn-primary mt-4">
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              Ask Assistant
            </>
          )}
        </button>

        {result && (
          <div className="mt-8">
            <h3 className="mb-5 text-lg font-semibold text-[var(--ink)]">Analysis Result</h3>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="card-flat p-4">
                <p className="text-xs text-[var(--muted)] mb-1">Category</p>
                <p className="text-base font-medium text-[var(--ink)]">{result.category}</p>
              </div>
              <div className="card-flat p-4">
                <p className="text-xs text-[var(--muted)] mb-1">Risk Level</p>
                <p className={`text-base font-semibold ${riskColor}`}>{result.risk_level}</p>
              </div>
            </div>

            <div className="mb-6">
              <h4 className="mb-3 text-base font-semibold text-[var(--ink)]">Advice</h4>
              <ul className="space-y-2">
                {result.advice?.map((item, index) => (
                  <li key={index} className="flex items-start gap-3 text-[var(--body)]">
                    <svg className="w-5 h-5 text-[var(--primary)] mt-0.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M9 18l6-6-6-6"/>
                    </svg>
                    <span className="text-sm leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="mb-3 text-base font-semibold text-[var(--ink)]">Recommended Actions</h4>
              <ul className="space-y-2">
                {result.recommended_actions?.map((item, index) => (
                  <li key={index} className="flex items-start gap-3 text-[var(--body)]">
                    <svg className="w-5 h-5 text-[var(--success)] mt-0.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                      <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                    <span className="text-sm leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </AgentPage>
  );
}
