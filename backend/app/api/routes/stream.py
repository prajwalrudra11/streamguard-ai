"""
StreamGuard AI - Stream Session Routes
Endpoints for managing stream sessions.
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import StreamSessionCreate, StreamSessionResponse
from app.api.dependencies import get_session_manager

router = APIRouter(prefix="/stream", tags=["Stream Session"])


@router.post("/start", response_model=dict)
async def start_stream(config: StreamSessionCreate):
    """Start a new stream session (with optional demo mode)."""
    session_mgr = get_session_manager()
    session = await session_mgr.start_session(config)
    return {
        "status": "started",
        "session": session,
        "message": f"Stream session started {'(demo mode)' if config.demo_mode else ''}"
    }


@router.post("/stop")
async def stop_stream():
    """End the current stream session."""
    session_mgr = get_session_manager()
    result = await session_mgr.end_session()
    if not result:
        raise HTTPException(status_code=404, detail="No active session to stop")
    return {"status": "stopped", "session": result}


@router.get("/status")
async def stream_status():
    """Get current stream session status."""
    session_mgr = get_session_manager()
    session = session_mgr.get_session()
    if not session:
        return {"is_active": False, "session": None}
    return {"is_active": True, "session": session}
