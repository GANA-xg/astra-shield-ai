"use client";

import { useState } from "react";

type Props = {
  onTranscript: (text: string) => void;
};

export default function VoiceRecorder({ onTranscript }: Props) {
  const [listening, setListening] = useState(false);

  const startRecording = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech Recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      console.log("🎤 Started Listening");
      setListening(true);
    };

    recognition.onend = () => {
      console.log("🛑 Stopped Listening");
      setListening(false);
    };

    recognition.onerror = (event: any) => {
      console.error("❌ Speech Error:", event.error);
    };

    recognition.onresult = (event: any) => {
      console.log("✅ Speech Result:", event);

      const text = event.results[0][0].transcript;

      console.log("📝 Transcript:", text);

      onTranscript(text);
    };

    recognition.start();
  };

  return (
    <button
      onClick={startRecording}
      className="bg-blue-600 text-white px-5 py-3 rounded-xl"
    >
      {listening ? "🎤 Listening..." : "🎤 Start Speaking"}
    </button>
  );
}