'use client';

import Link from 'next/link';

const agents = [
  {
    id: 'scam',
    title: 'Scam Call Detection',
    description: 'Analyze call recordings and transcripts to identify scam patterns and fraudulent behavior.',
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
      </svg>
    ),
    color: '#ff385c',
    href: '/scam',
  },
  {
    id: 'currency',
    title: 'Currency Detection',
    description: 'Verify currency authenticity using AI-powered image analysis and pattern recognition.',
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 6v12M15 9.5c0-1.38-1.34-2.5-3-2.5s-3 1.12-3 2.5 1.34 2.5 3 2.5 3 1.12 3 2.5-1.34 2.5-3 2.5"/>
      </svg>
    ),
    color: '#10b981',
    href: '/currency',
  },
  {
    id: 'fraud',
    title: 'Fraud Graph',
    description: 'Visualize fraud networks and connections between suspicious activities and entities.',
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="5" r="3"/>
        <circle cx="5" cy="19" r="3"/>
        <circle cx="19" cy="19" r="3"/>
        <path d="M12 8v4M8.5 16.5l2-4M15.5 16.5l-2-4"/>
      </svg>
    ),
    color: '#f59e0b',
    href: '/fraud',
  },
  {
    id: 'phishing',
    title: 'Phishing Detection',
    description: 'Scan URLs and messages to detect phishing attempts and malicious links.',
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
      </svg>
    ),
    color: '#3b82f6',
    href: '/phishing',
  },
  {
    id: 'citizen',
    title: 'Citizen Bot',
    description: 'Get personalized safety guidance and report incidents with our AI assistant.',
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2a7 7 0 0 1 7 7v1a7 7 0 0 1-14 0V9a7 7 0 0 1 7-7z"/>
        <path d="M9 14v.5"/>
        <path d="M15 14v.5"/>
        <path d="M9 18h6"/>
        <path d="M12 2v2"/>
      </svg>
    ),
    color: '#8b5cf6',
    href: '/citizen-safety',
  },
];

export default function HomePage() {

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-5 pt-20 pb-16 md:pt-32 md:pb-24">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-[radial-gradient(circle,rgba(255,56,92,0.08)_0%,transparent_70%)]"/>
        </div>
        
        <div className="relative max-w-4xl mx-auto text-center animate-fade-in-up">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--surface-soft)] border border-[var(--hairline)] mb-8">
            <div className="w-2 h-2 rounded-full bg-[var(--success)] animate-pulse"/>
            <span className="text-sm font-medium text-[var(--body)]">AI Protection Active</span>
          </div>
          
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-semibold text-[var(--ink)] tracking-tight leading-tight mb-6">
            Stay Safe with
            <span className="block text-[var(--primary)]">Astra Shield AI</span>
          </h1>
          
          <p className="text-lg md:text-xl text-[var(--body)] max-w-2xl mx-auto leading-relaxed">
            Your personal cybersecurity companion. Detect scams, verify authenticity, 
            and protect yourself from digital threats with our suite of AI-powered agents.
          </p>
        </div>
      </section>

      {/* Features Grid */}
      <section className="px-5 pb-24 md:pb-32">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {agents.map((agent, index) => (
              <Link
                key={agent.id}
                href={agent.href}
                className="group card card-interactive p-6 md:p-8 transition-all duration-300 animate-fade-in-up"
                style={{ animationDelay: `${100 + index * 80}ms` }}
              >
                <div 
                  className="w-14 h-14 rounded-2xl flex items-center justify-center mb-5 transition-transform duration-300 group-hover:scale-110"
                  style={{ 
                    backgroundColor: `${agent.color}15`,
                    color: agent.color 
                  }}
                >
                  {agent.icon}
                </div>
                
                <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">
                  {agent.title}
                </h3>
                
                <p className="text-sm text-[var(--body)] leading-relaxed">
                  {agent.description}
                </p>
                
                <div className="mt-6 flex items-center gap-2 text-sm font-medium text-[var(--muted)] group-hover:text-[var(--ink)] transition-colors">
                  <span>Get Started</span>
                  <svg className="w-4 h-4 transition-transform group-hover:translate-x-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[var(--hairline)] py-8 px-5">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            <span className="text-sm font-medium text-[var(--ink)]">Astra Shield</span>
          </div>
          <p className="text-sm text-[var(--muted)]">
            Protecting citizens with AI-powered cybersecurity
          </p>
        </div>
      </footer>
    </div>
  );
}
