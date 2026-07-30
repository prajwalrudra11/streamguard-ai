"""
StreamGuard AI - Revenue Agent
Prioritizes super chats based on payment and loyalty.
"""
from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class RevenueAgent(BaseAgent):
    """Calculates priority score based on payment amount and loyalty."""
    
    # Tier thresholds (USD)
    TIER_THRESHOLDS = {
        "diamond": 50.0,
        "gold": 20.0,
        "silver": 10.0,
        "bronze": 0.0,
    }
    
    # Priority base scores per tier
    TIER_SCORES = {
        "diamond": 90,
        "gold": 70,
        "silver": 50,
        "bronze": 30,
    }
    
    def __init__(self):
        super().__init__("revenue")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate priority score and tier."""
        amount = data.get("amount", 0.0)
        intent = data.get("intent", "other")
        
        # Determine tier
        tier = "bronze"
        for t, threshold in self.TIER_THRESHOLDS.items():
            if amount >= threshold:
                tier = t
                break
        
        # Base score from tier
        score = self.TIER_SCORES.get(tier, 30)
        
        # Bonus for questions (fans expect answers)
        if intent == "question":
            score = min(100, score + 10)
        
        # Bonus for high amounts within tier
        if tier == "diamond" and amount >= 100:
            score = 100  # Max priority
        
        return {
            "priority_score": score,
            "tier": tier,
            "is_repeat_supporter": False,  # TODO: Track with user history
            "is_first_time": True,  # TODO: Track with user history
        }
    
    def _fallback(self, data, error):
        return {
            "priority_score": 50,
            "tier": "bronze",
            "is_repeat_supporter": False,
            "is_first_time": True,
        }
