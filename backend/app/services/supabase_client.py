"""
StreamGuard AI - Supabase Client
Handles database connection and operations.
"""
from supabase import create_client, Client
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_supabase_client: Client = None


def get_supabase() -> Client:
    """Get or create the Supabase client singleton."""
    global _supabase_client
    
    if _supabase_client is None:
        settings = get_settings()
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_key,
        )
        logger.info("✅ Supabase client initialized")
    
    return _supabase_client


async def save_superchat(session_id: str, chat_data: dict) -> dict:
    """Save a processed super chat to the database."""
    client = get_supabase()
    
    record = {
        "session_id": session_id,
        "author_name": chat_data["author_name"],
        "author_channel_id": chat_data.get("author_channel_id"),
        "message": chat_data["message"],
        "amount": chat_data["amount"],
        "currency": chat_data.get("currency", "USD"),
        "sentiment": chat_data.get("sentiment"),
        "intent": chat_data.get("intent"),
        "priority_score": chat_data.get("priority_score", 50),
        "tier": chat_data.get("tier"),
        "risk_level": chat_data.get("risk_level", "low"),
        "is_safe": chat_data.get("is_safe", True),
        "moderation_flags": chat_data.get("moderation_flags", []),
        "suggested_reply": chat_data.get("suggested_reply"),
        "status": chat_data.get("status", "pending"),
    }
    
    result = client.table("super_chats").insert(record).execute()
    logger.debug(f"💾 Saved super chat from {chat_data['author_name']}")
    return result.data[0] if result.data else record


async def update_superchat_status(chat_id: str, status: str, read_at: str = None) -> dict:
    """Update super chat status (read, skipped, etc.)."""
    client = get_supabase()
    
    update_data = {"status": status}
    if read_at:
        update_data["read_at"] = read_at
    
    result = client.table("super_chats").update(update_data).eq("id", chat_id).execute()
    logger.debug(f"📝 Updated chat {chat_id} → {status}")
    return result.data[0] if result.data else {}


async def create_session(session_data: dict) -> dict:
    """Create a new stream session."""
    client = get_supabase()
    
    result = client.table("stream_sessions").insert(session_data).execute()
    logger.info(f"🎬 Created stream session: {result.data[0]['id'] if result.data else 'unknown'}")
    return result.data[0] if result.data else session_data


async def end_session(session_id: str, stats: dict) -> dict:
    """End a stream session and save final stats."""
    client = get_supabase()
    
    result = (
        client.table("stream_sessions")
        .update({
            "is_active": False,
            "ended_at": stats.get("ended_at"),
            "total_revenue": stats.get("total_revenue", 0),
            "total_chats": stats.get("total_chats", 0),
            "chats_read": stats.get("chats_read", 0),
            "chats_skipped": stats.get("chats_skipped", 0),
        })
        .eq("id", session_id)
        .execute()
    )
    logger.info(f"🏁 Ended stream session: {session_id}")
    return result.data[0] if result.data else {}


async def get_session_chats(session_id: str) -> list:
    """Get all super chats for a session."""
    client = get_supabase()
    
    result = (
        client.table("super_chats")
        .select("*")
        .eq("session_id", session_id)
        .order("received_at", desc=False)
        .execute()
    )
    return result.data or []


async def get_session(session_id: str) -> dict:
    """Get a stream session by ID."""
    client = get_supabase()
    
    result = (
        client.table("stream_sessions")
        .select("*")
        .eq("id", session_id)
        .single()
        .execute()
    )
    return result.data or {}
