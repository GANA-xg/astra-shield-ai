"use client";

import { useState } from "react";

type Props = {
  onTranscript: (text: string) => void;
};

export default function VoiceRecorder({ onTranscript }: Props) {
  const [listening, setListening] = useState(false);

  const startRecording = () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const SpeechRecognitionConstructor = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognitionConstructor) {
      alert("Speech Recognition is not supported in this browser.");
      return;
    }
    const recognition = new SpeechRecognitionConstructor();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);
    recognition.onerror = (event: { error: string }) => console.error("Speech Error:", event.error);
    recognition.onresult = (event: { results: { 0: { 0: { transcript: string } } } }) => {
      const text = event.results[0][0].transcript;
      onTranscript(text);
    };
    recognition.start();
  };

  return (
    <button onClick={startRecording} className="btn-primary">
      {listening ? "🎤 Listening..." : "🎤 Start Speaking"}
    </button>
  );
}
