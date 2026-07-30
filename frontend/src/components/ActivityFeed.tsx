/* ── StreamGuard AI - Activity Feed Component ─────── */
"use client";

interface ActivityItem {
  id: string;
  type: "read" | "skipped" | "flagged" | "new" | "voice";
  message: string;
  timestamp: Date;
}

interface ActivityFeedProps {
  items: ActivityItem[];
}

const typeConfig = {
  read: { icon: "✅", color: "text-[hsl(152,70%,50%)]" },
  skipped: { icon: "⏭️", color: "text-[hsl(220,10%,60%)]" },
  flagged: { icon: "⚠️", color: "text-[hsl(38,95%,55%)]" },
  new: { icon: "📥", color: "text-[hsl(210,90%,60%)]" },
  voice: { icon: "🎤", color: "text-[hsl(280,80%,60%)]" },
};

export default function ActivityFeed({ items }: ActivityFeedProps) {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-sm font-semibold text-[hsl(220,10%,60%)] uppercase tracking-wider mb-3 px-1">
        Activity Log
      </h2>

      <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
        {items.length === 0 ? (
          <p className="text-xs text-[hsl(220,10%,30%)] text-center py-8">
            No activity yet
          </p>
        ) : (
          items.map((item, i) => {
            const config = typeConfig[item.type];
            return (
              <div
                key={item.id}
                className="flex items-start gap-2 px-2 py-1.5 rounded-lg hover:bg-[hsl(220,16%,14%)] transition-colors animate-slide-down"
                style={{ animationDelay: `${i * 30}ms` }}
              >
                <span className="text-xs mt-0.5">{config.icon}</span>
                <div className="flex-1 min-w-0">
                  <p className={`text-xs ${config.color} truncate`}>
                    {item.message}
                  </p>
                </div>
                <span className="text-[10px] text-[hsl(220,10%,30%)] shrink-0">
                  {formatTime(item.timestamp)}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export type { ActivityItem };
