"use client";

import Sidebar from "@/components/Sidebar";
import Topbar from "@/components/Topbar";

export default function SettingsPage() {
  const services = [
    {
      name: "Backend API",
      status: "Online",
      color: "bg-emerald-500",
    },
    {
      name: "PostgreSQL Database",
      status: "Connected",
      color: "bg-emerald-500",
    },
    {
      name: "Google Safe Browsing",
      status: "Active",
      color: "bg-emerald-500",
    },
    {
      name: "OpenPhish Feed",
      status: "Running",
      color: "bg-emerald-500",
    },
    {
      name: "URLhaus Feed",
      status: "Running",
      color: "bg-emerald-500",
    },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950">
      <div className="flex">

        <Sidebar />

        <div className="flex-1 p-8">

          <Topbar />

          <h1 className="mt-8 text-4xl font-bold text-white">
            ⚙️ System Settings
          </h1>

          <p className="mt-2 text-white/60">
            Monitor the health of Astra Shield services.
          </p>

          <div className="mt-10 grid gap-6">

            {services.map((service) => (
              <div
                key={service.name}
                className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/10 p-6 backdrop-blur-xl"
              >
                <div>
                  <h2 className="text-xl font-semibold text-white">
                    {service.name}
                  </h2>

                  <p className="mt-1 text-white/50">
                    Service Status
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <div
                    className={`h-3 w-3 rounded-full ${service.color} animate-pulse`}
                  />

                  <span className="font-semibold text-emerald-300">
                    {service.status}
                  </span>
                </div>
              </div>
            ))}

          </div>

          <div className="mt-10 rounded-3xl border border-white/10 bg-white/10 p-8 backdrop-blur-xl">

            <h2 className="text-2xl font-bold text-white">
              Platform Information
            </h2>

            <div className="mt-6 grid gap-6 md:grid-cols-2">

              <InfoCard
                title="Application"
                value="Astra Shield"
              />

              <InfoCard
                title="Version"
                value="v1.0.0"
              />

              <InfoCard
                title="Environment"
                value="Development"
              />

              <InfoCard
                title="Framework"
                value="Next.js + FastAPI"
              />

            </div>

          </div>

        </div>

      </div>
    </main>
  );
}

function InfoCard({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl bg-slate-900/40 p-5">
      <p className="text-sm text-white/50">
        {title}
      </p>

      <h3 className="mt-2 text-xl font-semibold text-white">
        {value}
      </h3>
    </div>
  );
}