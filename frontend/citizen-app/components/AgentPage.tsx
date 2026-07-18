'use client';

import Link from 'next/link';
import { ReactNode } from 'react';

interface AgentPageProps {
  title: string;
  description: string;
  children: ReactNode;
}

export default function AgentPage({ title, description, children }: AgentPageProps) {
  return (
    <div className="min-h-screen">
      {/* Top Bar */}
      <header className="sticky top-0 z-40 bg-[var(--canvas)]/80 backdrop-blur-xl border-b border-[var(--hairline)]">
        <div className="max-w-4xl mx-auto px-5 h-16 flex items-center gap-4">
          <Link 
            href="/"
            className="btn-back !h-10 !px-4 !text-sm"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            <span className="hidden sm:inline">Home</span>
          </Link>
          
          <div className="flex-1 min-w-0">
            <h1 className="text-base font-semibold text-[var(--ink)] truncate">{title}</h1>
          </div>
          
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[var(--success)]"/>
            <span className="text-xs text-[var(--muted)] hidden sm:inline">Active</span>
          </div>
        </div>
      </header>

      {/* Page Content */}
      <main className="max-w-4xl mx-auto px-5 py-8 md:py-12">
        {/* Page Header */}
        <div className="mb-8">
          <p className="text-[var(--body)] text-base leading-relaxed max-w-2xl">
            {description}
          </p>
        </div>

        {/* Main Content */}
        {children}
      </main>
    </div>
  );
}
