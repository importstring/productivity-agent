"""Mock implementation of the RecordingManager for testing."""
import json
import os
from pathlib import Path
from datetime import datetime
import logging
import random

logger = logging.getLogger(__name__)

class RecordingManager:
    """Mock implementation of RecordingManager for testing."""
    
    def __init__(self, config):
        """Initialize the mock RecordingManager."""
        self.config = config
        self.recording = False
        self.session_id = None
        self.filepath = None
        
    async def start_recording(self, session_id):
        """Start a mock recording session."""
        logger.info(f"Mock RecordingManager: Starting recording session {session_id}")
        self.recording = True
        self.session_id = session_id
        
        # Create recordings directory if it doesn't exist
        os.makedirs("data/recordings", exist_ok=True)
        
        # Create placeholder file
        self.filepath = f"data/recordings/{session_id}.json"
        with open(self.filepath, 'w') as f:
            json.dump({
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "status": "recording"
            }, f, indent=2)
        
        return {"status": "success", "session_id": session_id}
    
    async def stop_recording(self):
        """Stop the mock recording session."""
        logger.info(f"Mock RecordingManager: Stopping recording session {self.session_id}")
        self.recording = False
        
        # Update placeholder file
        with open(self.filepath, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "duration": 300,
                "metrics": {
                    "head_position": 0.85,
                    "shoulder_alignment": 0.78,
                    "back_straightness": 0.92
                }
            }, f, indent=2)
        
        return {"status": "success", "filepath": self.filepath}
    
    async def get_realtime_metrics(self):
        """Get mock real-time metrics."""
        if not self.recording:
            return None
        
        # Generate random metrics
        return {
            "head_position": round(0.85 + random.uniform(-0.1, 0.1), 2),
            "shoulder_alignment": round(0.78 + random.uniform(-0.1, 0.1), 2),
            "back_straightness": round(0.92 + random.uniform(-0.1, 0.1), 2)
        } 