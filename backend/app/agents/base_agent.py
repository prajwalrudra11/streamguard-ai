"""
StreamGuard AI - Base Agent Interface
Abstract base class for all AI agents.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from app.core.logging import get_logger


class BaseAgent(ABC):
    """Base class for all StreamGuard AI agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"agent.{name}")
        self._call_count = 0
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return analysis results."""
        pass
    
    async def __call__(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with logging."""
        self._call_count += 1
        self.logger.debug(f"Processing (call #{self._call_count})")
        
        try:
            result = await self.process(data)
            self.logger.debug(f"Completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Failed: {e}")
            return self._fallback(data, e)
    
    def _fallback(self, data: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Return safe defaults if the agent fails."""
        return {}
