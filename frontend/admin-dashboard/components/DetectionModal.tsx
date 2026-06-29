"use client";

import { useEffect } from "react";
import { Detection } from "@/types/dashboard";

interface Props {
  detection: Detection | null;
  open: boolean;
  onClose: () => void;
}

export default function DetectionModal({
  detection,
  open,
  onClose,
}: Props) {
  useEffect(() => {
    function handleEsc(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }

    window.addEventListener("keydown", handleEsc);

    return () =>
      window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  if (!open || !detection) return null;

  const badge =
    detection.risk_level === "CRITICAL"
      ? "bg-red-500/25 text-red-200"
      : detection.risk_level === "HIGH"
      ? "bg-orange-500/25 text-orange-200"
      : detection.risk_level === "MEDIUM"
      ? "bg-yellow-500/25 text-yellow-100"
      : "bg-emerald-500/25 text-emerald-100";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-6"
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-3xl rounded-3xl border border-white/10 bg-slate-900/90 shadow-2xl backdrop-blur-xl"
      >
        {/* Header */}

        <div className="flex items-center justify-between border-b border-white/10 px-8 py-6">
          <div>
            <h2 className="text-3xl font-bold text-white">
              Detection Details
            </h2>

            <p className="mt-1 text-white/50">
              Investigation Report
            </p>
          </div>

          <button
            onClick={onClose}
            className="rounded-xl bg-white/10 px-4 py-2 text-xl text-white transition hover:bg-red-500"
          >
            ✕
          </button>
        </div>

        {/* Body */}

        <div className="space-y-8 p-8">

          <div className="grid gap-6 md:grid-cols-2">

            <InfoCard
              label="Scan Type"
              value={detection.scan_type.toUpperCase()}
            />

            <div>
              <p className="mb-2 text-sm text-white/50">
                Risk Level
              </p>

              <span
                className={`rounded-full px-4 py-2 font-semibold ${badge}`}
              >
                {detection.risk_level}
              </span>
            </div>

            <InfoCard
              label="Risk Score"
              value={`${detection.risk_score}/100`}
            />

            <InfoCard
              label="ML Probability"
              value={
                detection.ml_probability != null
                  ? `${(detection.ml_probability * 100).toFixed(2)}%`
                  : "N/A"
              }
            />

          </div>

          <div>
            <p className="mb-2 text-sm text-white/50">
              Input
            </p>

            <div className="rounded-2xl bg-slate-800/70 p-5 break-all text-white">
              {detection.input_text}
            </div>
          </div>

          <div>
            <p className="mb-2 text-sm text-white/50">
              Recommendation
            </p>

            <div className="rounded-2xl bg-blue-500/10 border border-blue-500/20 p-5 text-blue-100">
              {detection.recommendation}
            </div>
          </div>

          <div>
            <p className="mb-4 text-sm text-white/50">
              Detection Signals
            </p>

            <div className="flex flex-wrap gap-3">
              {detection.signals?.length ? (
                detection.signals.map((signal, index) => (
                  <span
                    key={index}
                    className="rounded-full bg-cyan-500/20 px-4 py-2 text-sm text-cyan-100"
                  >
                    ✓ {signal}
                  </span>
                ))
              ) : (
                <span className="text-white/50">
                  No signals recorded
                </span>
              )}
            </div>
          </div>

          <div className="border-t border-white/10 pt-6 text-right text-sm text-white/50">
            {new Date(
              detection.created_at
            ).toLocaleString()}
          </div>

        </div>
      </div>
    </div>
  );
}

function InfoCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl bg-white/5 p-5">
      <p className="text-sm text-white/50">
        {label}
      </p>

      <h3 className="mt-2 text-xl font-semibold text-white break-all">
        {value}
      </h3>
    </div>
  );
}