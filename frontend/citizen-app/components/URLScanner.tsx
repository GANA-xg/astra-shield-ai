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
    if (!url.trim()) { setError("Please enter a URL."); return; }
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
      <div className="flex flex-col gap-4 md:flex-row">
        <input
          type="text"
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="input-field flex-1"
        />
        <button onClick={handleAnalyze} disabled={loading} className="btn-primary">
          {loading ? "Analyzing..." : "Analyze URL"}
        </button>
      </div>
      {error && (
        <div className="mt-4 p-4 rounded-[var(--radius-sm)] bg-[rgba(255,56,92,0.1)] border border-[rgba(255,56,92,0.2)] text-[var(--error)] text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
