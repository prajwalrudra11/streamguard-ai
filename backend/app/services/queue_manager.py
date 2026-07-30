"""
StreamGuard AI - Intelligent Priority Queue
Manages super chat ordering based on AI analysis.
"""
import asyncio
import heapq
from typing import Optional, List, Dict
from datetime import datetime
from app.models.schemas import SuperChatQueueItem, ChatStatus, Tier
from app.core.logging import get_logger
from app.core.exceptions import QueueFullError

logger = get_logger(__name__)


class PriorityQueueItem:
    """Wrapper for heap queue ordering.
    
    Lower values = higher priority in heapq.
    We negate priority_score so higher scores come first.
    """
    def __init__(self, chat: SuperChatQueueItem, position: int):
        self.chat = chat
        self.position = position  # Insertion order for tie-breaking
    
    def __lt__(self, other):
        # Higher priority_score = should come first (negate for min-heap)
        if self.chat.priority_score != other.chat.priority_score:
            return self.chat.priority_score > other.chat.priority_score
        # Tie-break by insertion order (earlier = first)
        return self.position < other.position


class QueueManager:
    """Manages the intelligent super chat priority queue."""
    
    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self._heap: List[PriorityQueueItem] = []
        self._counter = 0  # Monotonic counter for tie-breaking
        self._chats: Dict[str, SuperChatQueueItem] = {}  # id → chat lookup
        self._current: Optional[SuperChatQueueItem] = None  # Currently displayed
        self._pinned: List[SuperChatQueueItem] = []
        self._lock = asyncio.Lock()
        
        # Stats
        self.total_added = 0
        self.total_read = 0
        self.total_skipped = 0
    
    async def add(self, chat: SuperChatQueueItem) -> None:
        """Add a processed super chat to the priority queue."""
        async with self._lock:
            if len(self._heap) >= self.max_size:
                raise QueueFullError(self.max_size)
            
            self._counter += 1
            item = PriorityQueueItem(chat, self._counter)
            heapq.heappush(self._heap, item)
            self._chats[chat.id] = chat
            self.total_added += 1
            
            logger.info(
                f"📥 Queued: {chat.author_name} | "
                f"${chat.amount} | Priority: {chat.priority_score} | "
                f"Queue size: {len(self._heap)}"
            )
    
    async def next(self) -> Optional[SuperChatQueueItem]:
        """Get the next highest-priority super chat."""
        async with self._lock:
            while self._heap:
                item = heapq.heappop(self._heap)
                chat = item.chat
                
                # Skip if already processed
                if chat.id not in self._chats:
                    continue
                
                chat.status = ChatStatus.DISPLAYED
                self._current = chat
                
                logger.info(
                    f"📤 Displaying: {chat.author_name} | "
                    f"${chat.amount} | {chat.sentiment.value}"
                )
                return chat
            
            return None
    
    async def mark_read(self, chat_id: str, method: str = "manual") -> bool:
        """Mark a super chat as read/acknowledged."""
        async with self._lock:
            if chat_id in self._chats:
                self._chats[chat_id].status = ChatStatus.READ
                del self._chats[chat_id]
                self.total_read += 1
                
                if self._current and self._current.id == chat_id:
                    self._current = None
                
                logger.info(f"✅ Read ({method}): {chat_id}")
                return True
            return False
    
    async def skip(self, chat_id: str) -> bool:
        """Skip a super chat."""
        async with self._lock:
            if chat_id in self._chats:
                self._chats[chat_id].status = ChatStatus.SKIPPED
                del self._chats[chat_id]
                self.total_skipped += 1
                
                if self._current and self._current.id == chat_id:
                    self._current = None
                
                logger.info(f"⏭️ Skipped: {chat_id}")
                return True
            return False
    
    async def pin(self, chat_id: str) -> bool:
        """Pin a super chat for later."""
        async with self._lock:
            if chat_id in self._chats:
                chat = self._chats[chat_id]
                chat.status = ChatStatus.PINNED
                self._pinned.append(chat)
                
                logger.info(f"📌 Pinned: {chat_id}")
                return True
            return False
    
    async def get_current(self) -> Optional[SuperChatQueueItem]:
        """Get the currently displayed super chat."""
        return self._current
    
    async def get_queue(self, limit: int = 20) -> List[SuperChatQueueItem]:
        """Get a preview of upcoming super chats."""
        async with self._lock:
            # Sort by priority for display
            sorted_items = sorted(self._heap)
            return [item.chat for item in sorted_items[:limit]]
    
    async def get_pinned(self) -> List[SuperChatQueueItem]:
        """Get all pinned super chats."""
        return self._pinned.copy()
    
    @property
    def size(self) -> int:
        return len(self._heap)
    
    @property
    def stats(self) -> dict:
        return {
            "queue_size": self.size,
            "total_added": self.total_added,
            "total_read": self.total_read,
            "total_skipped": self.total_skipped,
            "pinned_count": len(self._pinned),
            "has_current": self._current is not None,
        }
