/* ── StreamGuard AI - Dashboard Page ──────────────── */
"use client";

import { useState, useCallback, useEffect } from "react";
import type { SuperChat, ChatAction, StreamStats, WSEvent } from "@/types";
import type { ActivityItem } from "@/components/ActivityFeed";
import Header from "@/components/Header";
import StatsPanel from "@/components/StatsPanel";
import ChatQueue from "@/components/ChatQueue";
import SuperChatCard from "@/components/SuperChatCard";
import ActivityFeed from "@/components/ActivityFeed";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useVoiceRecognition } from "@/hooks/useVoiceRecognition";
import { api } from "@/lib/api";

export default function Dashboard() {
  // ── State ──────────────────────────────────────────
  const [showDashboard, setShowDashboard] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [currentChat, setCurrentChat] = useState<SuperChat | null>(null);
  const [queue, setQueue] = useState<SuperChat[]>([]);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [stats, setStats] = useState<StreamStats>({
    total_revenue: 0,
    total_chats: 0,
    chats_read: 0,
    chats_skipped: 0,
    queue_size: 0,
  });

  // ── Activity Logger ────────────────────────────────
  const addActivity = useCallback(
    (type: ActivityItem["type"], message: string) => {
      setActivity((prev) => [
        {
          id: `${Date.now()}-${Math.random()}`,
          type,
          message,
          timestamp: new Date(),
        },
        ...prev.slice(0, 99), // Keep last 100
      ]);
    },
    []
  );

  // ── WebSocket Handler ──────────────────────────────
  const handleWSMessage = useCallback(
    (event: WSEvent) => {
      switch (event.type) {
        case "new_superchat": {
          const chat = (event as unknown as { data: SuperChat }).data;

          setCurrentChat((curr) => {
            if (!curr) {
              // No current chat — make this the current one directly, don't add to queue
              setStats((s) => ({
                ...s,
                total_chats: s.total_chats + 1,
                total_revenue: s.total_revenue + chat.amount,
              }));
              addActivity(
                "new",
                `${chat.author_name} sent $${chat.amount.toFixed(2)} — "${chat.message.slice(0, 40)}..."`
              );
              return chat;
            }
            // There is already a current chat — add new one to queue (deduplicated)
            setQueue((prev) => {
              if (prev.some((c) => c.id === chat.id)) return prev; // already present
              const updated = [...prev, chat].sort(
                (a, b) => b.priority_score - a.priority_score
              );
              return updated;
            });
            setStats((prev) => ({
              ...prev,
              total_chats: prev.total_chats + 1,
              total_revenue: prev.total_revenue + chat.amount,
              queue_size: prev.queue_size + 1,
            }));
            addActivity(
              "new",
              `${chat.author_name} sent $${chat.amount.toFixed(2)} — "${chat.message.slice(0, 40)}..."`
            );
            return curr;
          });
          break;
        }

        case "chat_read": {
          const { chat_id, method } = event as unknown as {
            chat_id: string;
            method: string;
          };
          setCurrentChat((curr) =>
            curr?.id === chat_id ? null : curr
          );
          setStats((prev) => ({
            ...prev,
            chats_read: prev.chats_read + 1,
          }));
          addActivity(
            method === "voice" ? "voice" : "read",
            `Chat ${chat_id.slice(0, 8)}... marked as read (${method})`
          );
          break;
        }

        case "display_chat": {
          const chat = (event as unknown as { data: SuperChat }).data;
          setCurrentChat(chat);
          setQueue((prev) => prev.filter((c) => c.id !== chat.id));
          setStats((prev) => ({
            ...prev,
            queue_size: Math.max(0, prev.queue_size - 1),
          }));
          break;
        }

        case "chat_action": {
          const { chat_id, action } = event as unknown as {
            chat_id: string;
            action: string;
          };
          if (action === "skip") {
            setCurrentChat((curr) =>
              curr?.id === chat_id ? null : curr
            );
            setStats((prev) => ({
              ...prev,
              chats_skipped: prev.chats_skipped + 1,
            }));
            addActivity("skipped", `Chat ${chat_id.slice(0, 8)}... skipped`);
          }
          break;
        }

        default:
          break;
      }
    },
    [addActivity]
  );

  const { isConnected, connect, disconnect, send } =
    useWebSocket(handleWSMessage);

  // ── Voice Recognition ──────────────────────────────
  const handleVoiceTranscript = useCallback(
    (text: string) => {
      send({ type: "voice_transcript", text, timestamp: new Date().toISOString() });
      addActivity("voice", `Heard: "${text.slice(0, 50)}..."`);
    },
    [send, addActivity]
  );

  const { isListening, isSupported, startListening, stopListening } =
    useVoiceRecognition({ onTranscript: handleVoiceTranscript });

  // ── Sync current chat to backend ───────────────────
  // Whenever the displayed chat changes, tell the backend so voice matching works.
  useEffect(() => {
    if (isConnected && currentChat) {
      send({ type: "set_current", data: currentChat as unknown as Record<string, unknown> });
    }
  }, [currentChat, isConnected, send]);

  // ── Handlers ───────────────────────────────────────
  const handleStartStream = useCallback(async () => {
    try {
      await api.startStream({ streamer_name: "Streamer", demo_mode: true });
      setIsActive(true);
      connect();
      addActivity("new", "🎬 Stream session started (demo mode)");
    } catch (err) {
      console.error("Failed to start stream:", err);
      addActivity("flagged", "Failed to start stream session");
    }
  }, [connect, addActivity]);

  const handleStopStream = useCallback(async () => {
    try {
      await api.stopStream();
    } catch {
      /* ok */
    }
    setIsActive(false);
    disconnect();
    stopListening();
    setCurrentChat(null);
    setQueue([]);
    addActivity("skipped", "🏁 Stream session ended");
  }, [disconnect, stopListening, addActivity]);

  const handleChatAction = useCallback(
    async (chatId: string, action: ChatAction) => {
      try {
        await api.chatAction(chatId, action);

        if (action === "accept") {
          setCurrentChat((curr) => (curr?.id === chatId ? null : curr));
          setStats((prev) => ({
            ...prev,
            chats_read: prev.chats_read + 1,
          }));
          addActivity("read", `Accepted chat ${chatId.slice(0, 8)}...`);

          // Auto-advance
          const nextInQueue = queue[0];
          if (nextInQueue) {
            setCurrentChat(nextInQueue);
            setQueue((prev) => prev.slice(1));
            setStats((prev) => ({
              ...prev,
              queue_size: Math.max(0, prev.queue_size - 1),
            }));
          }
        } else if (action === "skip") {
          setCurrentChat((curr) => (curr?.id === chatId ? null : curr));
          setStats((prev) => ({
            ...prev,
            chats_skipped: prev.chats_skipped + 1,
          }));
          addActivity("skipped", `Skipped chat ${chatId.slice(0, 8)}...`);

          const nextInQueue = queue[0];
          if (nextInQueue) {
            setCurrentChat(nextInQueue);
            setQueue((prev) => prev.slice(1));
            setStats((prev) => ({
              ...prev,
              queue_size: Math.max(0, prev.queue_size - 1),
            }));
          }
        } else if (action === "pin") {
          addActivity("flagged", `Pinned chat ${chatId.slice(0, 8)}...`);
        }
      } catch (err) {
        console.error("Action failed:", err);
      }
    },
    [queue, addActivity]
  );

  const handleToggleVoice = useCallback(() => {
    if (isListening) {
      stopListening();
      addActivity("voice", "🎤 Voice recognition stopped");
    } else {
      startListening();
      addActivity("voice", "🎤 Voice recognition started");
    }
  }, [isListening, startListening, stopListening, addActivity]);

  // ── Render ─────────────────────────────────────────
  // ── Render ─────────────────────────────────────────
  if (!showDashboard) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[hsl(220,25%,6%)] text-white p-6 relative overflow-hidden select-none">
        {/* Animated Tech Background Grid & Glowing Orbs */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(56,189,248,0.06)_0%,transparent_70%)] pointer-events-none" />
        <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-[hsl(260,90%,60%,0.2)] rounded-full blur-[100px] pointer-events-none animate-float-glow-1" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[hsl(170,90%,50%,0.18)] rounded-full blur-[110px] pointer-events-none animate-float-glow-2" />
        <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-[hsl(330,90%,60%,0.15)] rounded-full blur-[90px] pointer-events-none animate-float-glow-1" />

        {/* Main Hero Card */}
        <div className="relative glass p-8 sm:p-12 md:p-14 rounded-3xl flex flex-col items-center text-center max-w-lg w-full shadow-[0_20px_80px_rgba(0,0,0,0.6)] border border-[hsl(220,20%,25%)] z-10 backdrop-blur-2xl transition-all duration-500 hover:border-[hsl(250,70%,60%,0.4)] hover:shadow-[0_25px_90px_rgba(168,85,247,0.25)]">
          
          {/* Top Pill Tag */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[hsl(250,80%,60%,0.12)] border border-[hsl(250,80%,60%,0.3)] text-xs font-semibold text-[hsl(250,90%,75%)] mb-7 tracking-wider uppercase shadow-inner">
            <span className="w-2 h-2 rounded-full bg-[hsl(168,85%,52%)] animate-pulse" />
            AI-Powered Stream Co-Pilot
          </div>

          {/* Glowing Animated Logo */}
          <div className="relative mb-7 group cursor-pointer" onClick={() => setShowDashboard(true)}>
            <div className="absolute -inset-2 rounded-3xl bg-gradient-to-r from-[hsl(168,85%,52%)] via-[hsl(280,80%,60%)] to-[hsl(330,85%,60%)] opacity-75 blur-md group-hover:opacity-100 transition duration-500 animate-pulse-ring" />
            <div className="relative w-24 h-24 sm:w-28 sm:h-28 rounded-2xl bg-[hsl(220,22%,12%)] border border-[hsl(220,15%,28%)] flex items-center justify-center text-5xl sm:text-6xl shadow-2xl transform group-hover:scale-105 group-hover:rotate-2 transition-all duration-300">
              🛡️
            </div>
          </div>

          {/* Title & Description */}
          <h1 className="text-4xl sm:text-5xl font-black tracking-tight mb-3 bg-gradient-to-r from-[hsl(168,90%,55%)] via-[hsl(270,90%,70%)] to-[hsl(330,90%,65%)] bg-clip-text text-transparent drop-shadow-sm">
            StreamGuard AI
          </h1>
          
          <p className="text-sm sm:text-base text-[hsl(220,12%,70%)] mb-8 max-w-sm font-normal leading-relaxed">
            Real-time voice moderation, super chat prioritization, and live stream analytics co-pilot.
          </p>

          {/* Feature Highlights */}
          <div className="grid grid-cols-3 gap-2.5 w-full mb-9">
            <div className="glass px-2.5 py-2 rounded-xl text-center border border-[hsl(220,12%,20%)] hover:border-[hsl(168,85%,52%,0.4)] transition-colors">
              <div className="text-base mb-0.5">🎙️</div>
              <div className="text-[11px] font-semibold text-[hsl(220,10%,80%)]">Voice Match</div>
            </div>
            <div className="glass px-2.5 py-2 rounded-xl text-center border border-[hsl(220,12%,20%)] hover:border-[hsl(280,80%,60%,0.4)] transition-colors">
              <div className="text-base mb-0.5">⚡</div>
              <div className="text-[11px] font-semibold text-[hsl(220,10%,80%)]">Smart Queue</div>
            </div>
            <div className="glass px-2.5 py-2 rounded-xl text-center border border-[hsl(220,12%,20%)] hover:border-[hsl(330,85%,60%,0.4)] transition-colors">
              <div className="text-base mb-0.5">📊</div>
              <div className="text-[11px] font-semibold text-[hsl(220,10%,80%)]">Analytics</div>
            </div>
          </div>

          {/* Dashboard Button */}
          <button
            onClick={() => setShowDashboard(true)}
            className="relative w-full py-4 px-8 rounded-2xl font-bold text-base bg-gradient-to-r from-[hsl(168,85%,48%)] via-[hsl(250,80%,60%)] to-[hsl(330,85%,60%)] text-white hover:shadow-[0_0_35px_rgba(168,85,247,0.5)] hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 flex items-center justify-center gap-3 cursor-pointer group overflow-hidden"
          >
            <span className="relative z-10 tracking-wide">Dashboard</span>
            <span className="relative z-10 text-lg group-hover:translate-x-1.5 transition-transform duration-300">→</span>
            {/* Shimmer sweep effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      <Header
        isActive={isActive}
        isConnected={isConnected}
        onStartStream={handleStartStream}
        onStopStream={handleStopStream}
        onToggleVoice={handleToggleVoice}
        isListening={isListening}
        voiceSupported={isSupported}
        onGoHome={() => setShowDashboard(false)}
      />

      <main className="flex-1 p-4 lg:p-6 overflow-hidden">
        {/* Stats Bar */}
        <div className="mb-5">
          <StatsPanel
            stats={stats}
            isConnected={isConnected}
            isListening={isListening}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-[calc(100vh-280px)]">
          {/* Left: Current Chat Focus */}
          <div className="lg:col-span-5 flex flex-col">
            <h2 className="text-sm font-semibold text-[hsl(220,10%,60%)] uppercase tracking-wider mb-3 px-1">
              🎯 Current Focus
            </h2>
            <div className="flex-1 glass rounded-xl p-4 flex items-center justify-center">
              {currentChat ? (
                <div className="w-full">
                  <SuperChatCard
                    chat={currentChat}
                    isCurrent={true}
                    onAction={handleChatAction}
                    showActions={true}
                  />
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-5xl mb-4">🛡️</div>
                  <p className="text-[hsl(220,10%,40%)] text-sm">
                    {isActive
                      ? "Waiting for super chats..."
                      : "Start a stream to begin"}
                  </p>
                  {!isActive && (
                    <button
                      onClick={handleStartStream}
                      className="mt-4 px-6 py-2.5 rounded-lg text-sm font-semibold gradient-primary text-white hover:opacity-90 transition-all shadow-lg cursor-pointer"
                    >
                      🚀 Start Demo Stream
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Middle: Queue */}
          <div className="lg:col-span-4 overflow-hidden">
            <ChatQueue
              queue={queue}
              currentChat={null}
              onAction={handleChatAction}
            />
          </div>

          {/* Right: Activity Feed */}
          <div className="lg:col-span-3 overflow-hidden">
            <ActivityFeed items={activity} />
          </div>
        </div>
      </main>
    </div>
  );
}
