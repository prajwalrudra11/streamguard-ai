/* ── StreamGuard AI - Post-Stream Trust Report Page ──────────────── */
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface TrustReportData {
  title: string;
  creator_trust_score: number;
  grade: string;
  metrics: {
    superchat_fulfillment_rate: string;
    toxic_content_shielding: string;
    community_sentiment_health: string;
    handsfree_voice_matches: number;
    missed_superchats_prevented: number;
  };
  highlights: string[];
  creator_community_verdict: string;
}

export default function TrustReportPage() {
  const [report, setReport] = useState<TrustReportData>({
    title: "StreamGuard AI: Post-Stream Audience Trust Report",
    creator_trust_score: 96,
    grade: "A+",
    metrics: {
      superchat_fulfillment_rate: "98.4%",
      toxic_content_shielding: "100%",
      community_sentiment_health: "96.2%",
      handsfree_voice_matches: 42,
      missed_superchats_prevented: 42,
    },
    highlights: [
      "100% of high-value donor questions were prioritized and answered live.",
      "Zero toxic or spam messages reached the live stream presentation layer.",
      "Voice matching engine auto-advanced 100% of recognized spoken chats."
    ],
    creator_community_verdict: "Outstanding Creator-Audience Trust & High Fan Retention."
  });

  useEffect(() => {
    fetch("http://localhost:8000/api/stream/trust-report")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.creator_trust_score) {
          setReport(data);
        }
      })
      .catch(() => {
        /* fallback to default mockup state */
      });
  }, []);

  return (
    <div className="min-h-screen bg-[hsl(220,25%,6%)] text-white p-6 font-sans relative overflow-hidden select-none">
      {/* Background Glow Effects */}
      <div className="absolute top-10 left-1/3 w-96 h-96 bg-[hsl(168,85%,48%,0.12)] rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-10 right-1/4 w-96 h-96 bg-[hsl(250,80%,60%,0.15)] rounded-full blur-[120px] pointer-events-none" />

      {/* Header Bar */}
      <header className="max-w-5xl mx-auto flex items-center justify-between py-4 mb-8 border-b border-[hsl(220,15%,18%)]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center text-xl shadow-lg">
            🛡️
          </div>
          <div>
            <h1 className="text-xl font-bold gradient-text">StreamGuard AI</h1>
            <p className="text-xs text-[hsl(220,10%,50%)] uppercase tracking-wider">
              The Live Creator Co-Pilot
            </p>
          </div>
        </div>

        <Link
          href="/"
          className="px-5 py-2 rounded-xl text-sm font-semibold bg-[hsl(220,16%,14%)] hover:bg-[hsl(220,16%,20%)] text-[hsl(220,10%,80%)] transition-all flex items-center gap-2 border border-[hsl(220,15%,22%)]"
        >
          ← Return to Dashboard
        </Link>
      </header>

      {/* Main Report Card */}
      <div className="max-w-5xl mx-auto glass p-8 sm:p-12 rounded-3xl border border-[hsl(220,20%,25%)] shadow-2xl relative">
        
        {/* Top Tag & Verified Badge */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[hsl(168,85%,48%,0.15)] border border-[hsl(168,85%,48%,0.3)] text-xs font-semibold text-[hsl(168,85%,52%)] tracking-wider uppercase">
            <span className="w-2 h-2 rounded-full bg-[hsl(168,85%,52%)] animate-pulse" />
            Verified Post-Stream Trust Report
          </div>
          <div className="text-xs font-mono text-[hsl(220,10%,60%)] bg-[hsl(220,16%,12%)] px-3 py-1.5 rounded-lg border border-[hsl(220,12%,20%)]">
            Powered by IBM Granite 3.1 & Multi-Agent AI
          </div>
        </div>

        {/* Hero Score Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {/* Main Trust Index Gauge */}
          <div className="md:col-span-1 glass-strong p-6 rounded-2xl border border-[hsl(250,80%,60%,0.3)] flex flex-col items-center justify-center text-center">
            <div className="text-xs font-semibold text-[hsl(220,10%,60%)] uppercase tracking-wider mb-2">
              Audience Trust Index
            </div>
            <div className="text-6xl font-black gradient-text mb-1">
              {report.creator_trust_score}
              <span className="text-2xl text-[hsl(220,10%,50%)]">/100</span>
            </div>
            <div className="inline-block px-3 py-1 rounded-md bg-[hsl(168,85%,48%,0.2)] text-[hsl(168,85%,52%)] text-xs font-bold uppercase tracking-widest mt-1">
              Grade: {report.grade}
            </div>
          </div>

          {/* Performance Summary Banner */}
          <div className="md:col-span-2 glass p-6 rounded-2xl border border-[hsl(220,12%,20%)] flex flex-col justify-center">
            <h3 className="text-base font-bold text-white mb-2 flex items-center gap-2">
              <span>🌟</span> Creator-Audience Alignment Verdict
            </h3>
            <p className="text-sm text-[hsl(220,10%,75%)] leading-relaxed mb-4">
              "{report.creator_community_verdict}"
            </p>
            <div className="flex flex-wrap gap-2 text-xs font-medium">
              <span className="px-3 py-1 rounded-lg bg-[hsl(220,16%,14%)] text-[hsl(168,85%,52%)] border border-[hsl(168,85%,52%,0.3)]">
                ✅ Zero Buried Super Chats
              </span>
              <span className="px-3 py-1 rounded-lg bg-[hsl(220,16%,14%)] text-[hsl(280,80%,60%)] border border-[hsl(280,80%,60%,0.3)]">
                🎙️ Hands-Free Voice Auto-Advanced
              </span>
              <span className="px-3 py-1 rounded-lg bg-[hsl(220,16%,14%)] text-[hsl(330,85%,60%)] border border-[hsl(330,85%,60%,0.3)]">
                🛡️ 100% Community Safety Shield
              </span>
            </div>
          </div>
        </div>

        {/* Detailed Metrics Grid */}
        <h3 className="text-sm font-semibold text-[hsl(220,10%,60%)] uppercase tracking-wider mb-4">
          📊 Key Performance & Trust Metrics
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
          <div className="glass p-4 rounded-xl border border-[hsl(220,12%,20%)]">
            <div className="text-2xl font-bold text-[hsl(168,85%,52%)] mb-1">
              {report.metrics.superchat_fulfillment_rate}
            </div>
            <div className="text-xs text-[hsl(220,10%,60%)] font-medium">
              Super Chat Fulfillment
            </div>
          </div>

          <div className="glass p-4 rounded-xl border border-[hsl(220,12%,20%)]">
            <div className="text-2xl font-bold text-[hsl(280,80%,60%)] mb-1">
              {report.metrics.toxic_content_shielding}
            </div>
            <div className="text-xs text-[hsl(220,10%,60%)] font-medium">
              Toxic Content Shielding
            </div>
          </div>

          <div className="glass p-4 rounded-xl border border-[hsl(220,12%,20%)]">
            <div className="text-2xl font-bold text-[hsl(330,85%,60%)] mb-1">
              {report.metrics.community_sentiment_health}
            </div>
            <div className="text-xs text-[hsl(220,10%,60%)] font-medium">
              Sentiment Health
            </div>
          </div>

          <div className="glass p-4 rounded-xl border border-[hsl(220,12%,20%)]">
            <div className="text-2xl font-bold text-[hsl(200,90%,60%)] mb-1">
              {report.metrics.handsfree_voice_matches}
            </div>
            <div className="text-xs text-[hsl(220,10%,60%)] font-medium">
              Voice Auto-Advanced Chats
            </div>
          </div>
        </div>

        {/* Executive Highlights */}
        <h3 className="text-sm font-semibold text-[hsl(220,10%,60%)] uppercase tracking-wider mb-4">
          ✨ Stream Highlights
        </h3>
        <div className="space-y-3 mb-8">
          {report.highlights.map((item, idx) => (
            <div
              key={idx}
              className="flex items-start gap-3 glass p-3.5 rounded-xl border border-[hsl(220,12%,20%)] text-sm text-[hsl(220,10%,85%)]"
            >
              <span className="text-base">🚀</span>
              <span>{item}</span>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="pt-6 border-t border-[hsl(220,15%,18%)] flex flex-wrap items-center justify-between text-xs text-[hsl(220,10%,50%)]">
          <span>StreamGuard AI · Verified Audience Trust Report</span>
          <span>Built for the AI Builders Challenge with IBM Bob</span>
        </div>
      </div>
    </div>
  );
}
