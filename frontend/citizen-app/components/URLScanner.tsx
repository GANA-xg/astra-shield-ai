"use client";

import { useState } from "react";
import { analyzeURL } from "@/lib/api";
import { URLAnalysisResponse } from "@/types/phishing";

interface URLScannerProps {
  onResult: (result: URLAnalysisResponse) => void;
}

export default function URLScanner({ onResult }: URLScannerProps) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    if (!url.trim()) {
      setError("Please enter a URL.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await analyzeURL(url);
      onResult(result);
    } catch (err) {
      console.error(err);
      setError("Failed to analyze URL.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="mb-8 flex flex-col gap-4 md:flex-row">
        <input
          type="text"
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="flex-1 rounded-2xl border border-white/20 bg-white/10 p-4 text-white placeholder:text-white/50 backdrop-blur-xl focus:border-cyan-400 focus:outline-none"
        />

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-500 px-8 py-4 font-semibold text-white shadow-lg transition hover:scale-[1.02] hover:shadow-cyan-500/40 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Analyzing..." : "Analyze URL"}
        </button>
      </div>

      {error && (
        <p className="rounded-2xl border border-red-400/30 bg-red-500/20 p-4 text-red-100 backdrop-blur-xl">
          {error}
        </p>
      )}
    </div>
  );
}
