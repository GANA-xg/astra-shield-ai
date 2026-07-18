"use client";

import { useEffect, useRef } from "react";

interface CameraCaptureProps {
  onCapture: (file: File, preview: string) => void;
  onClose: () => void;
}

export default function CameraCapture({ onCapture, onClose }: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    startCamera();
    return () => { stopCamera(); };
  }, []);

  async function startCamera() {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false,
      });
      streamRef.current = mediaStream;
      if (videoRef.current) videoRef.current.srcObject = mediaStream;
    } catch (error) {
      console.error(error);
      alert("Unable to access the camera. Please allow camera permission.");
      onClose();
    }
  }

  function stopCamera() {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  }

  function capturePhoto() {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], "captured-note.jpg", { type: "image/jpeg" });
      const preview = URL.createObjectURL(blob);
      stopCamera();
      onCapture(file, preview);
    }, "image/jpeg", 0.95);
  }

  return (
    <div className="mt-6 card-flat p-6">
      <h3 className="mb-4 text-center text-lg font-semibold text-[var(--ink)]">Live Camera</h3>
      <video ref={videoRef} autoPlay playsInline muted className="w-full rounded-[var(--radius-sm)]" />
      <canvas ref={canvasRef} className="hidden" />
      <div className="mt-6 flex justify-center gap-4">
        <button onClick={capturePhoto} className="btn-primary bg-[var(--success)] hover:bg-[#059669]">
          📸 Capture
        </button>
        <button onClick={() => { stopCamera(); onClose(); }} className="btn-secondary">
          ❌ Cancel
        </button>
      </div>
    </div>
  );
}
