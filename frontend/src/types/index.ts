/* ── StreamGuard AI - TypeScript Types ─────────────── */

export type ChatStatus = "pending" | "queued" | "displayed" | "read" | "skipped" | "pinned";
export type Sentiment = "positive" | "neutral" | "negative";
export type Intent = "question" | "compliment" | "request" | "story" | "greeting" | "other";
export type RiskLevel = "low" | "medium" | "high";
export type Tier = "bronze" | "silver" | "gold" | "diamond";
export type ChatAction = "accept" | "skip" | "pin";

export interface SuperChat {
  id: string;
  author_name: string;
  message: string;
  amount: number;
  currency: string;
  priority_score: number;
  tier: Tier;
  sentiment: Sentiment;
  intent: Intent;
  risk_level: RiskLevel;
  suggested_reply: string | null;
  status: ChatStatus;
  received_at: string;
}

export interface StreamSession {
  id: string;
  youtube_video_id: string | null;
  streamer_name: string;
  demo_mode: boolean;
  is_active: boolean;
  started_at: string;
  ended_at: string | null;
  total_revenue: number;
  total_chats: number;
  chats_read: number;
  chats_skipped: number;
}

export interface StreamStats {
  total_revenue: number;
  total_chats: number;
  chats_read: number;
  chats_skipped: number;
  queue_size: number;
}

export interface WSEvent {
  type: string;
  [key: string]: unknown;
}

export interface WSNewSuperChat extends WSEvent {
  type: "new_superchat";
  data: SuperChat;
}

export interface WSChatRead extends WSEvent {
  type: "chat_read";
  chat_id: string;
  method: "voice" | "manual";
  score?: number;
}

export interface WSDisplayChat extends WSEvent {
  type: "display_chat";
  data: SuperChat;
}

export interface WSChatActionEvent extends WSEvent {
  type: "chat_action";
  chat_id: string;
  action: ChatAction;
}
