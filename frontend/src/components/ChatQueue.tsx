/* ── StreamGuard AI - Chat Queue Component ─────────── */
"use client";

import type { SuperChat, ChatAction } from "@/types";
import SuperChatCard from "./SuperChatCard";

interface ChatQueueProps {
  queue: SuperChat[];
  currentChat: SuperChat | null;
  onAction: (chatId: string, action: ChatAction) => void;
}

export default function ChatQueue({ queue, currentChat, onAction }: ChatQueueProps) {
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 px-1">
        <h2 className="text-sm font-semibold text-[hsl(220,10%,60%)] uppercase tracking-wider">
          Chat Queue
        </h2>
        <span className="text-xs px-2 py-0.5 rounded-full bg-[hsl(168,85%,52%,0.15)] text-[hsl(168,85%,52%)]">
          {queue.length} pending
        </span>
      </div>

      {/* Current Chat Highlight */}
      {currentChat && (
        <div className="mb-3">
          <div className="text-xs text-[hsl(168,85%,52%)] font-medium mb-1.5 px-1 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[hsl(168,85%,52%)] animate-pulse" />
            NOW DISPLAYING
          </div>
          <SuperChatCard
            chat={currentChat}
            isCurrent={true}
            onAction={onAction}
            showActions={true}
          />
        </div>
      )}

      {/* Queue List */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {queue.length === 0 && !currentChat ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="text-4xl mb-3">📭</div>
            <p className="text-sm text-[hsl(220,10%,40%)]">
              No super chats in queue
            </p>
            <p className="text-xs text-[hsl(220,10%,30%)] mt-1">
              Start a stream session to begin receiving chats
            </p>
          </div>
        ) : (
          queue
            .filter((chat) => chat.id !== currentChat?.id) // guard against duplicates
            .map((chat, index) => (
            <div
              key={chat.id}
              style={{ animationDelay: `${index * 60}ms` }}
              className="animate-slide-in-up"
            >
              <SuperChatCard
                chat={chat}
                onAction={onAction}
                showActions={false}
              />
            </div>
          ))
        )}
      </div>
    </div>
  );
}
