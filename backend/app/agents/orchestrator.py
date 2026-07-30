"""
StreamGuard AI - Agent Orchestrator
Coordinates all AI agents with a single optimized Gemini call.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any
from google import genai
from app.config import get_settings
from app.agents.moderation_agent import ModerationAgent
from app.agents.sentiment_agent import SentimentAgent
from app.agents.revenue_agent import RevenueAgent
from app.agents.response_agent import ResponseAgent
from app.models.schemas import (
    SuperChatCreate, SuperChatQueueItem, ChatStatus,
    Tier, Sentiment, Intent, RiskLevel,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# Structured prompt for batch analysis
ANALYSIS_PROMPT = """You are StreamGuard AI, analyzing a live stream super chat.

Super Chat Details:
- Author: {author_name}
- Message: "{message}"
- Amount: ${amount} {currency}

Analyze this super chat and respond with ONLY valid JSON (no markdown, no code blocks):

{{
  "moderation": {{
    "is_toxic": false,
    "is_nsfw": false,
    "is_spam": false
  }},
  "sentiment": {{
    "sentiment": "positive|neutral|negative",
    "intent": "question|compliment|request|story|greeting|other"
  }},
  "response": {{
    "suggested_reply": "A short 1-2 sentence reply the streamer could say",
    "reply_tone": "casual|grateful|funny"
  }}
}}

Rules:
- Be accurate with moderation. Only flag truly toxic/spam content.
- Detect questions accurately (they need answers).
- Keep suggested replies short, natural, and matching the tone.
- For high-value donations ($20+), make the reply extra appreciative.
"""


class Orchestrator:
    """Coordinates all AI agents in an optimized pipeline."""
    
    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = "gemini-2.0-flash"
        
        # Initialize agents
        self.moderation = ModerationAgent()
        self.sentiment = SentimentAgent()
        self.revenue = RevenueAgent()
        self.response = ResponseAgent()
        
        logger.info("🤖 Orchestrator initialized with all agents")
    
    async def analyze(self, chat: SuperChatCreate) -> SuperChatQueueItem:
        """
        Full analysis pipeline for a super chat.
        Makes ONE Gemini call, then distributes results to agents.
        """
        chat_id = str(uuid.uuid4())
        
        # Step 1: Single LLM call for all AI analysis
        llm_results = await self._call_gemini(chat)
        
        # Step 2: Run moderation agent (with LLM + regex)
        mod_data = {
            "message": chat.message,
            "_llm_moderation": llm_results.get("moderation", {}),
        }
        mod_result = await self.moderation(mod_data)
        
        # Step 3: Run sentiment agent
        sent_data = {
            "message": chat.message,
            "_llm_sentiment": llm_results.get("sentiment", {}),
        }
        sent_result = await self.sentiment(sent_data)
        
        # Step 4: Run revenue agent (rule-based, uses sentiment for bonus)
        rev_data = {
            "amount": chat.amount,
            "intent": sent_result.get("intent", "other"),
        }
        rev_result = await self.revenue(rev_data)
        
        # Step 5: Run response agent
        resp_data = {
            "author_name": chat.author_name,
            "amount": chat.amount,
            "_llm_response": llm_results.get("response", {}),
        }
        resp_result = await self.response(resp_data)
        
        # Reduce priority for flagged chats
        priority = rev_result.get("priority_score", 50)
        if not mod_result.get("is_safe", True):
            priority = max(1, priority - 30)
        
        # Build final queue item
        queue_item = SuperChatQueueItem(
            id=chat_id,
            author_name=chat.author_name,
            message=chat.message,
            amount=chat.amount,
            currency=chat.currency,
            priority_score=priority,
            tier=Tier(rev_result.get("tier", "bronze")),
            sentiment=Sentiment(sent_result.get("sentiment", "neutral")),
            intent=Intent(sent_result.get("intent", "other")),
            risk_level=RiskLevel(mod_result.get("risk_level", "low")),
            suggested_reply=resp_result.get("suggested_reply"),
            status=ChatStatus.QUEUED,
            received_at=datetime.utcnow(),
        )
        
        logger.info(
            f"🤖 Analyzed: {chat.author_name} | "
            f"${chat.amount} | {queue_item.sentiment.value} | "
            f"Priority: {queue_item.priority_score} | "
            f"Risk: {queue_item.risk_level.value}"
        )
        
        return queue_item
    
    async def _call_gemini(self, chat: SuperChatCreate) -> Dict[str, Any]:
        """Make a single Gemini call for all analysis."""
        try:
            prompt = ANALYSIS_PROMPT.format(
                author_name=chat.author_name,
                message=chat.message,
                amount=chat.amount,
                currency=chat.currency,
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            
            raw_text = response.text.strip()
            
            # Clean potential markdown wrapping
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text
                raw_text = raw_text.rsplit("```", 1)[0]
                raw_text = raw_text.strip()
            
            result = json.loads(raw_text)
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Gemini JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return {}
