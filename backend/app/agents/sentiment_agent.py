"""
StreamGuard AI - Sentiment Agent
Classifies emotional tone and intent of super chats.
"""
from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class SentimentAgent(BaseAgent):
    """Analyzes sentiment and intent of super chats."""
    
    def __init__(self):
        super().__init__("sentiment")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify sentiment and intent."""
        # LLM results injected by orchestrator's batch call
        llm_result = data.get("_llm_sentiment", {})
        
        sentiment = llm_result.get("sentiment", "neutral")
        intent = llm_result.get("intent", "other")
        
        # Validate enum values
        valid_sentiments = {"positive", "neutral", "negative"}
        valid_intents = {"question", "compliment", "request", "story", "greeting", "other"}
        
        if sentiment not in valid_sentiments:
            sentiment = "neutral"
        if intent not in valid_intents:
            intent = "other"
        
        return {
            "sentiment": sentiment,
            "intent": intent,
        }
    
    def _fallback(self, data, error):
        return {"sentiment": "neutral", "intent": "other"}
