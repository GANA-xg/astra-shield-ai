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

  function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];

    if (!file) return;

    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));

    // Clear previous prediction
    setPrediction("");
    setConfidence(null);
  }

  async function handleAnalyze() {
    if (!selectedFile) {
      alert("Please upload an image first.");
      return;
    }

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
    setSelectedFile(null);
    setPreview(null);
    setPrediction("");
    setConfidence(null);

    const galleryInput = document.getElementById(
      "currency-file"
    ) as HTMLInputElement;


    if (galleryInput) {
      galleryInput.value = "";
    }
  }

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900 p-6 text-white shadow-lg">

      <h2 className="mb-6 text-center text-2xl font-semibold">
        Currency Scanner
      </h2>

      <div className="flex flex-col items-center">

        {/* Gallery + Camera Buttons */}
        <div className="flex flex-wrap justify-center gap-4">

          <label
            htmlFor="currency-file"
            className="cursor-pointer rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
          >
            🖼 Choose from Gallery
          </label>

          <button
            onClick={() => setShowCamera(true)}
              className="rounded-lg bg-emerald-600 px-6 py-3 font-semibold text-white transition hover:bg-emerald-700"

          >
            📷 Open Camera
          </button>

        </div>

        {/* Gallery Upload */}
        <input
          id="currency-file"
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />

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

        {selectedFile && (
          <p className="mt-4 text-sm text-slate-300">
            📄 {selectedFile.name}
          </p>
        )}

        {preview && (
          <img
            src={preview}
            alt="Currency Preview"
            className="mt-6 h-64 w-full max-w-md rounded-xl border border-slate-600 object-contain"
          />
        )}

        <button
          onClick={handleAnalyze}
          disabled={loading || !selectedFile}
          className="mt-6 rounded-lg bg-indigo-600 px-6 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-600"
        >
          {loading ? "🔍 Analyzing..." : "🔍 Analyze Currency"}
        </button>

        {prediction && (
          <div
            className={`mt-8 w-full rounded-xl border p-6 ${
              prediction.toLowerCase() === "genuine"
                ? "border-green-600 bg-green-950/40"
                : "border-red-600 bg-red-950/40"
            }`}
          >
            <h3 className="text-center text-2xl font-bold">
              Detection Result
            </h3>

            <p
              className={`mt-6 text-center text-4xl font-bold ${
                prediction.toLowerCase() === "genuine"
                  ? "text-green-400"
                  : "text-red-400"
              }`}
            >
              {prediction.toUpperCase()}
            </p>

            <p className="mt-4 text-center text-lg">
              Confidence:{" "}
              <span className="font-bold">
                {confidence}%
              </span>
            </p>

            <div className="mt-8 flex justify-center">
              <button
                onClick={handleReset}
                className="rounded-lg bg-slate-700 px-6 py-3 font-semibold text-white transition hover:bg-slate-600"
              >
                🔄 Scan Another Note
              </button>
            </div>
          </div>
        )}

      </div>

    </div>
  );
}