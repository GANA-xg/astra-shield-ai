"use client";

import Link from "next/link";
import Navbar from "@/components/Navbar";

const features = [
  {
    title: "🌐 URL Phishing Scanner",
    description:
      "Analyze suspicious URLs using AI and threat intelligence.",
    href: "/phishing",
  },
  {
    title: "📞 Scam Call Detection",
    description:
      "Detect fraudulent phone calls using AI analysis.",
    href: "/scam",
  },
  {
    title: "📩 SMS Scam Detection",
    description:
      "Identify phishing and scam SMS messages instantly.",
    href: "/sms",
  },
  {
    title: "🛡 Citizen Safety Assistant",
    description:
      "AI assistant for citizen safety guidance and incident response.",
    href: "/citizen-safety",
  },
  {
    title: "📊 Dashboard",
    description:
      "View statistics, trends, and security analytics.",
    href: "/dashboard",
  },
  {
    title: "📜 History",
    description:
      "Review previous analyses and investigations.",
    href: "/history",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-8">
      <div className="mx-auto max-w-7xl">
        <Navbar />

        <div className="mb-12 text-center">
          <h1 className="mb-4 text-5xl font-extrabold text-white">
            🛡 Astra Shield AI
          </h1>

          <p className="mx-auto max-w-3xl text-lg text-white/70">
            An AI-powered platform for phishing detection,
            scam prevention, cyber awareness, and citizen safety.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Link
              key={feature.href}
              href={feature.href}
              className="rounded-3xl border border-white/20 bg-white/10 p-8 shadow-2xl backdrop-blur-2xl transition-all duration-300 hover:-translate-y-2 hover:bg-white/15"
            >
              <h2 className="mb-4 text-2xl font-bold text-white">
                {feature.title}
              </h2>

              <p className="text-white/70 leading-7">
                {feature.description}
              </p>

              <div className="mt-6 text-blue-300 font-semibold">
                Open →
              </div>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}