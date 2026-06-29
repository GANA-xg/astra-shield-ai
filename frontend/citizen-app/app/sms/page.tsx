"use client";

import { useState } from "react";

import Navbar from "@/components/Navbar";
import { analyzeSMS } from "@/lib/api";
import { SMSResponse } from "@/types/phishing";

export default function SMSPage() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SMSResponse | null>(null);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    if (!message.trim()) {
      setError("Please enter an SMS message.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await analyzeSMS(message);
      setResult(response);
    } catch (err) {
      console.error(err);
      setError("Failed to analyze SMS.");
    } finally {
      setLoading(false);
    }
  }

  const badgeColor =
    result?.risk_level === "CRITICAL"
      ? "bg-red-100 text-red-700"
      : result?.risk_level === "HIGH"
      ? "bg-orange-100 text-orange-700"
      : result?.risk_level === "MEDIUM"
      ? "bg-yellow-100 text-yellow-700"
      : "bg-green-100 text-green-700";

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-8">
      <div className="mx-auto max-w-6xl">

        <Navbar />

        <div className="rounded-3xl border border-white/20 bg-white/10 p-8 shadow-2xl backdrop-blur-2xl">

          <h2 className="mb-2 text-4xl font-extrabold text-white">
            📱 SMS Phishing Scanner
          </h2>
          <p className="mb-8 text-white/70">
            Detect phishing, scam and malicious SMS messages using AI and threat intelligence.
          </p>

          <textarea
            rows={6}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Paste the SMS message here..."
            className="w-full rounded-2xl border border-white/20 bg-white/10 p-5 text-white placeholder:text-white/50 backdrop-blur-xl focus:border-blue-400 focus:outline-none"
          />

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="mt-5 rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-500 px-8 py-4 font-semibold text-white shadow-lg transition hover:scale-[1.02] hover:shadow-blue-500/40 disabled:bg-gray-400"
          >
            {loading ? "Analyzing..." : "Analyze SMS"}
          </button>

          {error && (
            <div className="mt-5 rounded-lg bg-red-100 p-4 text-red-700">
              {error}
            </div>
          )}

          {result && (
            <div className="mt-8 rounded-3xl border border-white/20 bg-white/10 p-6 shadow-2xl backdrop-blur-xl">

              <div className="flex items-center justify-between">

                <h3 className="text-2xl font-bold text-white">
                  SMS Analysis
                </h3>

                <span
                  className={`rounded-full px-4 py-2 font-bold ${badgeColor}`}
                >
                  {result.risk_level}
                </span>

              </div>

              <div className="mt-6">

                <div className="mb-2 flex justify-between text-white">
                  <span>Risk Score</span>
                  <span>{result.risk_score}/100</span>
                </div>

                <div className="h-3 overflow-hidden rounded-full bg-white/20">
                  <div
                    className="h-full bg-red-500"
                    style={{
                      width: `${result.risk_score}%`,
                    }}
                  />
                </div>

              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-2">

                <div className="rounded-2xl border border-emerald-400/20 bg-emerald-500/20 p-5 backdrop-blur-xl">
                  <p className="text-sm text-white">
                    Recommendation
                  </p>

                  <p className="mt-2 text-lg font-semibold text-white">
                    {result.recommendation}
                  </p>
                </div>

                <div className="rounded-2xl border border-blue-400/20 bg-blue-500/20 p-5 backdrop-blur-xl">
                  <p className="text-sm text-white">
                    URLs Found
                  </p>

                  <p className="mt-2 text-lg font-bold text-white">
                    {result.urls.length}
                  </p>
                </div>

              </div>

              <div className="mt-6 rounded-2xl border border-white/20 bg-white/10 p-5 backdrop-blur-xl">

                <h4 className="mb-3 text-lg font-bold text-white">
                  Detection Signals
                </h4>

                <ul className="space-y-2">

                  {result.signals.map((signal, index) => (
                    <li
                      key={index}
                      className="rounded-xl border border-white/10 bg-slate-800/40 p-3 text-white shadow"
                    >
                      ✅ {signal}
                    </li>
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