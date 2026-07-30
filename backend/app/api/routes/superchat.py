"""
StreamGuard AI - Super Chat Routes
REST endpoints for super chat management.
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import SuperChatCreate, ChatAction
from app.api.dependencies import get_orchestrator, get_queue, get_session_manager, get_ws_manager

router = APIRouter(prefix="/superchat", tags=["Super Chat"])


@router.post("/send")
async def send_superchat(chat: SuperChatCreate):
    """Manually send a super chat (for testing / demo)."""
    session_mgr = get_session_manager()
    if not session_mgr.get_session():
        raise HTTPException(status_code=400, detail="No active stream session")
    
    orchestrator = get_orchestrator()
    queue = get_queue()
    ws = get_ws_manager()
    
    # Analyze with AI agents
    queue_item = await orchestrator.analyze(chat)
    
    # Add to priority queue
    await queue.add(queue_item)
    
    # Update stats
    session_mgr.update_stats(revenue=chat.amount)
    
    # Broadcast to connected clients
    await ws.broadcast({
        "type": "new_superchat",
        "data": queue_item.model_dump(mode="json"),
    })
    
    return {"status": "queued", "chat": queue_item.model_dump(mode="json")}


@router.post("/action/{chat_id}")
async def chat_action(chat_id: str, action: ChatAction):
    """Accept, skip, or pin a super chat."""
    queue = get_queue()
    ws = get_ws_manager()
    session_mgr = get_session_manager()
    
    success = False
    if action == ChatAction.ACCEPT:
        success = await queue.mark_read(chat_id, method="manual")
        session_mgr.update_stats(read=True)
    elif action == ChatAction.SKIP:
        success = await queue.skip(chat_id)
        session_mgr.update_stats(skipped=True)
    elif action == ChatAction.PIN:
        success = await queue.pin(chat_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found in queue")
    
    # Broadcast action to all clients
    await ws.broadcast({
        "type": "chat_action",
        "chat_id": chat_id,
        "action": action.value,
    })
    
    return {"status": "ok", "action": action.value, "chat_id": chat_id}


@router.get("/queue")
async def get_queue_state():
    """Get current super chat queue."""
    queue = get_queue()
    items = await queue.get_queue(limit=30)
    current = await queue.get_current()
    
    return {
        "current": current.model_dump(mode="json") if current else None,
        "queue": [item.model_dump(mode="json") for item in items],
        "stats": queue.stats,
    }


@router.get("/next")
async def next_superchat():
    """Advance to the next super chat in queue."""
    queue = get_queue()
    ws = get_ws_manager()
    
    next_chat = await queue.next()
    if not next_chat:
        return {"status": "empty", "chat": None}
    
    # Broadcast to overlay
    await ws.broadcast({
        "type": "display_chat",
        "data": next_chat.model_dump(mode="json"),
    })
    
    return {"status": "ok", "chat": next_chat.model_dump(mode="json")}
