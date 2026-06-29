"use client";

import { useState } from "react";
import { URLAnalysisResponse } from "@/types/phishing";
import ResultCard from "@/components/ResultCard";
import URLScanner from "@/components/URLScanner";
import Navbar from "@/components/Navbar";
export default function Home() {
  const [result, setResult] = useState<URLAnalysisResponse | null>(null);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-8">
      <div className="mx-auto max-w-6xl">
        <Navbar />
        

        <div className="rounded-3xl border border-white/20 bg-white/10 p-8 shadow-2xl backdrop-blur-2xl">

          <div className="mb-8">
            <h2 className="mb-2 text-4xl font-extrabold text-white">
              🌐 URL Phishing Scanner
            </h2>
            <p className="text-white/70">
              Analyze websites in real time using AI, Google Safe Browsing, and multiple threat intelligence sources.
            </p>
          </div>
          <URLScanner onResult={setResult} />

          {result && <ResultCard result={result} />}

          <div className="mt-10 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur-xl transition-all duration-300 hover:-translate-y-1 hover:bg-white/15">
              <h4 className="text-lg font-bold text-white">🛡 Google Safe Browsing</h4>
              <p className="mt-3 text-sm leading-6 text-white/70">Live reputation checks against Google's threat intelligence.</p>
            </div>

            <div className="rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur-xl transition-all duration-300 hover:-translate-y-1 hover:bg-white/15">
              <h4 className="text-lg font-bold text-white">🤖 Machine Learning</h4>
              <p className="mt-3 text-sm leading-6 text-white/70">XGBoost phishing classifier trained on phishing URL datasets.</p>
            </div>

            <div className="rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur-xl transition-all duration-300 hover:-translate-y-1 hover:bg-white/15">
              <h4 className="text-lg font-bold text-white">🌍 Threat Intelligence</h4>
              <p className="mt-3 text-sm leading-6 text-white/70">OpenPhish feed integration with automatic refresh.</p>
            </div>
          </div>

        </div>
      </div>
    </main>
  );
}