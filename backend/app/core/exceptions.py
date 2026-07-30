"""
StreamGuard AI - Custom Exception Hierarchy
"""
from fastapi import HTTPException, status


class StreamGuardError(Exception):
    """Base exception for StreamGuard AI."""
    def __init__(self, message: str = "An internal error occurred"):
        self.message = message
        super().__init__(self.message)


class AgentError(StreamGuardError):
    """Raised when an AI agent fails to process."""
    def __init__(self, agent_name: str, message: str):
        self.agent_name = agent_name
        super().__init__(f"[{agent_name}] {message}")


class QueueError(StreamGuardError):
    """Raised when the super chat queue encounters an issue."""
    pass


class QueueFullError(QueueError):
    """Raised when the queue reaches maximum capacity."""
    def __init__(self, max_size: int):
        super().__init__(f"Queue is full (max capacity: {max_size})")


class SessionError(StreamGuardError):
    """Raised for stream session related errors."""
    pass


class NoActiveSessionError(SessionError):
    """Raised when an operation requires an active stream session."""
    def __init__(self):
        super().__init__("No active stream session found")


class VoiceMatchError(StreamGuardError):
    """Raised when voice matching encounters an issue."""
    pass


class YouTubeAPIError(StreamGuardError):
    """Raised when YouTube API calls fail."""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(f"YouTube API Error: {message}")


class DatabaseError(StreamGuardError):
    """Raised when database operations fail."""
    pass


# ── HTTP Exception Helpers ──────────────────────────────

def not_found(detail: str = "Resource not found") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def bad_request(detail: str = "Bad request") -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def server_error(detail: str = "Internal server error") -> HTTPException:
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
