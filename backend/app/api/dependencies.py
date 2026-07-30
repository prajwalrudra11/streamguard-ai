"""
StreamGuard AI - Dependency Injection
Singleton services shared across the application.
"""
from typing import List
from fastapi import WebSocket
import json
from app.services.queue_manager import QueueManager
from app.services.voice_matcher import VoiceMatcher
from app.services.session_manager import SessionManager
from app.agents.orchestrator import Orchestrator
from app.core.logging import get_logger

logger = get_logger(__name__)


# ── WebSocket Connection Manager ─────────────────────────

class WSConnectionManager:
    """Manages active WebSocket connections."""
    
    def __init__(self):
        self.connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        logger.info(f"🔌 Client connected. Total: {len(self.connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)
        logger.info(f"🔌 Client disconnected. Total: {len(self.connections)}")
    
    async def broadcast(self, data: dict):
        """Send data to all connected clients."""
        disconnected = []
        for ws in self.connections:
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(ws)
        
        for ws in disconnected:
            self.disconnect(ws)
    
    async def send_to(self, websocket: WebSocket, data: dict):
        """Send data to a specific client."""
        try:
            await ws.send_json(data)
        except Exception:
            self.disconnect(websocket)


# ── Singleton Instances ──────────────────────────────────

_queue: QueueManager = None
_voice_matcher: VoiceMatcher = None
_session_manager: SessionManager = None
_orchestrator: Orchestrator = None
_ws_manager: WSConnectionManager = None


def get_queue() -> QueueManager:
    global _queue
    if _queue is None:
        from app.config import get_settings
        _queue = QueueManager(max_size=get_settings().max_queue_size)
    return _queue


def get_voice_matcher() -> VoiceMatcher:
    global _voice_matcher
    if _voice_matcher is None:
        from app.config import get_settings
        settings = get_settings()
        _voice_matcher = VoiceMatcher(
            threshold=settings.voice_match_threshold,
            cooldown_seconds=settings.voice_cooldown_seconds,
        )
    return _voice_matcher


def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


def get_ws_manager() -> WSConnectionManager:
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WSConnectionManager()
    return _ws_manager


def init_services():
    """Initialize all services and wire callbacks."""
    queue = get_queue()
    orchestrator = get_orchestrator()
    session_mgr = get_session_manager()
    ws = get_ws_manager()
    
    # Wire demo mode: when a simulated chat arrives, analyze + queue + broadcast
    async def on_new_chat(chat):
        queue_item = await orchestrator.analyze(chat)
        await queue.add(queue_item)
        session_mgr.update_stats(revenue=chat.amount)
        await ws.broadcast({
            "type": "new_superchat",
            "data": queue_item.model_dump(mode="json"),
        })
    
    session_mgr.set_chat_callback(on_new_chat)
    logger.info("✅ All services initialized and wired")
