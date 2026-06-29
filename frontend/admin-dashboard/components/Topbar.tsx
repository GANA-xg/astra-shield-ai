"use client";

export default function Topbar() {
  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  return (
    <header className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/10 px-8 py-5 backdrop-blur-xl shadow-xl">
      <div>
        <h2 className="text-3xl font-bold text-white">
          Security Operations Center
        </h2>

        <p className="mt-1 text-white/60">
          Monitor phishing threats in real time
        </p>
      </div>

      <div className="text-right">
        <p className="text-white font-semibold">
          Administrator
        </p>

        <p className="text-sm text-white/60">
          {today}
        </p>
      </div>
    </header>
  );
}