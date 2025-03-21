"""Mock implementation of MultiAgentSystem for testing."""
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class MultiAgentSystem:
    """Mock implementation of MultiAgentSystem for testing."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the mock MultiAgentSystem."""
        self.config = config
        self.initialized = False
        
    async def initialize(self):
        """Initialize the mock system."""
        logger.info("Mock MultiAgentSystem: Initializing...")
        self.initialized = True
        
    async def cleanup(self):
        """Clean up resources."""
        logger.info("Mock MultiAgentSystem: Cleaning up...")
        self.initialized = False
        
    async def process_question(self, data: Dict[str, Any]) -> str:
        """Process a question and return a mock response."""
        question = data.get('question', '')
        logger.info(f"Mock MultiAgentSystem: Processing question: {question}")
        return f"Mock answer to: {question}"
    
    async def generate_insights(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mock insights from data."""
        logger.info("Mock MultiAgentSystem: Generating insights...")
        return [
            {
                "topic": "Productivity",
                "insight": "You tend to be most productive in the morning",
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat()
            },
            {
                "topic": "Focus",
                "insight": "Your focus sessions are more effective when preceded by physical activity",
                "confidence": 0.78,
                "timestamp": datetime.now().isoformat()
            }
        ] 