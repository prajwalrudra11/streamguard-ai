"""
StreamGuard AI - Session Manager
Manages stream session state and demo mode.
"""
import asyncio
import random
import uuid
from datetime import datetime
from typing import Optional, Callable, Awaitable
from app.models.schemas import (
    StreamSessionCreate, StreamSessionResponse, SuperChatCreate,
    SuperChatQueueItem, ChatStatus, Tier, Sentiment, Intent, RiskLevel,
)
from app.services import supabase_client as db
from app.core.logging import get_logger
from app.core.exceptions import NoActiveSessionError

logger = get_logger(__name__)

# Demo super chat templates
DEMO_CHATS = [
    {"author": "GamingFanatic42", "message": "Love your content! Keep it up! 🔥", "amount": 5.0},
    {"author": "TechNerd_99", "message": "Can you explain your PC setup? What GPU are you using?", "amount": 10.0},
    {"author": "SarahPlays", "message": "First time catching you live! Been watching for 2 years!", "amount": 20.0},
    {"author": "xXDarkLord420Xx", "message": "FREE V-BUCKS AT TOTALLYLEGIT.COM", "amount": 1.0},
    {"author": "CoolDude_Mike", "message": "What game are you playing next week?", "amount": 2.0},
    {"author": "DiamondDonator", "message": "You deserve this! Best streamer on the platform! 💎", "amount": 100.0},
    {"author": "QuietViewer", "message": "Hi from Japan! 🇯🇵", "amount": 5.0},
    {"author": "ProGamer_Elite", "message": "Your aim is insane! Can you do a tips video?", "amount": 15.0},
    {"author": "MusicLover_22", "message": "Can you play some lo-fi in the background?", "amount": 3.0},
    {"author": "OG_Subscriber", "message": "Been here since day 1. So proud of your growth! 😭", "amount": 50.0},
    {"author": "RandomTroll", "message": "lol lol lol lol lol lol lol", "amount": 1.0},
    {"author": "ArtistKate", "message": "I drew fan art of you! Check my channel!", "amount": 8.0},
    {"author": "NewFollower_2026", "message": "Just subscribed! What did I miss?", "amount": 2.0},
    {"author": "BigSpender_VIP", "message": "Shout out my birthday please! It's today! 🎂", "amount": 75.0},
    {"author": "ChillVibes", "message": "This stream is so relaxing after a long day at work", "amount": 5.0},
]


class SessionManager:
    """Manages stream sessions and demo mode simulation."""
    
    def __init__(self):
        self.active_session: Optional[dict] = None
        self._demo_task: Optional[asyncio.Task] = None
        self._on_new_chat: Optional[Callable[[SuperChatCreate], Awaitable[None]]] = None
    
    def set_chat_callback(self, callback: Callable[[SuperChatCreate], Awaitable[None]]):
        """Set the callback for when new chats arrive (demo or real)."""
        self._on_new_chat = callback
    
    async def start_session(self, config: StreamSessionCreate) -> dict:
        """Start a new stream session."""
        if self.active_session:
            await self.end_session()
        
        session_data = {
            "streamer_name": config.streamer_name,
            "youtube_video_id": config.youtube_video_id,
            "demo_mode": config.demo_mode,
            "is_active": True,
            "started_at": datetime.utcnow().isoformat(),
            "total_revenue": 0.0,
            "total_chats": 0,
            "chats_read": 0,
            "chats_skipped": 0,
        }
        
        saved = await db.create_session(session_data)
        self.active_session = saved
        
        if config.demo_mode:
            self._start_demo_mode()
        
        logger.info(f"🎬 Session started: {saved.get('id', 'local')} (demo={config.demo_mode})")
        return saved
    
    async def end_session(self) -> Optional[dict]:
        """End the current stream session."""
        if not self.active_session:
            return None
        
        self._stop_demo_mode()
        
        stats = {
            "ended_at": datetime.utcnow().isoformat(),
            "total_revenue": self.active_session.get("total_revenue", 0),
            "total_chats": self.active_session.get("total_chats", 0),
            "chats_read": self.active_session.get("chats_read", 0),
            "chats_skipped": self.active_session.get("chats_skipped", 0),
        }
        
        session_id = self.active_session.get("id")
        if session_id:
            await db.end_session(session_id, stats)
        
        result = {**self.active_session, **stats, "is_active": False}
        self.active_session = None
        logger.info("🏁 Session ended")
        return result
    
    def get_session(self) -> Optional[dict]:
        return self.active_session
    
    def update_stats(self, revenue: float = 0, read: bool = False, skipped: bool = False):
        """Update live session statistics."""
        if not self.active_session:
            return
        self.active_session["total_revenue"] = self.active_session.get("total_revenue", 0) + revenue
        self.active_session["total_chats"] = self.active_session.get("total_chats", 0) + 1
        if read:
            self.active_session["chats_read"] = self.active_session.get("chats_read", 0) + 1
        if skipped:
            self.active_session["chats_skipped"] = self.active_session.get("chats_skipped", 0) + 1
    
    # ── Demo Mode ────────────────────────────────────────
    
    def _start_demo_mode(self):
        self._demo_task = asyncio.create_task(self._demo_loop())
        logger.info("🎮 Demo mode started")
    
    def _stop_demo_mode(self):
        if self._demo_task and not self._demo_task.done():
            self._demo_task.cancel()
            logger.info("🎮 Demo mode stopped")
    
    async def _demo_loop(self):
        """Generate simulated super chats at intervals."""
        try:
            await asyncio.sleep(2)  # Initial delay
            while True:
                template = random.choice(DEMO_CHATS)
                chat = SuperChatCreate(
                    author_name=template["author"],
                    message=template["message"],
                    amount=template["amount"],
                    currency="USD",
                    session_id=self.active_session.get("id") if self.active_session else None,
                )
                
                if self._on_new_chat:
                    await self._on_new_chat(chat)
                
                interval = random.uniform(4.0, 10.0)
                await asyncio.sleep(interval)
                
        except asyncio.CancelledError:
            logger.debug("Demo loop cancelled")
