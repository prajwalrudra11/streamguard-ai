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
