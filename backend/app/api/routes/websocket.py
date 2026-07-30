"""
StreamGuard AI - WebSocket Routes
Real-time communication with streamer dashboard and overlay.
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.dependencies import get_ws_manager, get_queue, get_voice_matcher, get_session_manager
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication."""
    ws = get_ws_manager()
    await ws.connect(websocket)
    
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            event_type = data.get("type", "")
            
            if event_type != "ping":
                logger.info(f"📨 WS received: type='{event_type}'")
            
            if event_type == "voice_transcript":
                transcript_text = data.get("text", "")
                logger.info(f"\U0001f3a4 Voice transcript received: '{transcript_text[:80]}'")
                await _handle_voice(data, websocket)
            
            elif event_type == "set_current":
                # Frontend tells backend which chat is currently displayed
                await _handle_set_current(data)
            
            elif event_type == "chat_action":
                await _handle_action(data)
            
            elif event_type == "ping":
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        ws.disconnect(websocket)
        logger.info("🔌 Client disconnected")
    except Exception as e:
        ws.disconnect(websocket)
        logger.error(f"WebSocket error: {e}")


async def _handle_set_current(data: dict):
    """Frontend tells backend which chat is the current displayed one."""
    from app.models.schemas import SuperChatQueueItem
    chat_data = data.get("data")
    if not chat_data:
        return
    queue = get_queue()
    try:
        chat = SuperChatQueueItem(**chat_data)
        # Re-register in the internal lookup so mark_read works
        queue._chats[chat.id] = chat
        queue._current = chat
        logger.info(f"\U0001f4cc set_current: {chat.author_name} | '{chat.message[:50]}'")
    except Exception as e:
        logger.error(f"set_current failed: {e}")


async def _handle_voice(data: dict, ws_client: WebSocket):
    """Handle voice transcript from client."""
    transcript = data.get("text", "")
    if not transcript:
        return
    
    queue = get_queue()
    matcher = get_voice_matcher()
    ws = get_ws_manager()
    session_mgr = get_session_manager()
    
    current = await queue.get_current()
    if not current:
        logger.info("\U0001f3a4 Voice received but no current chat in backend queue — ignoring")
        return
    
    logger.info(f"\U0001f50d Matching transcript '{transcript[:60]}' against '{current.message[:60]}'")
    is_match, score = matcher.match(transcript, current.message)
    logger.info(f"\U0001f50d Match result: is_match={is_match}, score={score:.2f}, threshold={matcher.threshold:.2f}")
    
    if is_match:
        await queue.mark_read(current.id, method="voice")
        session_mgr.update_stats(read=True)
        
        # Notify all clients
        await ws.broadcast({
            "type": "chat_read",
            "chat_id": current.id,
            "method": "voice",
            "score": round(score, 2),
        })
        
        # Auto-advance to next
        next_chat = await queue.next()
        if next_chat:
            await ws.broadcast({
                "type": "display_chat",
                "data": next_chat.model_dump(mode="json"),
            })


async def _handle_action(data: dict):
    """Handle streamer action (accept/skip/pin)."""
    from app.models.schemas import ChatAction
    
    chat_id = data.get("chat_id", "")
    action = data.get("action", "")
    
    queue = get_queue()
    ws = get_ws_manager()
    session_mgr = get_session_manager()
    
    if action == "accept":
        await queue.mark_read(chat_id, method="manual")
        session_mgr.update_stats(read=True)
    elif action == "skip":
        await queue.skip(chat_id)
        session_mgr.update_stats(skipped=True)
    elif action == "pin":
        await queue.pin(chat_id)
    
    await ws.broadcast({
        "type": "chat_action",
        "chat_id": chat_id,
        "action": action,
    })
