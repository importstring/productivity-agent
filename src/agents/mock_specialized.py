"""Mock implementations of specialized agents for testing."""
from typing import Dict, List
import json
import os
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NightlyAnalysisAgent:
    """Mock implementation of NightlyAnalysisAgent for testing purposes."""
    
    def __init__(self):
        """Initialize the mock NightlyAnalysisAgent."""
        self.latest_recordings_dir = Path("data/recordings")
        self.analysis_dir = Path("data/analysis")
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
    
    async def analyze_latest_recording(self) -> Dict:
        """Mock implementation that returns a sample analysis result."""
        logger.info("Mock NightlyAnalysisAgent: Analyzing latest recording")
        
        # Check if there are any recordings
        if not self.latest_recordings_dir.exists() or not any(self.latest_recordings_dir.iterdir()):
            logger.warning("No recordings found in data/recordings")
            # Create a mock recording file for testing
            self.latest_recordings_dir.mkdir(parents=True, exist_ok=True)
            mock_recording = self.latest_recordings_dir / f"mock_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(mock_recording, 'w') as f:
                json.dump({"timestamp": datetime.now().isoformat(), "duration": 300, "type": "mock"}, f)
        
        # Generate mock analysis result
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "recording_id": f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "posture_analysis": {
                "head_position": {"average": 0.85, "trend": "improving"},
                "shoulder_alignment": {"average": 0.78, "trend": "stable"},
                "back_straightness": {"average": 0.92, "trend": "improving"}
            },
            "speech_analysis": {
                "clarity": {"average": 0.88, "trend": "improving"},
                "speaking_rate": 125.5,
                "pitch": {"variance": 0.15, "range": [75, 150]},
                "tone": {"warmth": 0.72, "brightness": 0.65, "clarity": 0.83}
            },
            "engagement_analysis": {
                "eye_contact": {"average": 0.76, "trend": "improving"},
                "gesture_frequency": {"average": 0.68, "trend": "stable"},
                "expression_variance": {"average": 0.81, "trend": "improving"}
            },
            "multimodal_analysis": {
                "overall_coherence": {"average": 0.79, "trend": "improving"},
                "speech_posture_alignment": {"score": 0.82, "pattern_matches": 5}
            },
            "progress_metrics": {
                "overall": {"score": 0.84, "confidence": 0.92, "trend": "improving"},
                "posture": {"average_improvement": 0.08, "consistency": 0.85, "trend": "improving"},
                "speech": {"average_improvement": 0.06, "consistency": 0.82, "trend": "improving"},
                "engagement": {"average_improvement": 0.07, "consistency": 0.88, "trend": "improving"},
                "multimodal": {"average_improvement": 0.05, "consistency": 0.79, "trend": "stable"}
            },
            "improvement_suggestions": [
                "Focus on maintaining consistent shoulder alignment throughout presentations",
                "Practice varying pitch more to add dynamism to speech",
                "Consider increasing gesture frequency slightly for better engagement",
                "Work on synchronizing posture shifts with speech emphasis points"
            ]
        }
        
        logger.info("Mock analysis completed successfully")
        return analysis_result

class QuestionRecorder:
    """Mock implementation of QuestionRecorder for testing purposes."""
    
    def __init__(self, config):
        """Initialize the mock QuestionRecorder."""
        self.config = config
        self.recording = False
        self.session_id = None
        self.metrics = {
            "response_time": 2.5,
            "clarity": 0.85,
            "confidence": 0.78,
            "engagement": 0.92
        }
    
    async def start_recording(self, session_id):
        """Start a mock recording session."""
        logger.info(f"Mock QuestionRecorder: Starting recording session {session_id}")
        self.recording = True
        self.session_id = session_id
        return {
            "status": "success",
            "session_id": session_id,
            "started_at": datetime.now().isoformat()
        }
    
    async def stop_recording(self):
        """Stop the mock recording session."""
        logger.info(f"Mock QuestionRecorder: Stopping recording session {self.session_id}")
        self.recording = False
        
        # Generate mock recording paths
        video_path = f"data/recordings/{self.session_id}_video.mp4"
        audio_path = f"data/recordings/{self.session_id}_audio.wav"
        
        # Return mock result
        return {
            "status": "success",
            "session_id": self.session_id,
            "video_path": video_path,
            "audio_path": audio_path,
            "duration": 300,
            "metrics": self.metrics,
            "ended_at": datetime.now().isoformat()
        }
    
    async def get_realtime_metrics(self):
        """Get mock real-time metrics."""
        if not self.recording:
            return None
        
        # Vary metrics slightly to simulate real-time changes
        import random
        self.metrics = {
            "response_time": round(2.5 + random.uniform(-0.5, 0.5), 2),
            "clarity": round(0.85 + random.uniform(-0.05, 0.05), 2),
            "confidence": round(0.78 + random.uniform(-0.08, 0.08), 2),
            "engagement": round(0.92 + random.uniform(-0.1, 0.1), 2)
        }
        
        return self.metrics 