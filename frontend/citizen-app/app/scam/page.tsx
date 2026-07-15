"use client";

import { useState } from "react";

import VoiceRecorder from "@/components/VoiceRecorder";
import TranscriptBox from "@/components/TranscriptBox";
import ScamResultCard from "@/components/ScamResultCard";

import { detectScam } from "@/lib/scamApi";

export default function ScamPage() {
  const [transcript, setTranscript] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleTranscript(text: string) {
    setTranscript(text);
    setLoading(true);

    try {
      const response = await detectScam(text);

      setResult(response);

      speakResult(response);
    } catch (err) {
      console.error(err);
      alert("Backend Error");
    }

    setLoading(false);
  }

  function speakResult(result: any) {
    if (!window.speechSynthesis) return;

    const message = result.is_scam
      ? `Warning. This appears to be a ${result.scam_type}. Risk score is ${result.risk_score} percent. ${result.reason}`
      : "No scam indicators were detected.";

    const speech = new SpeechSynthesisUtterance(message);

    speech.lang = "en-US";
    speech.rate = 1;
    speech.pitch = 1;

    window.speechSynthesis.speak(speech);
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 to-black text-white">

      <div className="max-w-4xl mx-auto p-10">

        <h1 className="text-4xl font-bold mb-8">
          🎙 AI Scam Call Detector
        </h1>

        <VoiceRecorder
          onTranscript={handleTranscript}
        />

        <div className="mt-6">
          <TranscriptBox transcript={transcript} />
        </div>

        {loading && (
          <div className="mt-6 text-lg">
            🔍 Analyzing Call...
          </div>
        )}

        {result && (
          <ScamResultCard result={result} />
        )}

      </div>

    </main>
  );
}