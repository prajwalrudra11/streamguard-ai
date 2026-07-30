/* ── StreamGuard AI - Stats Panel Component ──────── */
"use client";

import type { StreamStats } from "@/types";

interface StatsPanelProps {
  stats: StreamStats;
  isConnected: boolean;
  isListening: boolean;
}

export default function StatsPanel({ stats, isConnected, isListening }: StatsPanelProps) {
  const readRate =
    stats.total_chats > 0
      ? Math.round((stats.chats_read / stats.total_chats) * 100)
      : 0;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
      {/* Revenue */}
      <div className="glass rounded-xl p-4 animate-slide-in-up">
        <div className="text-xs text-[hsl(220,10%,60%)] uppercase tracking-wider mb-1">
          Revenue
        </div>
        <div className="text-2xl font-bold gradient-text animate-count-up">
          ${stats.total_revenue.toFixed(2)}
        </div>
      </div>

      {/* Total Chats */}
      <div className="glass rounded-xl p-4 animate-slide-in-up" style={{ animationDelay: "50ms" }}>
        <div className="text-xs text-[hsl(220,10%,60%)] uppercase tracking-wider mb-1">
          Total Chats
        </div>
        <div className="text-2xl font-bold text-[hsl(0,0%,95%)]">
          {stats.total_chats}
        </div>
      </div>

      {/* Read Rate */}
      <div className="glass rounded-xl p-4 animate-slide-in-up" style={{ animationDelay: "100ms" }}>
        <div className="text-xs text-[hsl(220,10%,60%)] uppercase tracking-wider mb-1">
          Read Rate
        </div>
        <div className="flex items-end gap-1">
          <span className="text-2xl font-bold text-[hsl(152,70%,50%)]">{readRate}%</span>
          <span className="text-xs text-[hsl(220,10%,40%)] mb-1">
            ({stats.chats_read}/{stats.total_chats})
          </span>
        </div>
      </div>

      {/* Queue Size */}
      <div className="glass rounded-xl p-4 animate-slide-in-up" style={{ animationDelay: "150ms" }}>
        <div className="text-xs text-[hsl(220,10%,60%)] uppercase tracking-wider mb-1">
          In Queue
        </div>
        <div className="text-2xl font-bold text-[hsl(38,95%,55%)]">
          {stats.queue_size}
        </div>
      </div>

      {/* Connection Status */}
      <div className="glass rounded-xl p-4 animate-slide-in-up" style={{ animationDelay: "200ms" }}>
        <div className="text-xs text-[hsl(220,10%,60%)] uppercase tracking-wider mb-1">
          Connection
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`w-2.5 h-2.5 rounded-full ${
              isConnected
                ? "bg-[hsl(152,70%,50%)] shadow-[0_0_8px_hsl(152,70%,50%,0.5)]"
                : "bg-[hsl(0,75%,55%)]"
            }`}
          />
          <span className="text-sm font-medium">
            {isConnected ? "Live" : "Offline"}
          </span>
        </div>
      </div>

      {/* Voice Status */}
      <div className="glass rounded-xl p-4 animate-slide-in-up" style={{ animationDelay: "250ms" }}>
        <div className="text-xs text-[hsl(220,10%,60%)] uppercase tracking-wider mb-1">
          Voice
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`w-2.5 h-2.5 rounded-full ${
              isListening
                ? "bg-[hsl(280,80%,60%)] shadow-[0_0_8px_hsl(280,80%,60%,0.5)] animate-pulse"
                : "bg-[hsl(220,10%,40%)]"
            }`}
          />
          <span className="text-sm font-medium">
            {isListening ? "🎤 Listening" : "Muted"}
          </span>
        </div>
      </div>
    </div>
  );
}
