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
    if (!message.trim()) {
      setError("Please enter an SMS message.");
      return;
    }

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
        className="w-full rounded-2xl border border-white/20 bg-white/10 p-5 text-white placeholder:text-white/50 backdrop-blur-xl focus:border-cyan-400 focus:outline-none"
      />

      <div className="mt-5 flex justify-end">
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-500 px-8 py-4 font-semibold text-white shadow-lg transition hover:scale-[1.02] hover:shadow-cyan-500/40 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Analyzing..." : "Analyze SMS"}
        </button>
      </div>

      {error && (
        <div className="mt-5 rounded-2xl border border-red-400/30 bg-red-500/20 p-4 text-red-100 backdrop-blur-xl">
          {error}
        </div>
      )}
    </div>
  );
}
