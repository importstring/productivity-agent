"""
Server-side recording utility for remote video streaming and analysis.
"""

import cv2
import numpy as np
import socket
import struct
import pickle
import zlib
import json
import logging
import mediapipe as mp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass

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

class RemoteRecordingServer:
    """Server for receiving and analyzing remote video streams."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("RemoteRecordingServer")
        
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Create necessary directories
        self.output_dir = Path(config.get("output_dir", "recordings"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize recording state
        self.current_session = None
        self.current_recording = None
        self.frame_count = 0
        self.metrics_history = []
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 5000):
        """Start the server to receive video streams."""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen(5)
            server_socket.setblocking(False)
            
            self.logger.info(f"Server started on {host}:{port}")
            
            while True:
                try:
                    client_socket, address = server_socket.accept()
                    self.logger.info(f"New connection from {address}")
                    
                    # Handle client connection
                    await self._handle_client(client_socket)
                    
                except BlockingIOError:
                    await asyncio.sleep(0.1)
                except Exception as e:
                    self.logger.error(f"Error handling client: {e}")
        
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            server_socket.close()
    
    async def _handle_client(self, client_socket: socket.socket):
        """Handle a client connection."""
        try:
            # Receive configuration
            config_data = await self._receive_data(client_socket)
            if not config_data:
                return
            
            config = RecordingConfig(**json.loads(config_data))
            
            # Initialize recording
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_session = f"session_{timestamp}"
            self.current_recording = self.output_dir / f"{self.current_session}.mp4"
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                str(self.current_recording),
                fourcc,
                config.fps,
                config.resolution
            )
            
            # Process frames
            while True:
                frame_data = await self._receive_data(client_socket)
                if not frame_data:
                    break
                
                # Decode frame
                frame = pickle.loads(frame_data)
                
                # Write frame
                out.write(frame)
                
                # Analyze pose
                metrics = self._analyze_pose(frame)
                if metrics:
                    self.metrics_history.append(metrics)
                    
                    # Send metrics back to client
                    await self._send_data(client_socket, json.dumps(metrics))
                
                self.frame_count += 1
            
            # Clean up
            out.release()
            
            # Process recording
            await self._process_recording()
            
        except Exception as e:
            self.logger.error(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
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
    
    def _analyze_pose(self, frame: np.ndarray) -> Optional[Dict]:
        """Analyze pose in frame using MediaPipe."""
        try:
            # Convert frame to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame
            results = self.pose.process(frame_rgb)
            
            if not results.pose_landmarks:
                return None
            
            # Extract landmarks
            landmarks = results.pose_landmarks.landmark
            
            # Calculate metrics
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "frame": self.frame_count,
                "shoulder_alignment": self._calculate_shoulder_alignment(landmarks),
                "back_straightness": self._calculate_back_straightness(landmarks),
                "head_position": self._calculate_head_position(landmarks),
                "neck_angle": self._calculate_neck_angle(landmarks)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing pose: {e}")
            return None
    
    def _calculate_shoulder_alignment(self, landmarks) -> float:
        """Calculate shoulder alignment score."""
        try:
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            
            # Calculate angle between shoulders
            angle = abs(left_shoulder.y - right_shoulder.y)
            return 1.0 - min(angle * 10, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating shoulder alignment: {e}")
            return 0.0
    
    def _calculate_back_straightness(self, landmarks) -> float:
        """Calculate back straightness score."""
        try:
            shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            
            # Calculate angle between shoulder and hip
            angle = abs(shoulder.x - hip.x)
            return 1.0 - min(angle * 5, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating back straightness: {e}")
            return 0.0
    
    def _calculate_head_position(self, landmarks) -> float:
        """Calculate head position score."""
        try:
            nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
            left_ear = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value]
            right_ear = landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value]
            
            # Calculate head tilt
            tilt = abs(left_ear.y - right_ear.y)
            return 1.0 - min(tilt * 10, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating head position: {e}")
            return 0.0
    
    def _calculate_neck_angle(self, landmarks) -> float:
        """Calculate neck angle score."""
        try:
            nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            
            # Calculate angle between nose and shoulder
            angle = abs(nose.x - left_shoulder.x)
            return 1.0 - min(angle * 5, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating neck angle: {e}")
            return 0.0
    
    async def _process_recording(self):
        """Process the completed recording."""
        try:
            if not self.current_recording or not self.metrics_history:
                return
            
            # Calculate summary statistics
            metrics = np.array(self.metrics_history)
            summary = {
                "session_id": self.current_session,
                "duration": self.frame_count / 30,  # Assuming 30 FPS
                "average_shoulder_alignment": np.mean(metrics[:, "shoulder_alignment"]),
                "average_back_straightness": np.mean(metrics[:, "back_straightness"]),
                "average_head_position": np.mean(metrics[:, "head_position"]),
                "average_neck_angle": np.mean(metrics[:, "neck_angle"])
            }
            
            # Save summary
            summary_file = self.output_dir / f"{self.current_session}_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.info(f"Recording processed and saved: {self.current_session}")
            
        except Exception as e:
            self.logger.error(f"Error processing recording: {e}")
        finally:
            # Reset state
            self.current_session = None
            self.current_recording = None
            self.frame_count = 0
            self.metrics_history = []

async def main():
    """Main function to run the server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configuration
    config = {
        "output_dir": "recordings",
        "server_host": "0.0.0.0",
        "server_port": 5000
    }
    
    # Create and start server
    server = RemoteRecordingServer(config)
    
    try:
        await server.start_server(config["server_host"], config["server_port"])
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 