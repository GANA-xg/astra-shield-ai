"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Dashboard", icon: "📊" },
  { href: "/detections", label: "Detections", icon: "🛡️" },
  { href: "/analytics", label: "Analytics", icon: "📈" },
  { href: "/reports", label: "Reports", icon: "📄" },
  { href: "/settings", label: "Settings", icon: "⚙️" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r border-[var(--hairline)] bg-[var(--surface-strong)] p-6 flex flex-col">
        <div className="mb-8">
          <h1 className="text-xl font-semibold text-[var(--ink)] flex items-center gap-2">
            <span className="text-[var(--primary)]">🛡️</span>
            Astra Shield
          </h1>
          <p className="text-xs text-[var(--muted)] mt-1">Security Operations Center</p>
        </div>

        <nav className="flex-1 space-y-1">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`nav-item flex items-center gap-3 ${active ? "active" : ""}`}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto pt-6 border-t border-[var(--hairline)]">
          <p className="text-xs text-[var(--muted-soft)]">v1.0.0</p>
        </div>
      </aside>

      <div className="flex-1 flex flex-col">
        <header className="flex items-center justify-between p-6 border-b border-[var(--hairline)] bg-[var(--surface-strong)]">
          <div>
            <h2 className="text-xl font-semibold text-[var(--ink)]">Security Operations Center</h2>
            <p className="text-sm text-[var(--muted)]">Monitor phishing threats in real time</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium text-[var(--ink)]">Administrator</p>
            <p className="text-xs text-[var(--muted)]">{today}</p>
          </div>
        </header>

        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
