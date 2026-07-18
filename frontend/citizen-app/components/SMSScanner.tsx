"use client";

import { useState } from "react";
import { analyzeSMS } from "@/lib/api";
import { SMSResponse } from "@/types/phishing";

interface SMSScannerProps {
  onResult: (result: SMSResponse) => void;
}

export default function SMSScanner({ onResult }: SMSScannerProps) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    if (!message.trim()) { setError("Please enter an SMS message."); return; }
    setLoading(true);
    setError("");
    try {
      const result = await analyzeSMS(message);
      onResult(result);
    } catch (err) {
      console.error(err);
      setError("Failed to analyze SMS.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <textarea
        rows={6}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Paste the SMS message here..."
        className="input-field h-auto min-h-[120px] resize-none"
      />
      <div className="mt-5 flex justify-end">
        <button onClick={handleAnalyze} disabled={loading} className="btn-primary">
          {loading ? "Analyzing..." : "Analyze SMS"}
        </button>
      </div>
      {error && (
        <div className="mt-5 p-4 rounded-[var(--radius-sm)] bg-[rgba(255,56,92,0.1)] border border-[rgba(255,56,92,0.2)] text-[var(--error)] text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
