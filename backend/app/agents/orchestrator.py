"""
StreamGuard AI - Agent Orchestrator
Coordinates all AI agents in a single optimized pipeline powered by IBM Granite (watsonx.ai).
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any
import urllib.request
import urllib.parse
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

# Structured prompt for batched multi-agent analysis
ANALYSIS_PROMPT = """You are StreamGuard AI, an AI co-pilot powered by IBM Granite analyzing a live stream super chat.

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
    """Coordinates all AI agents in an optimized pipeline using IBM Granite."""
    
    def __init__(self):
        self.settings = get_settings()
        self.primary_model = self.settings.ibm_granite_model  # "ibm/granite-3-8b-instruct"
        
        # Initialize specialized sub-agents
        self.moderation = ModerationAgent()
        self.sentiment = SentimentAgent()
        self.revenue = RevenueAgent()
        self.response = ResponseAgent()
        
        # Initialize Google fallback client if key exists
        self._gemini_client = None
        if self.settings.gemini_api_key:
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=self.settings.gemini_api_key)
            except Exception as e:
                logger.warning(f"Gemini client initialization notice: {e}")
        
        logger.info(f"🤖 Orchestrator initialized with IBM Granite ({self.primary_model})")
    
    async def analyze(self, chat: SuperChatCreate) -> SuperChatQueueItem:
        """
        Full analysis pipeline for a super chat.
        Makes ONE single-pass LLM call via IBM Granite, then distributes results to agents.
        """
        chat_id = str(uuid.uuid4())
        
        # Step 1: Single LLM call for all AI analysis
        llm_results = await self._call_llm(chat)
        
        # Step 2: Run moderation agent (LLM + regex)
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
        
        # Step 4: Run revenue agent
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
            f"🤖 IBM Granite Analyzed: {chat.author_name} | "
            f"${chat.amount} | {queue_item.sentiment.value} | "
            f"Priority: {queue_item.priority_score} | "
            f"Risk: {queue_item.risk_level.value}"
        )
        
        return queue_item
    
    async def _call_llm(self, chat: SuperChatCreate) -> Dict[str, Any]:
        """Make a single LLM call for all analysis (IBM Granite primary, Gemini fallback)."""
        prompt = ANALYSIS_PROMPT.format(
            author_name=chat.author_name,
            message=chat.message,
            amount=chat.amount,
            currency=chat.currency,
        )
        
        # 1. Try IBM watsonx / IBM Granite API
        if self.settings.watsonx_api_key and self.settings.watsonx_project_id:
            res = await self._call_watsonx_granite(prompt)
            if res:
                return res
        
        # 2. Try Gemini fallback if configured
        if self._gemini_client:
            res = await self._call_gemini_fallback(prompt)
            if res:
                return res
        
        # 3. Intelligent fallback parsing for local development
        return self._heuristic_fallback(chat)

    async def _get_iam_token(self, api_key: str) -> str:
        """Exchange IBM Cloud API key for an IAM Bearer access token."""
        if not api_key or api_key.startswith("ey"):  # Already a bearer token
            return api_key
        try:
            url = "https://iam.cloud.ibm.com/identity/token"
            data = urllib.parse.urlencode({
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": api_key
            }).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res.get("access_token", api_key)
        except Exception as e:
            logger.warning(f"IBM Cloud IAM token exchange notice: {e}")
            return api_key

    async def _call_watsonx_granite(self, prompt: str) -> Dict[str, Any]:
        """Invoke IBM Granite 3.1 model via IBM watsonx.ai REST endpoint."""
        try:
            bearer_token = await self._get_iam_token(self.settings.watsonx_api_key)
            url = f"{self.settings.watsonx_url}/ml/v1/text/generation?version=2023-05-29"
            payload = {
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 300,
                    "min_new_tokens": 10
                },
                "model_id": self.primary_model,
                "project_id": self.settings.watsonx_project_id
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {bearer_token}"
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                raw_text = res_data['results'][0]['generated_text'].strip()
                return self._parse_json(raw_text)
        except Exception as e:
            logger.warning(f"watsonx Granite API call notice: {e}")
            return {}

    async def _call_gemini_fallback(self, prompt: str) -> Dict[str, Any]:
        """Fallback LLM call."""
        try:
            response = self._gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            return self._parse_json(response.text.strip())
        except Exception as e:
            logger.warning(f"Fallback LLM call notice: {e}")
            return {}

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Clean and parse JSON from LLM outputs."""
        try:
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text
                raw_text = raw_text.rsplit("```", 1)[0]
                raw_text = raw_text.strip()
            return json.loads(raw_text)
        except Exception:
            return {}

    def _heuristic_fallback(self, chat: SuperChatCreate) -> Dict[str, Any]:
        """Rule-based intelligent fallback for offline dev/testing."""
        msg_lower = chat.message.lower()
        is_question = "?" in chat.message or any(w in msg_lower for w in ["what", "why", "how", "when", "can you"])
        is_toxic = any(w in msg_lower for w in ["hate", "dumb", "scam", "ugly"])
        
        reply = f"Thank you so much {chat.author_name} for the generous support!"
        if chat.amount >= 20:
            reply = f"Wow {chat.author_name}! Thank you so much for the amazing ${chat.amount} super chat!"
        elif is_question:
            reply = f"Great question {chat.author_name}! Thanks for bringing that up."
            
        return {
            "moderation": {"is_toxic": is_toxic, "is_nsfw": False, "is_spam": False},
            "sentiment": {
                "sentiment": "negative" if is_toxic else "positive" if chat.amount >= 10 else "neutral",
                "intent": "question" if is_question else "compliment"
            },
            "response": {
                "suggested_reply": reply,
                "reply_tone": "grateful"
            }
        }
