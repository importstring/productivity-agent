"""
Question recording and response analysis utilities.
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
import speech_recognition as sr
from pydub import AudioSegment
import wave
import io

@dataclass
class ResponseMetrics:
    """Data class for storing response metrics."""
    confidence: float
    speaking_rate: float
    clarity: float
    engagement: float
    timestamp: str
    audio_quality: float

class QuestionRecorder:
    """Manages recording and analysis of question responses."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("QuestionRecorder")
        
        # Initialize MediaPipe
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Recording state
        self.is_recording = False
        self.current_recording = None
        self.frame_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        self.analysis_queue = queue.Queue()
        
        # Create necessary directories
        self.responses_dir = Path("data/responses")
        self.responses_dir.mkdir(parents=True, exist_ok=True)
        
    async def start_recording(self, question_id: str) -> Dict:
        """Start a new response recording session."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = f"q_{question_id}_{timestamp}"
            
            # Initialize video capture
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise RuntimeError("Failed to open camera")
            
            # Get camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_path = self.responses_dir / f"{session_id}.mp4"
            out = cv2.VideoWriter(
                str(video_path),
                fourcc,
                fps,
                (width, height)
            )
            
            # Initialize audio recording
            audio_path = self.responses_dir / f"{session_id}.wav"
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024
            )
            
            self.current_recording = {
                'cap': cap,
                'writer': out,
                'video_path': video_path,
                'audio': audio,
                'stream': stream,
                'audio_path': audio_path,
                'session_id': session_id,
                'start_time': datetime.now().isoformat()
            }
            
            # Start recording and analysis threads
            self.is_recording = True
            threading.Thread(target=self._recording_thread).start()
            threading.Thread(target=self._audio_thread).start()
            threading.Thread(target=self._analysis_thread).start()
            
            return {
                'status': 'success',
                'session_id': session_id,
                'video_path': str(video_path),
                'audio_path': str(audio_path)
            }
            
        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
            return {'error': str(e)}
    
    async def stop_recording(self) -> Dict:
        """Stop the current recording session."""
        try:
            if not self.current_recording:
                return {'error': 'No active recording session'}
            
            self.is_recording = False
            
            # Release resources
            self.current_recording['cap'].release()
            self.current_recording['writer'].release()
            self.current_recording['stream'].stop_stream()
            self.current_recording['stream'].close()
            self.current_recording['audio'].terminate()
            
            # Save audio data
            with wave.open(str(self.current_recording['audio_path']), 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(4)  # 4 bytes for float32
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.current_recording['audio_frames']))
            
            # Process final analysis
            analysis = await self._process_recording(
                self.current_recording['video_path'],
                self.current_recording['audio_path']
            )
            
            # Save analysis results
            analysis_file = self.current_recording['video_path'].with_suffix('.json')
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f)
            
            return {
                'status': 'success',
                'session_id': self.current_recording['session_id'],
                'analysis_file': str(analysis_file)
            }
            
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
            return {'error': str(e)}
    
    def _recording_thread(self):
        """Thread for capturing and recording video frames."""
        while self.is_recording:
            ret, frame = self.current_recording['cap'].read()
            if not ret:
                break
            
            # Add frame to queue for analysis
            self.frame_queue.put(frame)
            
            # Write frame to video file
            self.current_recording['writer'].write(frame)
    
    def _audio_thread(self):
        """Thread for recording audio."""
        self.current_recording['audio_frames'] = []
        
        while self.is_recording:
            try:
                data = self.current_recording['stream'].read(1024)
                self.current_recording['audio_frames'].append(data)
                self.audio_queue.put(data)
            except Exception as e:
                self.logger.error(f"Error recording audio: {e}")
                break
    
    def _analysis_thread(self):
        """Thread for analyzing responses in real-time."""
        while self.is_recording:
            try:
                # Get latest frame and audio data
                frame = self.frame_queue.get(timeout=1)
                audio_data = self.audio_queue.get(timeout=1)
                
                # Analyze frame
                frame_metrics = self._analyze_frame(frame)
                
                # Analyze audio
                audio_metrics = self._analyze_audio(audio_data)
                
                # Combine metrics
                if frame_metrics and audio_metrics:
                    combined_metrics = ResponseMetrics(
                        confidence=frame_metrics['confidence'],
                        speaking_rate=audio_metrics['speaking_rate'],
                        clarity=audio_metrics['clarity'],
                        engagement=frame_metrics['engagement'],
                        timestamp=datetime.now().isoformat(),
                        audio_quality=audio_metrics['quality']
                    )
                    self.analysis_queue.put(combined_metrics)
                    
            except queue.Empty:
                continue
    
    def _analyze_frame(self, frame: np.ndarray) -> Optional[Dict]:
        """Analyze a single frame for facial metrics."""
        try:
            # Convert frame to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(frame_rgb)
            
            if not results.multi_face_landmarks:
                return None
            
            # Get face landmarks
            landmarks = results.multi_face_landmarks[0]
            
            # Calculate metrics
            confidence = self._calculate_face_confidence(landmarks)
            engagement = self._calculate_engagement(landmarks)
            
            return {
                'confidence': confidence,
                'engagement': engagement
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing frame: {e}")
            return None
    
    def _analyze_audio(self, audio_data: bytes) -> Optional[Dict]:
        """Analyze audio data for speech metrics."""
        try:
            # Convert audio data to AudioSegment
            audio = AudioSegment.from_raw(
                io.BytesIO(audio_data),
                sample_width=4,
                frame_rate=44100,
                channels=1
            )
            
            # Calculate metrics
            speaking_rate = self._calculate_speaking_rate(audio)
            clarity = self._calculate_clarity(audio)
            quality = self._calculate_audio_quality(audio)
            
            return {
                'speaking_rate': speaking_rate,
                'clarity': clarity,
                'quality': quality
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing audio: {e}")
            return None
    
    def _calculate_face_confidence(self, landmarks) -> float:
        """Calculate face detection confidence."""
        # Use visibility of key facial landmarks
        key_points = [
            self.mp_face.FACEMESH_NOSE,
            self.mp_face.FACEMESH_LEFT_EYE,
            self.mp_face.FACEMESH_RIGHT_EYE,
            self.mp_face.FACEMESH_MOUTH
        ]
        
        visibility_scores = []
        for point in key_points:
            visibility_scores.append(landmarks.landmark[point].visibility)
        
        return np.mean(visibility_scores)
    
    def _calculate_engagement(self, landmarks) -> float:
        """Calculate engagement level from facial expressions."""
        # Analyze mouth openness
        mouth_top = landmarks.landmark[self.mp_face.FACEMESH_MOUTH].landmark[0]
        mouth_bottom = landmarks.landmark[self.mp_face.FACEMESH_MOUTH].landmark[1]
        mouth_openness = abs(mouth_top.y - mouth_bottom.y)
        
        # Analyze eye openness
        left_eye = landmarks.landmark[self.mp_face.FACEMESH_LEFT_EYE].landmark
        right_eye = landmarks.landmark[self.mp_face.FACEMESH_RIGHT_EYE].landmark
        
        eye_openness = (
            abs(left_eye[1].y - left_eye[4].y) +
            abs(right_eye[1].y - right_eye[4].y)
        ) / 2
        
        # Combine metrics
        return (mouth_openness + eye_openness) / 2
    
    def _calculate_speaking_rate(self, audio: AudioSegment) -> float:
        """Calculate speaking rate from audio."""
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples())
        
        # Calculate energy envelope
        energy = np.abs(samples)
        threshold = np.mean(energy) * 1.5
        
        # Count speech segments
        speech_segments = np.where(energy > threshold)[0]
        if len(speech_segments) == 0:
            return 0.0
        
        # Calculate average segment duration
        segment_durations = np.diff(speech_segments)
        return np.mean(segment_durations) / audio.frame_rate
    
    def _calculate_clarity(self, audio: AudioSegment) -> float:
        """Calculate speech clarity from audio."""
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples())
        
        # Calculate signal-to-noise ratio
        signal = samples[np.abs(samples) > np.mean(np.abs(samples))]
        noise = samples[np.abs(samples) <= np.mean(np.abs(samples))]
        
        if len(noise) == 0:
            return 1.0
        
        snr = np.mean(np.abs(signal)) / np.mean(np.abs(noise))
        return min(1.0, snr / 10.0)  # Normalize to 0-1
    
    def _calculate_audio_quality(self, audio: AudioSegment) -> float:
        """Calculate overall audio quality."""
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples())
        
        # Calculate dynamic range
        dynamic_range = np.max(np.abs(samples)) - np.min(np.abs(samples))
        
        # Calculate signal-to-noise ratio
        signal = samples[np.abs(samples) > np.mean(np.abs(samples))]
        noise = samples[np.abs(samples) <= np.mean(np.abs(samples))]
        
        if len(noise) == 0:
            return 1.0
        
        snr = np.mean(np.abs(signal)) / np.mean(np.abs(noise))
        
        # Combine metrics
        return (dynamic_range + snr) / 2
    
    async def _process_recording(self, video_path: Path, audio_path: Path) -> Dict:
        """Process a completed recording and generate analysis."""
        try:
            # Collect all metrics from analysis queue
            metrics = []
            while not self.analysis_queue.empty():
                metric = self.analysis_queue.get_nowait()
                if metric:
                    metrics.append(metric.__dict__)
            
            # Calculate summary statistics
            if metrics:
                summary = {
                    'average_confidence': np.mean([m['confidence'] for m in metrics]),
                    'average_speaking_rate': np.mean([m['speaking_rate'] for m in metrics]),
                    'average_clarity': np.mean([m['clarity'] for m in metrics]),
                    'average_engagement': np.mean([m['engagement'] for m in metrics]),
                    'average_audio_quality': np.mean([m['audio_quality'] for m in metrics]),
                    'total_frames_analyzed': len(metrics)
                }
            else:
                summary = {
                    'error': 'No valid metrics collected',
                    'total_frames_analyzed': 0
                }
            
            return {
                'video_path': str(video_path),
                'audio_path': str(audio_path),
                'metrics': metrics,
                'summary': summary,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing recording: {e}")
            return {'error': str(e)}
    
    async def get_realtime_metrics(self) -> Optional[ResponseMetrics]:
        """Get the most recent response metrics."""
        try:
            return self.analysis_queue.get_nowait()
        except queue.Empty:
            return None 