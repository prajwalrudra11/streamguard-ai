/* ── StreamGuard AI - API Client ───────────────────── */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API request failed");
  }
  return res.json();
}

export const api = {
  // Stream session
  startStream: (data: { streamer_name: string; demo_mode: boolean }) =>
    request("/api/stream/start", { method: "POST", body: JSON.stringify(data) }),

  stopStream: () =>
    request("/api/stream/stop", { method: "POST" }),

  getStreamStatus: () =>
    request<{ is_active: boolean; session: unknown }>("/api/stream/status"),

  // Super chats
  sendSuperChat: (data: {
    author_name: string;
    message: string;
    amount: number;
    currency?: string;
  }) => request("/api/superchat/send", { method: "POST", body: JSON.stringify(data) }),

  chatAction: (chatId: string, action: "accept" | "skip" | "pin") =>
    request(`/api/superchat/action/${chatId}?action=${action}`, { method: "POST" }),

  getQueue: () =>
    request<{ current: unknown; queue: unknown[]; stats: unknown }>("/api/superchat/queue"),

  nextChat: () =>
    request("/api/superchat/next", { method: "GET" }),

  // Health
  health: () => request<{ status: string }>("/health"),
};
