"""
Client-side recording utility for remote video streaming.
"""

import cv2
import numpy as np
import socket
import struct
import pickle
import zlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional
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

class RemoteRecorderClient:
    """Client for remote video recording and streaming."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("RemoteRecorderClient")
        
        # Initialize camera
        self.cap = None
        self.is_recording = False
        
        # Create necessary directories
        self.output_dir = Path(config.get("output_dir", "recordings"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def start_recording(self, server_host: str, server_port: int = 5000):
        """Start recording and streaming to server."""
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise RuntimeError("Failed to open camera")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Get actual camera properties
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            # Create recording configuration
            config = RecordingConfig(
                device_name="remote_device",
                resolution=(width, height),
                fps=fps,
                codec="MJPG",
                output_dir=str(self.output_dir),
                server_host=server_host,
                server_port=server_port
            )
            
            # Connect to server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_host, server_port))
            
            # Send configuration
            await self._send_data(client_socket, json.dumps(config.__dict__))
            
            # Start recording loop
            self.is_recording = True
            while self.is_recording:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Encode and send frame
                await self._send_data(client_socket, self._encode_frame(frame))
                
                # Receive metrics if available
                metrics = await self._receive_data(client_socket)
                if metrics:
                    self.logger.info(f"Received metrics: {metrics}")
            
            # Clean up
            client_socket.close()
            self.cap.release()
            
        except Exception as e:
            self.logger.error(f"Error in recording: {e}")
            if self.cap:
                self.cap.release()
    
    def stop_recording(self):
        """Stop the recording session."""
        self.is_recording = False
    
    async def _send_data(self, client_socket: socket.socket, data: bytes):
        """Send data to server."""
        try:
            # Compress data
            compressed_data = zlib.compress(data)
            
            # Send data size
            client_socket.send(struct.pack('!I', len(compressed_data)))
            
            # Send compressed data
            client_socket.send(compressed_data)
            
        except Exception as e:
            self.logger.error(f"Error sending data: {e}")
    
    async def _receive_data(self, client_socket: socket.socket) -> Optional[str]:
        """Receive data from server."""
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
            return zlib.decompress(data).decode()
            
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            return None
    
    def _encode_frame(self, frame: np.ndarray) -> bytes:
        """Encode frame for transmission."""
        try:
            # Convert frame to bytes
            return pickle.dumps(frame)
            
        except Exception as e:
            self.logger.error(f"Error encoding frame: {e}")
            return None

async def main():
    """Main function to run the client."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configuration
    config = {
        "output_dir": "recordings",
        "server_host": "YOUR_WINDOWS_IP",  # Replace with your Windows computer's IP
        "server_port": 5000
    }
    
    # Create and start recorder
    recorder = RemoteRecorderClient(config)
    
    try:
        await recorder.start_recording(config["server_host"], config["server_port"])
    except KeyboardInterrupt:
        recorder.stop_recording()
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 