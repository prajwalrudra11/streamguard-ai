/* ── StreamGuard AI - OBS Stream Overlay Page ─────── */
/* Add as Browser Source in OBS: http://localhost:3000/overlay */
"use client";

import { useState, useCallback, useEffect } from "react";
import type { SuperChat, WSEvent } from "@/types";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useVoiceRecognition } from "@/hooks/useVoiceRecognition";

const tierColors: Record<string, string> = {
  bronze: "#cd7f32",
  silver: "#a0a8b4",
  gold: "#f0c040",
  diamond: "#4dd9ff",
};

const tierEmoji: Record<string, string> = {
  bronze: "🥉",
  silver: "🥈",
  gold: "🥇",
  diamond: "💎",
};

export default function OverlayPage() {
  const [currentChat, setCurrentChat] = useState<SuperChat | null>(null);
  const [isExiting, setIsExiting] = useState(false);

  const handleWSMessage = useCallback((event: WSEvent) => {
    if (event.type === "new_superchat" || event.type === "display_chat") {
      const chat = (event as unknown as { data: SuperChat }).data;
      setIsExiting(false);
      setCurrentChat(chat);
    }

    if (event.type === "chat_read" || event.type === "chat_action") {
      setIsExiting(true);
      setTimeout(() => {
        setCurrentChat(null);
        setIsExiting(false);
      }, 500);
    }
  }, []);

  const { connect, send } = useWebSocket(handleWSMessage);

  // Voice recognition for auto-read detection
  const handleVoiceTranscript = useCallback(
    (text: string) => {
      send({
        type: "voice_transcript",
        text,
        timestamp: new Date().toISOString(),
      });
    },
    [send]
  );

  const { startListening } = useVoiceRecognition({
    onTranscript: handleVoiceTranscript,
  });

  useEffect(() => {
    connect();
    startListening();
  }, [connect, startListening]);

  if (!currentChat) return null;

  const tierColor = tierColors[currentChat.tier] || tierColors.bronze;

  return (
    <div className="min-h-screen bg-transparent flex items-end justify-end p-6">
      <div
        className={`
          max-w-sm w-full rounded-2xl overflow-hidden
          transition-all duration-500 ease-out
          ${isExiting ? "opacity-0 translate-x-12 scale-95" : "opacity-100 translate-x-0 scale-100"}
        `}
        style={{
          background: "rgba(10, 12, 18, 0.92)",
          backdropFilter: "blur(20px)",
          border: `2px solid ${tierColor}40`,
          boxShadow: `0 0 30px ${tierColor}20, 0 8px 32px rgba(0,0,0,0.5)`,
          animation: isExiting ? "none" : "overlaySlideIn 0.5s ease-out",
        }}
      >
        {/* Tier accent bar */}
        <div
          className="h-1"
          style={{
            background: `linear-gradient(90deg, ${tierColor}, ${tierColor}80, transparent)`,
          }}
        />

        <div className="p-4">
          {/* Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2.5">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-base"
                style={{
                  background: `linear-gradient(135deg, ${tierColor}, ${tierColor}80)`,
                }}
              >
                {currentChat.author_name.charAt(0).toUpperCase()}
              </div>
              <div>
                <div className="font-semibold text-white text-sm">
                  {currentChat.author_name}
                </div>
                <div
                  className="text-xs font-medium"
                  style={{ color: tierColor }}
                >
                  {tierEmoji[currentChat.tier]} {currentChat.tier.toUpperCase()}
                </div>
              </div>
            </div>
            <div
              className="text-xl font-bold"
              style={{ color: tierColor }}
            >
              ${currentChat.amount.toFixed(2)}
            </div>
          </div>

          {/* Message */}
          <p className="text-white/90 text-sm leading-relaxed mb-3">
            {currentChat.message}
          </p>

          {/* Suggested Reply */}
          {currentChat.suggested_reply && (
            <div
              className="rounded-lg px-3 py-2 text-xs"
              style={{
                background: `${tierColor}10`,
                border: `1px solid ${tierColor}30`,
                color: `${tierColor}`,
              }}
            >
              💡 {currentChat.suggested_reply}
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        @keyframes overlaySlideIn {
          from {
            opacity: 0;
            transform: translateX(60px) scale(0.9);
          }
          to {
            opacity: 1;
            transform: translateX(0) scale(1);
          }
        }
      `}</style>
    </div>
  );
}
