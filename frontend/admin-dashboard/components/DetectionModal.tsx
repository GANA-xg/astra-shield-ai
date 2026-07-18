"use client";

import { useEffect } from "react";
import { Detection } from "@/types/dashboard";

interface Props {
  detection: Detection | null;
  open: boolean;
  onClose: () => void;
}

export default function DetectionModal({ detection, open, onClose }: Props) {
  useEffect(() => {
    function handleEsc(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  if (!open || !detection) return null;

  const badge = `badge-${detection.risk_level.toLowerCase()}`;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} className="modal-content">
        <div className="flex items-center justify-between p-6 border-b border-[var(--hairline)]">
          <div>
            <h2 className="text-xl font-semibold text-[var(--ink)]">Detection Details</h2>
            <p className="mt-1 text-sm text-[var(--muted)]">Investigation Report</p>
          </div>
          <button onClick={onClose} className="btn-secondary px-3 py-2 h-auto">
            ✕
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="card-flat p-4">
              <p className="text-sm text-[var(--muted)]">Scan Type</p>
              <h3 className="mt-1 text-base font-semibold text-[var(--ink)]">{detection.scan_type.toUpperCase()}</h3>
            </div>
            <div>
              <p className="mb-2 text-sm text-[var(--muted)]">Risk Level</p>
              <span className={badge}>{detection.risk_level}</span>
            </div>
            <div className="card-flat p-4">
              <p className="text-sm text-[var(--muted)]">Risk Score</p>
              <h3 className="mt-1 text-base font-semibold text-[var(--ink)]">{detection.risk_score}/100</h3>
            </div>
            <div className="card-flat p-4">
              <p className="text-sm text-[var(--muted)]">ML Probability</p>
              <h3 className="mt-1 text-base font-semibold text-[var(--ink)]">
                {detection.ml_probability != null
                  ? `${(detection.ml_probability * 100).toFixed(2)}%`
                  : "N/A"}
              </h3>
            </div>
          </div>

          <div>
            <p className="mb-2 text-sm text-[var(--muted)]">Input</p>
            <div className="card-flat p-4 break-all text-[var(--ink)]">{detection.input_text}</div>
          </div>

          <div>
            <p className="mb-2 text-sm text-[var(--muted)]">Recommendation</p>
            <div className="card-flat p-4 text-[var(--body)]">{detection.recommendation}</div>
          </div>

          <div>
            <p className="mb-3 text-sm text-[var(--muted)]">Detection Signals</p>
            <div className="flex flex-wrap gap-2">
              {detection.signals?.length ? (
                detection.signals.map((signal, index) => (
                  <span key={index} className="badge-low">✓ {signal}</span>
                ))
              ) : (
                <span className="text-[var(--muted-soft)]">No signals recorded</span>
              )}
            </div>
          </div>

          <div className="border-t border-[var(--hairline)] pt-4 text-right text-sm text-[var(--muted)]">
            {new Date(detection.created_at).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
}
