"""
Command-line interface for the Productivity Agent system.
"""

import asyncio
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from src.utils.recording import RecordingManager
from src.utils.question_recorder import QuestionRecorder

class CLI:
    """Command-line interface for the Productivity Agent system."""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize managers
        self.recording_manager = RecordingManager(self.config)
        self.question_recorder = QuestionRecorder(self.config)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load system configuration."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}
            
    def _setup_logging(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger("CLI")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it exists
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        fh = logging.FileHandler(log_dir / "cli.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    async def record_posture(self, duration: int = 300):
        """Record and analyze posture for a specified duration."""
        try:
            self.logger.info(f"Starting posture recording for {duration} seconds")
            
            # Start recording
            result = await self.recording_manager.start_recording(
                f"posture_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if 'error' in result:
                self.logger.error(f"Failed to start recording: {result['error']}")
                return
            
            # Wait for specified duration
            await asyncio.sleep(duration)
            
            # Stop recording
            result = await self.recording_manager.stop_recording()
            
            if 'error' in result:
                self.logger.error(f"Failed to stop recording: {result['error']}")
                return
            
            self.logger.info(f"Recording completed: {result['filepath']}")
            self.logger.info(f"Analysis saved to: {result['analysis_file']}")
            
        except Exception as e:
            self.logger.error(f"Error in posture recording: {e}")
    
    async def record_response(self, question_id: str, duration: Optional[int] = None):
        """Record and analyze a response to a question."""
        try:
            self.logger.info(f"Starting response recording for question {question_id}")
            
            # Start recording
            result = await self.question_recorder.start_recording(question_id)
            
            if 'error' in result:
                self.logger.error(f"Failed to start recording: {result['error']}")
                return
            
            if duration:
                # Wait for specified duration
                await asyncio.sleep(duration)
            else:
                # Wait for user input to stop
                input("Press Enter to stop recording...")
            
            # Stop recording
            result = await self.question_recorder.stop_recording()
            
            if 'error' in result:
                self.logger.error(f"Failed to stop recording: {result['error']}")
                return
            
            self.logger.info(f"Recording completed: {result['session_id']}")
            self.logger.info(f"Analysis saved to: {result['analysis_file']}")
            
        except Exception as e:
            self.logger.error(f"Error in response recording: {e}")
    
    async def monitor_posture(self, duration: int = 300, interval: int = 5):
        """Monitor posture in real-time."""
        try:
            self.logger.info(f"Starting posture monitoring for {duration} seconds")
            
            # Start recording
            result = await self.recording_manager.start_recording(
                f"monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if 'error' in result:
                self.logger.error(f"Failed to start recording: {result['error']}")
                return
            
            # Monitor for specified duration
            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < duration:
                metrics = await self.recording_manager.get_realtime_metrics()
                
                if metrics:
                    print("\nPosture Metrics:")
                    print(f"Shoulder Alignment: {metrics.shoulder_alignment:.2f}")
                    print(f"Back Straightness: {metrics.back_straightness:.2f}")
                    print(f"Head Position: {metrics.head_position:.2f}")
                    print(f"Neck Angle: {metrics.neck_angle:.2f}")
                    print(f"Confidence: {metrics.confidence:.2f}")
                
                await asyncio.sleep(interval)
            
            # Stop recording
            result = await self.recording_manager.stop_recording()
            
            if 'error' in result:
                self.logger.error(f"Failed to stop recording: {result['error']}")
                return
            
            self.logger.info(f"Monitoring completed: {result['filepath']}")
            self.logger.info(f"Analysis saved to: {result['analysis_file']}")
            
        except Exception as e:
            self.logger.error(f"Error in posture monitoring: {e}")
    
    async def monitor_response(self, question_id: str, duration: Optional[int] = None, interval: int = 5):
        """Monitor response metrics in real-time."""
        try:
            self.logger.info(f"Starting response monitoring for question {question_id}")
            
            # Start recording
            result = await self.question_recorder.start_recording(question_id)
            
            if 'error' in result:
                self.logger.error(f"Failed to start recording: {result['error']}")
                return
            
            # Monitor for specified duration or until user stops
            start_time = datetime.now()
            while True:
                if duration and (datetime.now() - start_time).total_seconds() >= duration:
                    break
                
                metrics = await self.question_recorder.get_realtime_metrics()
                
                if metrics:
                    print("\nResponse Metrics:")
                    print(f"Confidence: {metrics.confidence:.2f}")
                    print(f"Speaking Rate: {metrics.speaking_rate:.2f}")
                    print(f"Clarity: {metrics.clarity:.2f}")
                    print(f"Engagement: {metrics.engagement:.2f}")
                    print(f"Audio Quality: {metrics.audio_quality:.2f}")
                
                await asyncio.sleep(interval)
            
            # Stop recording
            result = await self.question_recorder.stop_recording()
            
            if 'error' in result:
                self.logger.error(f"Failed to stop recording: {result['error']}")
                return
            
            self.logger.info(f"Monitoring completed: {result['session_id']}")
            self.logger.info(f"Analysis saved to: {result['analysis_file']}")
            
        except Exception as e:
            self.logger.error(f"Error in response monitoring: {e}")

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Productivity Agent CLI")
    parser.add_argument("--config", default="src/config/system_config.json",
                      help="Path to system configuration file")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Posture recording command
    posture_parser = subparsers.add_parser("record-posture",
                                          help="Record and analyze posture")
    posture_parser.add_argument("--duration", type=int, default=300,
                              help="Recording duration in seconds")
    
    # Response recording command
    response_parser = subparsers.add_parser("record-response",
                                          help="Record and analyze a response")
    response_parser.add_argument("question_id", help="ID of the question")
    response_parser.add_argument("--duration", type=int,
                              help="Recording duration in seconds")
    
    # Posture monitoring command
    monitor_posture_parser = subparsers.add_parser("monitor-posture",
                                                 help="Monitor posture in real-time")
    monitor_posture_parser.add_argument("--duration", type=int, default=300,
                                      help="Monitoring duration in seconds")
    monitor_posture_parser.add_argument("--interval", type=int, default=5,
                                      help="Update interval in seconds")
    
    # Response monitoring command
    monitor_response_parser = subparsers.add_parser("monitor-response",
                                                  help="Monitor response metrics in real-time")
    monitor_response_parser.add_argument("question_id", help="ID of the question")
    monitor_response_parser.add_argument("--duration", type=int,
                                      help="Monitoring duration in seconds")
    monitor_response_parser.add_argument("--interval", type=int, default=5,
                                      help="Update interval in seconds")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = CLI(args.config)
    
    if args.command == "record-posture":
        asyncio.run(cli.record_posture(args.duration))
    elif args.command == "record-response":
        asyncio.run(cli.record_response(args.question_id, args.duration))
    elif args.command == "monitor-posture":
        asyncio.run(cli.monitor_posture(args.duration, args.interval))
    elif args.command == "monitor-response":
        asyncio.run(cli.monitor_response(args.question_id, args.duration, args.interval))

if __name__ == "__main__":
    main() 