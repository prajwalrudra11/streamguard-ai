"""
StreamGuard AI - Pydantic Schemas
Request/Response models for the API layer.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ── Enums ────────────────────────────────────────────────

class ChatStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    DISPLAYED = "displayed"
    READ = "read"
    SKIPPED = "skipped"
    PINNED = "pinned"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Intent(str, Enum):
    QUESTION = "question"
    COMPLIMENT = "compliment"
    REQUEST = "request"
    STORY = "story"
    GREETING = "greeting"
    OTHER = "other"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Tier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"


class ChatAction(str, Enum):
    ACCEPT = "accept"
    SKIP = "skip"
    PIN = "pin"


# ── Super Chat Schemas ───────────────────────────────────

class SuperChatBase(BaseModel):
    """Base super chat fields."""
    author_name: str = Field(..., description="Display name of the sender")
    author_channel_id: Optional[str] = Field(None, description="YouTube channel ID")
    message: str = Field(..., description="Super chat message text")
    amount: float = Field(..., ge=0, description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")


class SuperChatCreate(SuperChatBase):
    """Schema for creating a new super chat (demo mode / YouTube ingestion)."""
    session_id: Optional[str] = Field(None, description="Stream session ID")


class SuperChatAnalysis(BaseModel):
    """AI analysis results attached to a super chat."""
    # Moderation
    is_safe: bool = True
    risk_level: RiskLevel = RiskLevel.LOW
    moderation_flags: List[str] = Field(default_factory=list)
    
    # Sentiment
    sentiment: Sentiment = Sentiment.NEUTRAL
    intent: Intent = Intent.OTHER
    
    # Revenue
    priority_score: int = Field(default=50, ge=1, le=100)
    tier: Tier = Tier.BRONZE
    is_repeat_supporter: bool = False
    is_first_time: bool = False
    
    # Response
    suggested_reply: Optional[str] = None
    reply_tone: Optional[str] = None


class SuperChatResponse(SuperChatBase):
    """Full super chat response with analysis."""
    id: str
    session_id: str
    status: ChatStatus = ChatStatus.PENDING
    analysis: Optional[SuperChatAnalysis] = None
    received_at: datetime
    read_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class SuperChatQueueItem(BaseModel):
    """Super chat as displayed in the queue."""
    id: str
    author_name: str
    message: str
    amount: float
    currency: str
    priority_score: int
    tier: Tier
    sentiment: Sentiment
    intent: Intent
    risk_level: RiskLevel
    suggested_reply: Optional[str] = None
    status: ChatStatus
    received_at: datetime


# ── Stream Session Schemas ───────────────────────────────

class StreamSessionCreate(BaseModel):
    """Schema for starting a new stream session."""
    youtube_video_id: Optional[str] = Field(None, description="YouTube live video ID")
    streamer_name: str = Field(default="Streamer", description="Streamer display name")
    demo_mode: bool = Field(default=True, description="Enable demo mode with simulated chats")


class StreamSessionResponse(BaseModel):
    """Stream session details."""
    id: str
    youtube_video_id: Optional[str] = None
    streamer_name: str
    demo_mode: bool
    is_active: bool
    started_at: datetime
    ended_at: Optional[datetime] = None
    total_revenue: float = 0.0
    total_chats: int = 0
    chats_read: int = 0
    chats_skipped: int = 0
    
    model_config = {"from_attributes": True}


# ── WebSocket Event Schemas ──────────────────────────────

class WSEvent(BaseModel):
    """Base WebSocket event."""
    type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WSNewSuperChat(WSEvent):
    """New super chat event sent to clients."""
    type: str = "new_superchat"
    data: SuperChatQueueItem


class WSChatRead(WSEvent):
    """Chat was read/acknowledged."""
    type: str = "chat_read"
    chat_id: str
    method: str = "manual"  # "manual" | "voice"


class WSChatAction(WSEvent):
    """Client action on a chat."""
    type: str = "chat_action"
    chat_id: str
    action: ChatAction


class WSVoiceTranscript(WSEvent):
    """Voice transcript from client."""
    type: str = "voice_transcript"
    text: str


class WSQueueUpdate(WSEvent):
    """Updated queue state."""
    type: str = "queue_update"
    queue: List[SuperChatQueueItem]
    total_pending: int


class WSStreamStats(WSEvent):
    """Live stream statistics."""
    type: str = "stream_stats"
    total_revenue: float
    total_chats: int
    chats_read: int
    chats_skipped: int
    avg_response_time: Optional[float] = None


# ── Settings Schemas ─────────────────────────────────────

class StreamerSettings(BaseModel):
    """Streamer preference settings."""
    voice_match_threshold: float = Field(default=0.70, ge=0.0, le=1.0)
    voice_cooldown_seconds: int = Field(default=5, ge=1, le=30)
    moderation_strict_mode: bool = False
    auto_advance_on_voice: bool = True
    min_amount_for_priority: float = Field(default=5.0, ge=0)
    ai_reply_tone: str = Field(default="casual", description="casual | grateful | funny | professional")
    max_display_time_seconds: int = Field(default=30, ge=5, le=120)


# ── Demo Mode Schemas ────────────────────────────────────

class DemoConfig(BaseModel):
    """Configuration for demo mode simulated chats."""
    interval_seconds: float = Field(default=5.0, ge=1.0, le=60.0, description="Seconds between simulated chats")
    include_spam: bool = Field(default=True, description="Include occasional spam for demo")
    max_amount: float = Field(default=100.0, ge=1.0)
    min_amount: float = Field(default=1.0, ge=0.5)
