from typing import Dict, List, Optional
from datetime import datetime

class BaseAgent:
    """Base class for all agents in the system"""
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.memory = []
        self.state = {}
        self.created_at = datetime.now()
        
    def process(self, input_data: Dict) -> Dict:
        """Process input data and return results"""
        raise NotImplementedError
        
    def reflect(self) -> Dict:
        """Self-reflection on performance and learning"""
        raise NotImplementedError
        
    def update_state(self, new_state: Dict) -> None:
        """Update agent's internal state"""
        self.state.update(new_state)
        
    def add_to_memory(self, item: Dict) -> None:
        """Add an item to agent's memory"""
        self.memory.append({
            "timestamp": datetime.now(),
            "content": item
        })
        
    def get_recent_memory(self, n: int = 5) -> List[Dict]:
        """Get n most recent memory items"""
        return self.memory[-n:] 