"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";

interface CitizenResponse {
  category: string;
  risk_level: string;
  advice: string[];
  recommended_actions: string[];
}

export default function CitizenSafetyPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<CitizenResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const askAssistant = async () => {
    if (!query.trim()) return;

    setLoading(true);

    try {
      const res = await fetch(
        "http://localhost:8000/citizen/advice",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: query,
          }),
        }
      );

      const data = await res.json();
      console.log("Citizen API Response:", data);
      setResult(data);
    } catch (error) {
      console.error(error);

      setResult({
        category: "Connection Error",
        risk_level: "Unknown",
        advice: ["Unable to connect to backend server."],
        recommended_actions: [
          "Verify the backend server is running.",
          "Check the API endpoint URL."
        ],
      });
    }

    setLoading(false);
  };

  const riskColor =
    result?.risk_level?.toLowerCase() === "high"
      ? "text-red-400"
      : result?.risk_level?.toLowerCase() === "medium"
      ? "text-yellow-400"
      : "text-green-400";

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-8">
      <div className="mx-auto max-w-6xl">
        <Navbar />

        <div className="rounded-3xl border border-white/20 bg-white/10 p-8 shadow-2xl backdrop-blur-2xl">
          <h1 className="mb-4 text-4xl font-extrabold text-white">
            🛡 Citizen Safety Assistant
          </h1>

          <p className="mb-6 text-white/70">
            Ask any safety-related question and receive AI-powered guidance.
          </p>

          <textarea
            rows={6}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Example: Someone called me asking for my OTP and bank details."
            className="w-full rounded-xl border border-white/20 bg-white/10 p-4 text-white outline-none"
          />

          <button
            onClick={askAssistant}
            disabled={loading}
            className="mt-4 rounded-xl bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Analyzing..." : "Ask Assistant"}
          </button>

          {result && (
            <div className="mt-8 rounded-2xl border border-white/20 bg-white/10 p-6 text-white">
              <h2 className="mb-6 text-2xl font-bold">
                Analysis Result
              </h2>

              <div className="mb-4">
                <span className="font-semibold">Category:</span>{" "}
                {result.category}
              </div>

              <div className="mb-6">
                <span className="font-semibold">Risk Level:</span>{" "}
                <span className={`font-bold ${riskColor}`}>
                  {result.risk_level}
                </span>
              </div>

              <div className="mb-6">
                <h3 className="mb-2 text-xl font-semibold">
                  Advice
                </h3>

                <ul className="list-disc space-y-2 pl-6">
                  {result.advice?.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="mb-2 text-xl font-semibold">
                  Recommended Actions
                </h3>

                <ul className="list-disc space-y-2 pl-6">
                  {result.recommended_actions?.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}