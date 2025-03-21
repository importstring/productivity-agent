"""
Recording and computer vision utilities for the Productivity Agent system.
"""

import cv2
import numpy as np
from datetime import datetime
import json
from pathlib import Path
import mediapipe as mp
import logging
from typing import Dict, List, Optional, Tuple, Any
import asyncio
from dataclasses import dataclass
import threading
import queue
import os
import time
import random

@dataclass
class PostureMetrics:
    """Data class for storing posture metrics."""
    shoulder_alignment: float
    back_straightness: float
    head_position: float
    neck_angle: float
    timestamp: str
    confidence: float

# Add test mode flag
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"

class RecordingManager:
    """Manages video recording and computer vision analysis."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("RecordingManager")
        
        # Check if we're in a GUI environment
        self.has_display = "DISPLAY" in os.environ or os.environ.get("TERM_PROGRAM") == "Apple_Terminal"
        
        # Initialize MediaPipe if not in test mode
        if not TEST_MODE:
            try:
                # Import MediaPipe here to avoid dependency issues in test mode
                import mediapipe as mp
                self.mp = mp
                self.mp_pose = mp.solutions.pose
                self.mp_drawing = mp.solutions.drawing_utils
                self.pose = self.mp_pose.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    smooth_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                self.logger.info("MediaPipe pose detection initialized successfully")
            except ImportError:
                self.logger.warning("MediaPipe not available, pose detection will be limited")
                self.mp = None
                self.mp_pose = None
                self.pose = None
        
        # Recording state
        self.is_recording = False
        self.current_recording = None
        self.current_session_id = None
        self.metrics_queue = queue.Queue()
        
        # Create necessary directories
        self.recordings_dir = Path(self.config.get("recording", {}).get("storage", {}).get("recordings_dir", "data/recordings"))
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        
    async def start_recording(self, session_id: str) -> Dict[str, Any]:
        """Start a recording session."""
        try:
            self.logger.info(f"Starting recording session: {session_id}")
            
            # In test mode, simulate starting a recording
            if TEST_MODE:
                self.logger.info("TEST MODE: Simulating start of recording")
                self.is_recording = True
                self.current_session_id = session_id
                self.current_recording = {
                    'session_id': session_id,
                    'start_time': datetime.now().isoformat()
                }
                return {
                    "status": "success",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
                
            if not self.pose:
                raise RuntimeError("MediaPipe pose detection not initialized")
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{session_id}_{timestamp}.avi"  # Using .avi for MJPG codec
            filepath = self.recordings_dir / filename
            
            # Initialize video capture with known working settings
            cap = cv2.VideoCapture(0)  # Use camera index 0
            if not cap.isOpened():
                raise RuntimeError("Failed to open camera")
            
            # Set camera properties to match the working settings we found
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Get actual camera properties
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            self.logger.info(f"Camera initialized with resolution: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            # Initialize video writer with MJPG codec
            fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
            out = cv2.VideoWriter(
                str(filepath),
                fourcc,
                actual_fps,
                (actual_width, actual_height)
            )
            
            if not out.isOpened():
                raise RuntimeError("Failed to create video writer")
            
            self.current_recording = {
                'cap': cap,
                'writer': out,
                'filepath': filepath,
                'session_id': session_id,
                'start_time': datetime.now().isoformat()
            }
            
            # Start recording thread
            self.is_recording = True
            threading.Thread(target=self._recording_thread, daemon=True).start()
            
            return {
                'status': 'success',
                'filepath': str(filepath),
                'session_id': session_id
            }
            
        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
            return {'error': str(e)}
    
    async def stop_recording(self) -> Dict:
        """Stop the current recording session."""
        try:
            if not self.is_recording:
                return {"error": "No active recording session"}
            
            self.logger.info(f"Stopping recording session: {self.current_session_id}")
            
            # In test mode, simulate stopping a recording
            if TEST_MODE:
                self.logger.info("TEST MODE: Simulating stop of recording")
                self.is_recording = False
                
                # Generate mock data for the session
                recordings_dir = Path("data/recordings")
                recordings_dir.mkdir(parents=True, exist_ok=True)
                
                video_path = recordings_dir / f"{self.current_session_id}_video.mp4"
                
                # Create empty files to simulate recording
                with open(video_path, 'w') as f:
                    f.write("Mock video file")
                
                filepath = recordings_dir / f"{self.current_session_id}.json"
                
                # Generate mock metrics
                metrics = self._generate_mock_metrics()
                
                # Save mock results to file
                with open(filepath, 'w') as f:
                    json.dump({
                        "session_id": self.current_session_id,
                        "start_time": (datetime.now().timestamp() - 300),  # 5 minutes ago
                        "end_time": datetime.now().timestamp(),
                        "metrics": metrics
                    }, f, indent=2)
                
                result = {
                    "status": "success",
                    "session_id": self.current_session_id,
                    "filepath": str(filepath),
                    "video_path": str(video_path)
                }
                
                self.current_session_id = None
                return result
            
            self.is_recording = False
            
            # Release resources
            self.current_recording['cap'].release()
            self.current_recording['writer'].release()
            
            if self.has_display:
                cv2.destroyAllWindows()
            
            # Process final analysis
            analysis = await self._process_recording(self.current_recording['filepath'])
            
            # Save analysis results
            analysis_file = self.current_recording['filepath'].with_suffix('.json')
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f)
            
            return {
                'status': 'success',
                'filepath': str(self.current_recording['filepath']),
                'analysis_file': str(analysis_file)
            }
            
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
            return {'error': str(e)}
    
    def _recording_thread(self):
        """Thread for capturing, analyzing, and recording video frames."""
        try:
            start_time = time.time()
            frame_count = 0
            pose_count = 0
            last_fps_print = time.time()
            
            while self.is_recording:
                # Read a frame
                ret, frame = self.current_recording['cap'].read()
                if not ret:
                    self.logger.error("Failed to capture frame")
                    break
                
                frame_count += 1
                
                # Process frame with MediaPipe
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(frame_rgb)
                
                # Analyze pose if detected
                if results.pose_landmarks:
                    pose_count += 1
                    metrics = self._analyze_pose(results.pose_landmarks.landmark)
                    if metrics:
                        self.metrics_queue.put(metrics)
                    
                    # Draw landmarks on frame for monitoring
                    if self.has_display:
                        annotated_frame = frame.copy()
                        self.mp_drawing.draw_landmarks(
                            annotated_frame,
                            results.pose_landmarks,
                            self.mp_pose.POSE_CONNECTIONS
                        )
                        cv2.imshow('Posture Monitor', annotated_frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            self.is_recording = False
                            break
                
                # Write original frame to video file
                self.current_recording['writer'].write(frame)
                
                # Print stats every second
                current_time = time.time()
                if current_time - last_fps_print >= 1:
                    elapsed = current_time - start_time
                    fps_actual = frame_count / elapsed
                    pose_rate = pose_count / elapsed
                    self.logger.info(f"FPS: {fps_actual:.1f}, Pose Detection Rate: {pose_rate:.1f}/s")
                    last_fps_print = current_time
                
        except Exception as e:
            self.logger.error(f"Error in recording thread: {e}")
            self.is_recording = False
    
    def _analyze_pose(self, landmarks) -> Optional[PostureMetrics]:
        """Analyze pose landmarks and calculate metrics."""
        try:
            # Calculate metrics
            shoulder_alignment = self._calculate_shoulder_alignment(landmarks)
            back_straightness = self._calculate_back_straightness(landmarks)
            head_position = self._calculate_head_position(landmarks)
            neck_angle = self._calculate_neck_angle(landmarks)
            
            # Calculate average confidence from upper body landmarks
            upper_body_indices = [
                self.mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                self.mp_pose.PoseLandmark.LEFT_EAR.value,
                self.mp_pose.PoseLandmark.RIGHT_EAR.value,
                self.mp_pose.PoseLandmark.NOSE.value
            ]
            confidence = np.mean([landmarks[i].visibility for i in upper_body_indices])
            
            return PostureMetrics(
                shoulder_alignment=shoulder_alignment,
                back_straightness=back_straightness,
                head_position=head_position,
                neck_angle=neck_angle,
                timestamp=datetime.now().isoformat(),
                confidence=confidence
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing pose: {e}")
            return None
    
    def _calculate_shoulder_alignment(self, landmarks) -> float:
        """Calculate shoulder alignment score."""
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        
        # Calculate angle between shoulders
        angle = abs(np.arctan2(
            right_shoulder.y - left_shoulder.y,
            right_shoulder.x - left_shoulder.x
        ))
        
        # Convert to score (0-1, where 1 is perfect alignment)
        return 1 - (angle / np.pi)
    
    def _calculate_back_straightness(self, landmarks) -> float:
        """Calculate back straightness score."""
        hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        
        # Calculate angle between hip and shoulder
        angle = abs(np.arctan2(
            shoulder.y - hip.y,
            shoulder.x - hip.x
        ))
        
        # Convert to score (0-1, where 1 is perfect straightness)
        return 1 - (angle / np.pi)
    
    def _calculate_head_position(self, landmarks) -> float:
        """Calculate head position score."""
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
        left_ear = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value]
        right_ear = landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value]
        
        # Calculate head tilt
        ear_angle = abs(np.arctan2(
            right_ear.y - left_ear.y,
            right_ear.x - left_ear.x
        ))
        
        # Calculate head forward position
        forward_position = nose.z - (left_ear.z + right_ear.z) / 2
        
        # Combine scores
        tilt_score = 1 - (ear_angle / np.pi)
        position_score = 1 - abs(forward_position)
        
        return (tilt_score + position_score) / 2
    
    def _calculate_neck_angle(self, landmarks) -> float:
        """Calculate neck angle score."""
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
        mid_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        
        # Calculate angle between nose and shoulder (approximating neck angle)
        angle = abs(np.arctan2(
            nose.y - mid_shoulder.y,
            nose.x - mid_shoulder.x
        ))
        
        # Convert to score (0-1, where 1 is perfect alignment)
        return 1 - (angle / np.pi)
    
    async def _process_recording(self, filepath: Path) -> Dict:
        """Process the completed recording and generate analysis."""
        metrics = []
        while not self.metrics_queue.empty():
            metric = self.metrics_queue.get()
            if metric:
                metrics.append({
                    'shoulder_alignment': metric.shoulder_alignment,
                    'back_straightness': metric.back_straightness,
                    'head_position': metric.head_position,
                    'neck_angle': metric.neck_angle,
                    'confidence': metric.confidence,
                    'timestamp': metric.timestamp
                })
        
        return {
            'filepath': str(filepath),
            'metrics': metrics,
            'summary': {
                'total_frames_analyzed': len(metrics),
                'average_metrics': {
                    'shoulder_alignment': np.mean([m['shoulder_alignment'] for m in metrics]) if metrics else 0,
                    'back_straightness': np.mean([m['back_straightness'] for m in metrics]) if metrics else 0,
                    'head_position': np.mean([m['head_position'] for m in metrics]) if metrics else 0,
                    'neck_angle': np.mean([m['neck_angle'] for m in metrics]) if metrics else 0,
                    'confidence': np.mean([m['confidence'] for m in metrics]) if metrics else 0
                } if metrics else {'error': 'No valid metrics collected'}
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_realtime_metrics(self) -> Optional[PostureMetrics]:
        """Get the most recent posture metrics."""
        try:
            if not self.is_recording:
                return None
                
            # In test mode, generate random metrics
            if TEST_MODE:
                return self._generate_mock_realtime_metrics()
                
            # TODO: Implement actual real-time metrics collection
            # This would include analyzing the current frame for posture
            
            # Placeholder for actual implementation
            return self.metrics_queue.get_nowait()
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {e}")
            return None
    
    def _generate_mock_metrics(self) -> List[Dict[str, Any]]:
        """Generate mock metrics for testing."""
        metrics = []
        
        # Generate 10 timepoints with random metrics
        start_time = datetime.now()
        for i in range(10):
            timestamp = start_time.timestamp() + i * 30  # 30 seconds apart
            metrics.append({
                "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
                "shoulder_alignment": round(random.uniform(0.7, 0.95), 2),
                "back_straightness": round(random.uniform(0.75, 0.95), 2),
                "head_position": round(random.uniform(0.7, 0.9), 2),
                "neck_angle": round(random.uniform(0.7, 0.9), 2),
                "confidence": round(random.uniform(0.8, 0.98), 2),
                "engagement": round(random.uniform(0.75, 0.95), 2)
            })
            
        return metrics
    
    def _generate_mock_realtime_metrics(self) -> Dict[str, Any]:
        """Generate mock real-time metrics for testing."""
        return {
            "timestamp": datetime.now().isoformat(),
            "posture": {
                "shoulder_alignment": round(random.uniform(0.7, 0.95), 2),
                "back_straightness": round(random.uniform(0.75, 0.95), 2),
                "head_position": round(random.uniform(0.7, 0.9), 2),
                "neck_angle": round(random.uniform(0.7, 0.9), 2)
            },
            "confidence": round(random.uniform(0.8, 0.98), 2),
            "engagement": round(random.uniform(0.75, 0.95), 2)
        } 