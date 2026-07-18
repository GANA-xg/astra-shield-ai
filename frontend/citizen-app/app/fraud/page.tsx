"use client";

import { useState } from "react";
import AgentPage from "@/components/AgentPage";

interface FraudNode {
  id: string;
  type: "phone" | "email" | "url" | "account";
  value: string;
  risk: "high" | "medium" | "low";
}

interface FraudEdge {
  from: string;
  to: string;
  relation: string;
}

interface FraudGraph {
  nodes: FraudNode[];
  edges: FraudEdge[];
  summary: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export default function FraudPage() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<FraudGraph | null>(null);
  const [loading, setLoading] = useState(false);

  const analyzeGraph = async () => {
    if (!input.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/fraud/graph`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });
      const data = await res.json();
      setResult(data);
    } catch {
      setResult({
        nodes: [
          { id: "1", type: "phone", value: input, risk: "high" },
          { id: "2", type: "account", value: "Linked Account", risk: "medium" },
          { id: "3", type: "url", value: "Suspicious URL", risk: "high" },
        ],
        edges: [
          { from: "1", to: "2", relation: "calls" },
          { from: "2", to: "3", relation: "uses" },
        ],
        summary: "Unable to connect to backend. Showing sample fraud network for demonstration.",
      });
    }
    setLoading(false);
  };

  const riskColor = (risk: string) =>
    risk === "high" ? "bg-[var(--error)]" :
    risk === "medium" ? "bg-[var(--warning)]" :
    "bg-[var(--success)]";

  const typeIcon = (type: string) => {
    switch (type) {
      case "phone": return "📞";
      case "email": return "📧";
      case "url": return "🔗";
      case "account": return "👤";
      default: return "⚠️";
    }
  };

  return (
    <AgentPage
      title="Fraud Graph"
      description="Visualize fraud networks and connections between suspicious activities, phone numbers, and accounts."
    >
      <div className="card-flat p-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter a phone number, email, or URL to analyze..."
            className="input-field flex-1"
            onKeyDown={(e) => e.key === "Enter" && analyzeGraph()}
          />
          <button onClick={analyzeGraph} disabled={loading || !input.trim()} className="btn-primary shrink-0">
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="5" r="3"/>
                  <circle cx="5" cy="19" r="3"/>
                  <circle cx="19" cy="19" r="3"/>
                  <path d="M12 8v4M8.5 16.5l2-4M15.5 16.5l-2-4"/>
                </svg>
                Analyze Network
              </>
            )}
          </button>
        </div>

        {result && (
          <div className="mt-8">
            {/* Summary */}
            <div className="mb-6 p-4 rounded-xl bg-[var(--surface-soft)] border border-[var(--hairline)]">
              <p className="text-sm text-[var(--body)] leading-relaxed">{result.summary}</p>
            </div>

            {/* Graph Visualization */}
            <div className="relative min-h-[300px] rounded-xl bg-[var(--canvas)] border border-[var(--hairline)] p-6 overflow-hidden">
              {/* Nodes */}
              <div className="flex flex-wrap justify-center gap-6 relative z-10">
                {result.nodes.map((node) => (
                  <div
                    key={node.id}
                    className="flex flex-col items-center gap-2"
                  >
                    <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-2xl ${riskColor(node.risk)}`}>
                      {typeIcon(node.type)}
                    </div>
                    <div className="text-center">
                      <p className="text-xs font-medium text-[var(--ink)] max-w-[100px] truncate">{node.value}</p>
                      <p className="text-[10px] text-[var(--muted)] capitalize">{node.type}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Edges (simplified visualization) */}
              {result.edges.length > 0 && (
                <div className="mt-8 space-y-2">
                  <p className="text-xs font-medium text-[var(--muted)] mb-3">Connections</p>
                  {result.edges.map((edge, i) => {
                    const fromNode = result.nodes.find(n => n.id === edge.from);
                    const toNode = result.nodes.find(n => n.id === edge.to);
                    return (
                      <div key={i} className="flex items-center gap-2 text-xs">
                        <span className="text-[var(--ink)]">{fromNode?.value}</span>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" strokeWidth="2">
                          <path d="M5 12h14M12 5l7 7-7 7"/>
                        </svg>
                        <span className="text-[var(--muted)] italic">{edge.relation}</span>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" strokeWidth="2">
                          <path d="M5 12h14M12 5l7 7-7 7"/>
                        </svg>
                        <span className="text-[var(--ink)]">{toNode?.value}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Legend */}
            <div className="mt-6 flex flex-wrap gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[var(--error)]"/>
                <span className="text-[var(--body)]">High Risk</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[var(--warning)]"/>
                <span className="text-[var(--body)]">Medium Risk</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[var(--success)]"/>
                <span className="text-[var(--body)]">Low Risk</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </AgentPage>
  );
}
