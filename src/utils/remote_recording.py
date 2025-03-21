"""
Remote recording and analysis utilities for cross-device video processing.
"""

import cv2
import numpy as np
from datetime import datetime
import json
from pathlib import Path
import mediapipe as mp
import logging
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
import threading
import queue
import os
import time
import socket
import struct
import pickle
import zlib

@dataclass
class RecordingConfig:
    """Configuration for remote recording."""
    device_name: str
    resolution: Tuple[int, int]
    fps: int
    codec: str
    output_dir: str
    server_host: str
    server_port: int

class RemoteRecordingManager:
    """Manages remote video recording and analysis."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("RemoteRecordingManager")
        
        # Initialize MediaPipe
        try:
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
        except Exception as e:
            self.logger.error(f"Failed to initialize MediaPipe: {e}")
            self.pose = None
        
        # Create necessary directories
        self.recordings_dir = Path(self.config.get("recording", {}).get("storage", {}).get("recordings_dir", "data/recordings"))
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        
    async def start_server(self, host: str = "0.0.0.0", port: int = 5000):
        """Start the server to receive video streams."""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen(5)
            self.logger.info(f"Server listening on {host}:{port}")
            
            while True:
                client_socket, address = server_socket.accept()
                self.logger.info(f"Connection from {address}")
                
                # Handle client connection
                asyncio.create_task(self._handle_client(client_socket))
                
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            server_socket.close()
    
    async def _handle_client(self, client_socket: socket.socket):
        """Handle incoming client connection."""
        try:
            # Receive recording configuration
            config_data = await self._receive_data(client_socket)
            config = RecordingConfig(**json.loads(config_data))
            
            # Create output file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{config.device_name}_{timestamp}.avi"
            filepath = self.recordings_dir / filename
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*config.codec)
            out = cv2.VideoWriter(
                str(filepath),
                fourcc,
                config.fps,
                config.resolution
            )
            
            # Process incoming frames
            while True:
                frame_data = await self._receive_data(client_socket)
                if not frame_data:
                    break
                
                # Decompress and decode frame
                frame = self._decode_frame(frame_data)
                
                # Write frame to video file
                out.write(frame)
                
                # Process frame with MediaPipe if available
                if self.pose:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.pose.process(frame_rgb)
                    
                    if results.pose_landmarks:
                        metrics = self._analyze_pose(results.pose_landmarks.landmark)
                        if metrics:
                            # Send metrics back to client
                            await self._send_data(client_socket, json.dumps(metrics.__dict__))
            
            # Clean up
            out.release()
            client_socket.close()
            
            # Process the recording
            analysis = await self._process_recording(filepath)
            
            # Save analysis results
            analysis_file = filepath.with_suffix('.json')
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f)
            
            self.logger.info(f"Recording completed: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error handling client: {e}")
            client_socket.close()
    
    async def _receive_data(self, client_socket: socket.socket) -> Optional[bytes]:
        """Receive data from client."""
        try:
            # Receive data size
            size_data = client_socket.recv(4)
            if not size_data:
                return None
            
            size = struct.unpack('!I', size_data)[0]
            
            # Receive compressed data
            data = b''
            while len(data) < size:
                chunk = client_socket.recv(size - len(data))
                if not chunk:
                    return None
                data += chunk
            
            # Decompress data
            return zlib.decompress(data)
            
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            return None
    
    async def _send_data(self, client_socket: socket.socket, data: str):
        """Send data to client."""
        try:
            # Compress data
            compressed_data = zlib.compress(data.encode())
            
            # Send data size
            client_socket.send(struct.pack('!I', len(compressed_data)))
            
            # Send compressed data
            client_socket.send(compressed_data)
            
        except Exception as e:
            self.logger.error(f"Error sending data: {e}")
    
    def _decode_frame(self, frame_data: bytes) -> np.ndarray:
        """Decode frame data."""
        try:
            # Decompress frame data
            decompressed = zlib.decompress(frame_data)
            
            # Convert to numpy array
            frame = pickle.loads(decompressed)
            return frame
            
        except Exception as e:
            self.logger.error(f"Error decoding frame: {e}")
            return None
    
    def _analyze_pose(self, landmarks) -> Optional[Dict]:
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
            
            return {
                'shoulder_alignment': float(shoulder_alignment),
                'back_straightness': float(back_straightness),
                'head_position': float(head_position),
                'neck_angle': float(neck_angle),
                'confidence': float(confidence),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing pose: {e}")
            return None
    
    async def _process_recording(self, filepath: Path) -> Dict:
        """Process a completed recording and generate analysis."""
        try:
            # Open video file
            cap = cv2.VideoCapture(str(filepath))
            if not cap.isOpened():
                return {"error": "Failed to open video file"}
            
            # Process frames
            metrics = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame with MediaPipe
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(frame_rgb)
                
                if results.pose_landmarks:
                    frame_metrics = self._analyze_pose(results.pose_landmarks.landmark)
                    if frame_metrics:
                        metrics.append(frame_metrics)
            
            cap.release()
            
            # Calculate summary statistics
            if metrics:
                summary = {
                    'average_shoulder_alignment': np.mean([m['shoulder_alignment'] for m in metrics]),
                    'average_back_straightness': np.mean([m['back_straightness'] for m in metrics]),
                    'average_head_position': np.mean([m['head_position'] for m in metrics]),
                    'average_neck_angle': np.mean([m['neck_angle'] for m in metrics]),
                    'average_confidence': np.mean([m['confidence'] for m in metrics]),
                    'total_frames_analyzed': len(metrics)
                }
            else:
                summary = {
                    'error': 'No valid metrics collected',
                    'total_frames_analyzed': 0
                }
            
            return {
                'filepath': str(filepath),
                'metrics': metrics,
                'summary': summary,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing recording: {e}")
            return {'error': str(e)}
    
    def _calculate_shoulder_alignment(self, landmarks) -> float:
        """Calculate shoulder alignment score."""
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        
        # Calculate vertical difference
        vertical_diff = abs(left_shoulder.y - right_shoulder.y)
        return 1.0 - min(1.0, vertical_diff * 10)
    
    def _calculate_back_straightness(self, landmarks) -> float:
        """Calculate back straightness score."""
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
        
        # Calculate shoulder and hip line angles
        shoulder_angle = abs(np.arctan2(right_shoulder.y - left_shoulder.y,
                                      right_shoulder.x - left_shoulder.x))
        hip_angle = abs(np.arctan2(right_hip.y - left_hip.y,
                                 right_hip.x - left_hip.x))
        
        # Calculate deviation from vertical
        angle_diff = abs(shoulder_angle - hip_angle)
        return 1.0 - min(1.0, angle_diff / (np.pi / 2))
    
    def _calculate_head_position(self, landmarks) -> float:
        """Calculate head position score."""
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
        left_ear = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value]
        right_ear = landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value]
        
        # Calculate head tilt
        ear_angle = abs(np.arctan2(right_ear.y - left_ear.y,
                                 right_ear.x - left_ear.x))
        
        # Calculate forward/backward tilt
        nose_forward = nose.z - (left_ear.z + right_ear.z) / 2
        
        # Combine scores
        tilt_score = 1.0 - min(1.0, ear_angle / (np.pi / 4))
        forward_score = 1.0 - min(1.0, abs(nose_forward) * 2)
        
        return (tilt_score + forward_score) / 2
    
    def _calculate_neck_angle(self, landmarks) -> float:
        """Calculate neck angle score."""
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
        left_ear = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value]
        right_ear = landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value]
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        
        # Calculate ear midpoint
        ear_midpoint = {
            'x': (left_ear.x + right_ear.x) / 2,
            'y': (left_ear.y + right_ear.y) / 2,
            'z': (left_ear.z + right_ear.z) / 2
        }
        
        # Calculate shoulder midpoint
        shoulder_midpoint = {
            'x': (left_shoulder.x + right_shoulder.x) / 2,
            'y': (left_shoulder.y + right_shoulder.y) / 2,
            'z': (left_shoulder.z + right_shoulder.z) / 2
        }
        
        # Calculate neck angle
        neck_vector = {
            'x': ear_midpoint['x'] - shoulder_midpoint['x'],
            'y': ear_midpoint['y'] - shoulder_midpoint['y'],
            'z': ear_midpoint['z'] - shoulder_midpoint['z']
        }
        
        # Calculate angle from vertical
        vertical_angle = abs(np.arctan2(neck_vector['x'],
                                      neck_vector['y']))
        
        return 1.0 - min(1.0, vertical_angle / (np.pi / 4)) 