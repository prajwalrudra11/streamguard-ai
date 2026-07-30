"""
StreamGuard AI - Moderation Agent
Detects spam, toxicity, and inappropriate content.
"""
import re
from typing import Any, Dict, List
from app.agents.base_agent import BaseAgent


class ModerationAgent(BaseAgent):
    """Filters spam, toxic, and inappropriate super chats."""
    
    def __init__(self):
        super().__init__("moderation")
        
        # Quick regex pre-filters (before hitting the LLM)
        self._spam_patterns = [
            re.compile(r"https?://\S+", re.IGNORECASE),          # Links
            re.compile(r"(.)\1{5,}"),                             # Repeated chars: "aaaaaa"
            re.compile(r"free\s+(v-?bucks|robux|money)", re.I),   # Common scams
            re.compile(r"(subscribe|follow)\s+my\s+channel", re.I),
        ]
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a super chat for safety."""
        message = data.get("message", "")
        
        flags: List[str] = []
        risk_level = "low"
        
        # Step 1: Regex pre-filter
        for pattern in self._spam_patterns:
            if pattern.search(message):
                flags.append("spam")
                risk_level = "medium"
                break
        
        # Step 2: LLM analysis (will be populated by orchestrator's batch call)
        llm_result = data.get("_llm_moderation", {})
        if llm_result:
            if llm_result.get("is_toxic"):
                flags.append("toxic")
                risk_level = "high"
            if llm_result.get("is_nsfw"):
                flags.append("nsfw")
                risk_level = "high"
            if llm_result.get("is_spam") and "spam" not in flags:
                flags.append("spam")
                risk_level = max(risk_level, "medium")
        
        is_safe = risk_level != "high"
        
        return {
            "is_safe": is_safe,
            "risk_level": risk_level,
            "moderation_flags": flags,
        }
    
    def _fallback(self, data, error):
        """If moderation fails, default to safe (don't block paying users)."""
        self.logger.warning(f"Moderation fallback triggered: {error}")
        return {
            "is_safe": True,
            "risk_level": "low",
            "moderation_flags": [],
        }
