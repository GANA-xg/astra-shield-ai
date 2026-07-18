"use client";

import AdminLayout from "@/components/AdminLayout";

export default function SettingsPage() {
  const services = [
    { name: "Backend API", status: "Online" },
    { name: "PostgreSQL Database", status: "Connected" },
    { name: "Google Safe Browsing", status: "Active" },
    { name: "OpenPhish Feed", status: "Running" },
    { name: "URLhaus Feed", status: "Running" },
  ];

  return (
    <AdminLayout>
      <h1 className="mb-2 text-2xl font-semibold text-[var(--ink)]">System Settings</h1>
      <p className="mb-8 text-[var(--muted)]">Monitor the health of Astra Shield services.</p>

      <div className="space-y-4 mb-8">
        {services.map((service) => (
          <div key={service.name} className="card-flat p-6 flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-[var(--ink)]">{service.name}</h2>
              <p className="mt-1 text-sm text-[var(--muted)]">Service Status</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="h-3 w-3 rounded-full bg-[var(--success)] animate-pulse" />
              <span className="font-medium text-[var(--success)]">{service.status}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="card-flat p-6">
        <h2 className="text-lg font-semibold text-[var(--ink)]">Platform Information</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="card-flat p-4">
            <p className="text-sm text-[var(--muted)]">Application</p>
            <h3 className="mt-1 text-base font-semibold text-[var(--ink)]">Astra Shield</h3>
          </div>
          <div className="card-flat p-4">
            <p className="text-sm text-[var(--muted)]">Version</p>
            <h3 className="mt-1 text-base font-semibold text-[var(--ink)]">v1.0.0</h3>
          </div>
          <div className="card-flat p-4">
            <p className="text-sm text-[var(--muted)]">Environment</p>
            <h3 className="mt-1 text-base font-semibold text-[var(--ink)]">Development</h3>
          </div>
          <div className="card-flat p-4">
            <p className="text-sm text-[var(--muted)]">Framework</p>
            <h3 className="mt-1 text-base font-semibold text-[var(--ink)]">Next.js + FastAPI</h3>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
