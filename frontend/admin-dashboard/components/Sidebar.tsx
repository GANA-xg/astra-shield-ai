"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  {
    href: "/",
    label: "Dashboard",
    icon: "📊",
  },
  {
    href: "/detections",
    label: "Detections",
    icon: "🛡",
  },
  {
    href: "/analytics",
    label: "Analytics",
    icon: "📈",
  },
  {
    href: "/reports",
    label: "Reports",
    icon: "📄",
  },
  {
    href: "/settings",
    label: "Settings",
    icon: "⚙️",
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-72 border-r border-white/10 bg-slate-950/80 p-6 backdrop-blur-xl">
      <h1 className="mb-10 text-3xl font-bold text-white">
        🛡 Astra Shield
      </h1>

      <nav className="space-y-3">
        {items.map((item) => {
          const active = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-xl p-4 transition ${
                active
                  ? "bg-cyan-600 text-white"
                  : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}