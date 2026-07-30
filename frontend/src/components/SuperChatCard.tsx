/* ── StreamGuard AI - Super Chat Card Component ──── */
"use client";

import type { SuperChat, ChatAction } from "@/types";

interface SuperChatCardProps {
  chat: SuperChat;
  isCurrent?: boolean;
  onAction?: (chatId: string, action: ChatAction) => void;
  showActions?: boolean;
}

const tierConfig = {
  bronze: { label: "Bronze", emoji: "🥉", class: "tier-bronze" },
  silver: { label: "Silver", emoji: "🥈", class: "tier-silver" },
  gold: { label: "Gold", emoji: "🥇", class: "tier-gold" },
  diamond: { label: "Diamond", emoji: "💎", class: "tier-diamond" },
};

const intentEmoji: Record<string, string> = {
  question: "❓",
  compliment: "💖",
  request: "🙏",
  story: "📖",
  greeting: "👋",
  other: "💬",
};

export default function SuperChatCard({
  chat,
  isCurrent = false,
  onAction,
  showActions = true,
}: SuperChatCardProps) {
  const tier = tierConfig[chat.tier];
  const amountColor =
    chat.amount >= 50
      ? "text-[hsl(195,100%,65%)]"
      : chat.amount >= 20
      ? "text-[hsl(45,90%,55%)]"
      : chat.amount >= 10
      ? "text-[hsl(220,10%,65%)]"
      : "text-[hsl(30,60%,50%)]";

  return (
    <div
      className={`
        relative rounded-xl p-4 transition-all duration-300
        ${
          isCurrent
            ? "glass-strong ring-2 ring-[hsl(168,85%,52%)] animate-pulse-glow"
            : "glass hover:bg-[hsl(220,16%,14%)]"
        }
        ${chat.risk_level === "high" ? "ring-1 ring-[hsl(0,75%,55%,0.4)]" : ""}
        animate-slide-in-right
      `}
    >
      {/* Header: Author + Amount */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {/* Avatar placeholder */}
          <div className="w-8 h-8 rounded-full gradient-primary flex items-center justify-center text-sm font-bold text-white shrink-0">
            {chat.author_name.charAt(0).toUpperCase()}
          </div>
          <div>
            <span className="font-semibold text-sm">{chat.author_name}</span>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span
                className={`text-xs px-1.5 py-0.5 rounded border ${tier.class}`}
              >
                {tier.emoji} {tier.label}
              </span>
              <span className={`text-xs sentiment-${chat.sentiment}`}>
                {intentEmoji[chat.intent]} {chat.intent}
              </span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <span className={`text-lg font-bold ${amountColor}`}>
            ${chat.amount.toFixed(2)}
          </span>
          <div className="text-xs text-[hsl(220,10%,40%)]">
            P: {chat.priority_score}
          </div>
        </div>
      </div>

      {/* Message */}
      <p className="text-sm text-[hsl(0,0%,85%)] mb-2 leading-relaxed">
        {chat.message}
      </p>

      {/* Suggested Reply */}
      {chat.suggested_reply && (
        <div className="bg-[hsl(168,85%,52%,0.08)] border border-[hsl(168,85%,52%,0.2)] rounded-lg px-3 py-2 mb-2">
          <span className="text-xs text-[hsl(168,85%,52%)] font-medium">
            💡 Suggested Reply
          </span>
          <p className="text-xs text-[hsl(0,0%,80%)] mt-0.5">
            {chat.suggested_reply}
          </p>
        </div>
      )}

      {/* Risk Warning */}
      {chat.risk_level !== "low" && (
        <div
          className={`text-xs px-2 py-1 rounded mb-2 ${
            chat.risk_level === "high"
              ? "bg-[hsl(0,75%,55%,0.1)] text-[hsl(0,75%,55%)]"
              : "bg-[hsl(38,95%,55%,0.1)] text-[hsl(38,95%,55%)]"
          }`}
        >
          ⚠️ {chat.risk_level === "high" ? "Flagged content" : "Review suggested"}
        </div>
      )}

      {/* Action Buttons */}
      {showActions && onAction && (
        <div className="flex gap-2 pt-1">
          <button
            onClick={() => onAction(chat.id, "accept")}
            className="flex-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-[hsl(152,70%,50%,0.15)] text-[hsl(152,70%,50%)] hover:bg-[hsl(152,70%,50%,0.25)] transition-colors cursor-pointer"
          >
            ✅ Accept
          </button>
          <button
            onClick={() => onAction(chat.id, "skip")}
            className="flex-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-[hsl(0,75%,55%,0.15)] text-[hsl(0,75%,55%)] hover:bg-[hsl(0,75%,55%,0.25)] transition-colors cursor-pointer"
          >
            ⏭️ Skip
          </button>
          <button
            onClick={() => onAction(chat.id, "pin")}
            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-[hsl(38,95%,55%,0.15)] text-[hsl(38,95%,55%)] hover:bg-[hsl(38,95%,55%,0.25)] transition-colors cursor-pointer"
          >
            📌
          </button>
        </div>
      )}
    </div>
  );
}
