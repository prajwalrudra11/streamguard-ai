"""
StreamGuard AI - Response Agent
Generates suggested replies for the streamer.
"""
from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class ResponseAgent(BaseAgent):
    """Generates contextual reply suggestions for super chats."""
    
    def __init__(self):
        super().__init__("response")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a suggested reply."""
        # LLM result injected by orchestrator's batch call
        llm_result = data.get("_llm_response", {})
        
        suggested_reply = llm_result.get("suggested_reply", "")
        reply_tone = llm_result.get("reply_tone", "casual")
        
        # Validate tone
        valid_tones = {"casual", "grateful", "funny", "professional"}
        if reply_tone not in valid_tones:
            reply_tone = "casual"
        
        return {
            "suggested_reply": suggested_reply,
            "reply_tone": reply_tone,
        }
    
    def _fallback(self, data, error):
        author = data.get("author_name", "friend")
        amount = data.get("amount", 0)
        return {
            "suggested_reply": f"Thanks for the ${amount:.0f}, {author}! 🙏",
            "reply_tone": "grateful",
        }
