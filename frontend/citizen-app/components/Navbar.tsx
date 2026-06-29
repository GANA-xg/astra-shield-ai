"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "URL Scanner" },
  { href: "/sms", label: "SMS Scanner" },
  { href: "/history", label: "History" },
  { href: "/dashboard", label: "Dashboard" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="mb-8 rounded-2xl border border-slate-700 bg-slate-900/80 backdrop-blur">
      <div className="flex flex-col gap-4 p-6 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">
            🛡 Astra Shield AI
          </h1>

          <p className="mt-1 text-slate-300">
            AI-Powered Cyber Threat Detection Platform
          </p>
        </div>

        <nav className="flex flex-wrap gap-3">
          {links.map((link) => {
            const active = pathname === link.href;

            return (
              <Link
                key={link.href}
                href={link.href}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                  active
                    ? "bg-blue-600 text-white"
                    : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}