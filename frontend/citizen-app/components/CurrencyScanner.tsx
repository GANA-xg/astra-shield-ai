"use client";

import { useState } from "react";
import { detectCurrency } from "@/lib/currencyApi";
import CameraCapture from "@/components/CameraCapture";

export default function CurrencyScanner() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [prediction, setPrediction] = useState("");
  const [confidence, setConfidence] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [showCamera, setShowCamera] = useState(false);

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    if (preview) URL.revokeObjectURL(preview);
    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setPrediction("");
    setConfidence(null);
  }

  async function handleAnalyze() {
    if (!selectedFile) { alert("Please upload an image first."); return; }
    try {
      setLoading(true);
      const result = await detectCurrency(selectedFile);
      setPrediction(result.prediction);
      setConfidence(result.confidence);
    } catch (error) {
      console.error(error);
      alert("Prediction failed.");
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    if (preview) URL.revokeObjectURL(preview);
    setSelectedFile(null);
    setPreview(null);
    setPrediction("");
    setConfidence(null);
    const galleryInput = document.getElementById("currency-file") as HTMLInputElement;
    if (galleryInput) galleryInput.value = "";
  }

  return (
    <div className="text-[var(--ink)]">
      <div className="flex flex-col items-center">
        <div className="flex flex-wrap justify-center gap-4">
          <label htmlFor="currency-file" className="btn-primary cursor-pointer">
            🖼️ Choose from Gallery
          </label>
          <button onClick={() => setShowCamera(true)} className="btn-secondary">
            📷 Open Camera
          </button>
        </div>
        <input id="currency-file" type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
        {showCamera && (
          <CameraCapture
            onCapture={(file, imagePreview) => {
              setSelectedFile(file);
              setPreview(imagePreview);
              setPrediction("");
              setConfidence(null);
              setShowCamera(false);
            }}
            onClose={() => setShowCamera(false)}
          />
        )}
        {selectedFile && <p className="mt-4 text-sm text-[var(--muted)]">📄 {selectedFile.name}</p>}
        {preview && (
          <img src={preview} alt="Currency Preview" className="mt-6 h-64 w-full max-w-md rounded-[var(--radius-sm)] object-contain" />
        )}
        <button onClick={handleAnalyze} disabled={loading || !selectedFile} className="btn-primary mt-6">
          {loading ? "🔍 Analyzing..." : "🔍 Analyze Currency"}
        </button>
        {prediction && (
          <div className={`mt-8 w-full card-flat p-6 ${
            prediction.toLowerCase() === "genuine" ? "border-[var(--success)]" : "border-[var(--error)]"
          }`}>
            <h3 className="text-center text-xl font-semibold text-[var(--ink)]">Detection Result</h3>
            <p className={`mt-6 text-center text-3xl font-bold ${
              prediction.toLowerCase() === "genuine" ? "text-[var(--success)]" : "text-[var(--error)]"
            }`}>{prediction.toUpperCase()}</p>
            <p className="mt-4 text-center text-base text-[var(--body)]">
              Confidence: <span className="font-semibold text-[var(--ink)]">{confidence}%</span>
            </p>
            <div className="mt-8 flex justify-center">
              <button onClick={handleReset} className="btn-secondary">
                🔄 Scan Another Note
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
