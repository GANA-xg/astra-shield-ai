import { useRef, useEffect, useState, useCallback } from "react";

interface FadingVideoProps {
  src: string | string[];
  className?: string;
  style?: React.CSSProperties;
}

export default function FadingVideo({
  src,
  className,
  style,
}: FadingVideoProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [videoSrcs] = useState<string[]>(
    Array.isArray(src) ? src : [src]
  );
  const [currentIndex, setCurrentIndex] = useState(0);
  const fadeStateRef = useRef<"idle" | "fading-in" | "visible" | "fading-out">(
    "idle"
  );
  const rafRef = useRef<number>(0);
  const opacityRef = useRef(0);

  const setOpacity = useCallback((val: number) => {
    opacityRef.current = val;
    if (videoRef.current) {
      videoRef.current.style.opacity = String(val);
    }
  }, []);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let cancelled = false;

    const fadeIn = () => {
      fadeStateRef.current = "fading-in";
      const start = performance.now();
      const duration = 500;

      const tick = (now: number) => {
        if (cancelled) return;
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        setOpacity(progress);
        if (progress < 1) {
          rafRef.current = requestAnimationFrame(tick);
        } else {
          fadeStateRef.current = "visible";
        }
      };
      rafRef.current = requestAnimationFrame(tick);
    };

    const fadeOut = () => {
      fadeStateRef.current = "fading-out";
      const start = performance.now();
      const duration = 550;

      const tick = (now: number) => {
        if (cancelled) return;
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        setOpacity(1 - progress);
        if (progress < 1) {
          rafRef.current = requestAnimationFrame(tick);
        } else {
          fadeStateRef.current = "idle";
          setOpacity(0);
          if (videoSrcs.length === 1) {
            video.currentTime = 0;
            video.play();
            fadeIn();
          } else {
            const nextIndex = (currentIndex + 1) % videoSrcs.length;
            setCurrentIndex(nextIndex);
          }
        }
      };
      rafRef.current = requestAnimationFrame(tick);
    };

    const onLoadedData = () => {
      if (!cancelled) fadeIn();
    };

    const onTimeUpdate = () => {
      if (cancelled) return;
      const remaining = video.duration - video.currentTime;
      if (remaining <= 0.55 && fadeStateRef.current === "visible") {
        fadeOut();
      }
    };

    const onEnded = () => {
      if (videoSrcs.length === 1) {
        video.currentTime = 0;
        video.play();
        fadeIn();
      } else {
        const nextIndex = (currentIndex + 1) % videoSrcs.length;
        setCurrentIndex(nextIndex);
      }
    };

    video.addEventListener("loadeddata", onLoadedData);
    video.addEventListener("timeupdate", onTimeUpdate);
    video.addEventListener("ended", onEnded);

    if (video.readyState >= 2) {
      onLoadedData();
    }

    return () => {
      cancelled = true;
      cancelAnimationFrame(rafRef.current);
      video.removeEventListener("loadeddata", onLoadedData);
      video.removeEventListener("timeupdate", onTimeUpdate);
      video.removeEventListener("ended", onEnded);
    };
  }, [videoSrcs, currentIndex, setOpacity]);

  return (
    <video
      ref={videoRef}
      src={videoSrcs[currentIndex]}
      autoPlay
      muted
      playsInline
      preload="auto"
      className={className}
      style={{ opacity: 0, ...style }}
    />
  );
}
