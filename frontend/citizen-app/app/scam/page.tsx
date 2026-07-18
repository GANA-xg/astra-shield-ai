"use client";

import { useState } from "react";
import AgentPage from "@/components/AgentPage";
import VoiceRecorder from "@/components/VoiceRecorder";
import TranscriptBox from "@/components/TranscriptBox";
import ScamResultCard from "@/components/ScamResultCard";
import { detectScam } from "@/lib/scamApi";

interface ScamResult {
  is_scam: boolean;
  scam_type: string;
  confidence: number;
  reason: string;
  risk_score: number;
  detected_keywords: string[];
  recommendation: string[];
}

export default function ScamPage() {
  const [transcript, setTranscript] = useState("");
  const [result, setResult] = useState<ScamResult | null>(null);
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

  function speakResult(result: ScamResult) {
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
    <AgentPage
      title="Scam Call Detection"
      description="Analyze call recordings and transcripts to identify scam patterns and fraudulent behavior. Record your call or paste a transcript to get started."
    >
      <div className="card-flat p-6">
        <VoiceRecorder onTranscript={handleTranscript} />
        <div className="mt-6">
          <TranscriptBox transcript={transcript} />
        </div>
        {loading && (
          <div className="mt-6 text-[var(--body)] flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
            Analyzing call for scam indicators...
          </div>
        )}
        {result && <ScamResultCard result={result} />}
      </div>
    </AgentPage>
  );
}
