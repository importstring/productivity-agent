"""Question recorder for handling verbal responses and daily reflections."""

from typing import Dict, Optional, List
import logging
from pathlib import Path
import json
import cv2
import numpy as np
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment
import librosa
import soundfile as sf
import asyncio
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import ollama
import threading
import queue
import time
import os
import pyaudio
import wave
import random

# Add test mode flag
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"

class OllamaClient:
    def __init__(self, model: str = "2.1b"):
        self.model = model
    def query(self, prompt: str) -> str:
        response = self.ollama.generate(model=self.model, prompt=prompt)
        return response['response']

class QuestionRecorder:
    """Records and analyzes verbal responses to questions and daily reflections."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("QuestionRecorder")
        self.recording_dir = Path("data/recordings")
        self.responses_dir = Path("data/responses")
        self.analysis_dir = Path("data/analysis")
        self.ollama = OllamaClient()
        # Create necessary directories
        for directory in [self.recording_dir, self.responses_dir, self.analysis_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize recording state
        self.is_recording = False
        self.current_recording = None
        self.frame_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        
        # Initialize ollama
        self.ollama = ollama.Client()

        # Email configuration
        self.email_config = self.config.get("email", {})
        self.default_recipient = "communication.analysis@yahoo.com"
        
        # Maximum recording duration (5 minutes)
        self.max_duration = 300
    
    async def start_recording(self, session_id: str) -> Dict:
        """Start recording a response."""
        try:
            self.logger.info(f"Starting recording session: {session_id}")
            
            # In test mode, simulate starting a recording
            if TEST_MODE:
                self.logger.info("TEST MODE: Simulating start of recording")
                self.is_recording = True
                self.current_recording = {
                    'session_id': session_id,
                    'start_time': datetime.now().isoformat(),
                    'metrics': []
                }
                return {
                    "status": "success",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
                
            # Initialize video capture
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise RuntimeError("Failed to open camera")
            
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Get actual camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            # Create unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = self.recording_dir / f"response_{session_id}_{timestamp}.mp4"
            audio_path = self.recording_dir / f"response_{session_id}_{timestamp}.wav"
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                str(video_path),
                fourcc,
                fps,
                (width, height)
            )
            
            # Initialize audio recording
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
                'start_time': datetime.now().isoformat(),
                'audio_frames': [],
                'metrics': []
            }
            
            # Start recording threads
            self.is_recording = True
            threading.Thread(target=self._recording_thread).start()
            threading.Thread(target=self._audio_thread).start()
            
            return {
                "status": "success",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            return {"error": str(e)}
    
    async def stop_recording(self) -> Dict:
        """Stop recording and save the response."""
        try:
            if not self.current_recording:
                return {"error": "No active recording session"}
            
            self.logger.info(f"Stopping recording session: {self.current_recording['session_id']}")
            
            # In test mode, simulate stopping a recording
            if TEST_MODE:
                self.logger.info("TEST MODE: Simulating stop of recording")
                self.is_recording = False
                
                # Generate mock data for the session
                recordings_dir = Path("data/recordings")
                recordings_dir.mkdir(parents=True, exist_ok=True)
                
                video_path = recordings_dir / f"{self.current_recording['session_id']}_video.mp4"
                audio_path = recordings_dir / f"{self.current_recording['session_id']}_audio.wav"
                
                # Create empty files to simulate recording
                with open(video_path, 'w') as f:
                    f.write("Mock video file")
                    
                with open(audio_path, 'w') as f:
                    f.write("Mock audio file")
                
                result = {
                    "status": "success",
                    "session_id": self.current_recording['session_id'],
                    "end_time": datetime.now().isoformat(),
                    "filepath": str(recordings_dir / f"{self.current_recording['session_id']}.json"),
                    "video_path": str(video_path),
                    "audio_path": str(audio_path),
                    "metrics": self._generate_mock_metrics()
                }
                
                # Save mock results to file
                with open(recordings_dir / f"{self.current_recording['session_id']}.json", 'w') as f:
                    json.dump(result, f, indent=2)
                
                self.current_recording = None
                return result
                
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
            
            # Process recording
            analysis = await self.analyze_video(str(self.current_recording['video_path']))
            
            return {
                "status": "success",
                "session_id": self.current_recording['session_id'],
                "end_time": datetime.now().isoformat(),
                "filepath": f"data/recordings/{self.current_recording['session_id']}.json",
                "analysis": analysis
            }
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {e}")
            self.is_recording = False
            self.current_recording = None
            return {"error": str(e)}
    
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
            
            # Check duration
            if time.time() - datetime.fromisoformat(self.current_recording['start_time']).timestamp() >= self.max_duration:
                self.is_recording = False
                break
    
    def _audio_thread(self):
        """Thread for recording audio."""
        while self.is_recording:
            try:
                data = self.current_recording['stream'].read(1024)
                self.current_recording['audio_frames'].append(data)
                self.audio_queue.put(data)
            except Exception as e:
                self.logger.error(f"Error recording audio: {e}")
                break
    
    async def send_email_with_video(self, recipient_email: str = None, video_path: str = None, questions: List[str] = None) -> Dict:
        """Send an email with the video attachment and generated questions."""
        try:
            # Use default recipient if none provided
            recipient_email = recipient_email or self.default_recipient
            
            # Create email message
            message = MIMEMultipart()
            message["From"] = self.email_config.get("sender_email")
            message["To"] = recipient_email
            message["Subject"] = "Your Recorded Video and Questions"
            
            # Prepare email body with questions
            body = "Here is your recorded video and some questions based on your content:\n\n"
            for i, question in enumerate(questions, 1):
                body += f"{i}. {question}\n"
            body += "\n\nPlease review the video and consider these questions."
            
            message.attach(MIMEText(body, "plain"))
            
            # Attach the video file
            with open(video_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={Path(video_path).name}"
            )
            message.attach(part)
            
            # Send the email
            await aiosmtplib.send(
                message,
                hostname=self.email_config.get("smtp_server"),
                port=self.email_config.get("smtp_port"),
                username=self.email_config.get("smtp_username"),
                password=self.email_config.get("smtp_password"),
                use_tls=True
            )
            
            return {"status": "success", "recipient": recipient_email}
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return {"error": str(e)}
    
    async def generate_questions(self, transcription: str) -> Dict:
        """Generate questions based on the transcribed content."""
        try:
            # Call the Ollama API to generate questions
            response = self.ollama.query(
                prompt=f"Generate questions based on this transcript: {transcription}"
            )
            
            # Extract and process the questions
            questions_text = response.choices[0].message.content
            questions = []
            
            # Parse numbered questions
            for line in questions_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() and line[1:3] in ['. ', '- ', ') ']):
                    questions.append(line[3:].strip())
                elif line and line.startswith('Question'):
                    questions.append(line.split(':', 1)[1].strip())
            
            return {"status": "success", "questions": questions}
        except Exception as e:
            self.logger.error(f"Question generation failed: {e}")
            return {"error": str(e)}
    
    async def schedule_overnight_processing(self, tasks: List[Dict]) -> Dict:
        """Schedule tasks to run overnight."""
        try:
            results = []
            for task in tasks:
                # Schedule execution time (default to 9 PM if not specified)
                execution_time = task.get("execution_time", "21:00")
                
                # Calculate delay until execution time
                now = datetime.now()
                target_time = datetime.strptime(execution_time, "%H:%M").time()
                target_datetime = datetime.combine(now.date(), target_time)
                
                # If target time is earlier today, schedule for tomorrow
                if target_datetime < now:
                    target_datetime = datetime.combine(now.date().replace(day=now.day + 1), target_time)
                
                # Calculate delay in seconds
                delay_seconds = (target_datetime - now).total_seconds()
                
                # Schedule the task
                asyncio.create_task(self._execute_delayed_task(
                    task.get("type"),
                    task.get("session_id"),
                    task.get("recipient_email"),
                    delay_seconds
                ))
                
                results.append({
                    "task_type": task.get("type"),
                    "scheduled_time": target_datetime.isoformat()
                })
            
            return {"status": "success", "scheduled_tasks": results}
        except Exception as e:
            self.logger.error(f"Failed to schedule tasks: {e}")
            return {"error": str(e)}
    
    async def _execute_delayed_task(self, task_type: str, session_id: str, recipient_email: str = None, delay_seconds: float = 0):
        """Execute a task after the specified delay."""
        try:
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)
            
            if task_type == "video_response":
                # Start recording
                recording_result = await self.start_recording(session_id)
                if "error" in recording_result:
                    self.logger.error(f"Recording failed: {recording_result['error']}")
                    return
                
                # Wait for recording to complete (max 5 minutes)
                await asyncio.sleep(self.max_duration + 5)
                
                # Stop recording and get analysis
                stop_result = await self.stop_recording()
                if "error" in stop_result:
                    self.logger.error(f"Stop recording failed: {stop_result['error']}")
                    return
                
                # Generate questions from transcription
                questions_result = await self.generate_questions(stop_result["analysis"]["audio_analysis"]["transcript"])
                if "error" in questions_result:
                    self.logger.error(f"Question generation failed: {questions_result['error']}")
                    return
                
                # Send email with video and questions
                email_result = await self.send_email_with_video(
                    recipient_email,
                    str(self.current_recording['video_path']),
                    questions_result["questions"]
                )
                
                if "error" in email_result:
                    self.logger.error(f"Email sending failed: {email_result['error']}")
                    return
                
                self.logger.info(f"Successfully completed video response task for session {session_id}")
                
        except Exception as e:
            self.logger.error(f"Delayed execution failed: {e}")
    
    async def get_realtime_metrics(self) -> Optional[Dict]:
        """Get real-time metrics during recording."""
        try:
            if not self.is_recording:
                return None
                
            # In test mode, generate random metrics
            if TEST_MODE:
                return self._generate_mock_realtime_metrics()
                
            # TODO: Implement actual real-time metrics collection
            # This would include analyzing the current frame and audio
            
            # Placeholder for actual implementation
            return {
                "timestamp": datetime.now().isoformat(),
                "posture": {
                    "shoulder_alignment": 0.85,
                    "back_straightness": 0.78,
                    "head_position": 0.82
                },
                "speech": {
                    "volume": 0.75,
                    "clarity": 0.82,
                    "speaking_rate": 145.3
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {e}")
            return None
    
    def _generate_mock_metrics(self) -> List[Dict]:
        """Generate mock metrics for testing."""
        metrics = []
        
        # Generate 10 timepoints with random metrics
        start_time = datetime.now()
        for i in range(10):
            timestamp = start_time.timestamp() + i * 30  # 30 seconds apart
            metrics.append({
                "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
                "posture": {
                    "shoulder_alignment": round(random.uniform(0.7, 0.95), 2),
                    "back_straightness": round(random.uniform(0.75, 0.95), 2),
                    "head_position": round(random.uniform(0.7, 0.9), 2),
                    "neck_angle": round(random.uniform(0.7, 0.9), 2)
                },
                "speech": {
                    "volume": round(random.uniform(0.7, 0.9), 2),
                    "clarity": round(random.uniform(0.75, 0.95), 2),
                    "speaking_rate": round(random.uniform(120, 160), 1),
                    "pitch_variance": round(random.uniform(0.6, 0.85), 2)
                },
                "engagement": {
                    "eye_contact": round(random.uniform(0.65, 0.9), 2),
                    "facial_expression": round(random.uniform(0.7, 0.9), 2),
                    "hand_gestures": round(random.uniform(0.6, 0.85), 2)
                },
                "content": {
                    "relevance": round(random.uniform(0.8, 0.98), 2),
                    "structure": round(random.uniform(0.75, 0.95), 2),
                    "conciseness": round(random.uniform(0.7, 0.9), 2),
                    "word_choice": round(random.uniform(0.75, 0.95), 2)
                }
            })
            
        return metrics
    
    def _generate_mock_realtime_metrics(self) -> Dict:
        """Generate mock real-time metrics for testing."""
        return {
            "timestamp": datetime.now().isoformat(),
            "posture": {
                "shoulder_alignment": round(random.uniform(0.7, 0.95), 2),
                "back_straightness": round(random.uniform(0.75, 0.95), 2),
                "head_position": round(random.uniform(0.7, 0.9), 2)
            },
            "speech": {
                "volume": round(random.uniform(0.7, 0.9), 2),
                "clarity": round(random.uniform(0.75, 0.95), 2),
                "speaking_rate": round(random.uniform(120, 160), 1)
            },
            "engagement": {
                "eye_contact": round(random.uniform(0.65, 0.9), 2),
                "facial_expression": round(random.uniform(0.7, 0.9), 2)
            },
            "content": {
                "relevance": round(random.uniform(0.8, 0.98), 2),
                "word_choice": round(random.uniform(0.75, 0.95), 2)
            }
        }
    
    async def process_daily_reflection(self, text: str, date: str) -> Dict:
        """Process daily reflection text."""
        try:
            reflection_file = self.responses_dir / f"reflection_{date}.json"
            
            reflection = {
                "timestamp": datetime.now().isoformat(),
                "text": text,
                "analysis": {
                    "key_points": self._extract_key_points(text),
                    "sentiment": self._analyze_sentiment(text),
                    "action_items": self._extract_action_items(text),
                    "concerns": self._extract_concerns(text)
                }
            }
            
            with open(reflection_file, 'w') as f:
                json.dump(reflection, f, indent=2)
            
            return {"status": "success", "file": str(reflection_file)}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def analyze_video(self, video_path: str) -> Dict:
        """Analyze video recording for posture, tone, and engagement."""
        try:
            # Extract audio from video
            audio_path = Path(video_path).with_suffix('.wav')
            self._extract_audio(video_path, str(audio_path))
            
            # Analyze audio
            audio_analysis = self._analyze_audio(str(audio_path))
            
            # Analyze video frames
            video_analysis = self._analyze_video_frames(video_path)
            
            # Combine analyses
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "audio_analysis": audio_analysis,
                "video_analysis": video_analysis,
                "combined_metrics": self._combine_metrics(audio_analysis, video_analysis)
            }
            
            # Save analysis
            analysis_file = Path(video_path).with_suffix('.analysis.json')
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            return {"status": "success", "file": str(analysis_file)}
            
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_audio(self, video_path: str, audio_path: str) -> None:
        """Extract audio from video file."""
        video = AudioSegment.from_file(video_path, format="mp4")
        video.export(audio_path, format="wav")
    
    def _analyze_audio(self, audio_path: str) -> Dict:
        """Analyze audio for tone, pitch, and speech patterns."""
        # Load audio file
        y, sr = librosa.load(audio_path)
        
        # Extract features
        pitch = librosa.yin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        return {
            "tone": {
                "pitch_mean": float(np.mean(pitch)),
                "pitch_std": float(np.std(pitch)),
                "tempo": float(tempo)
            },
            "speech_metrics": {
                "pace": self._calculate_speech_pace(y, sr),
                "energy": float(np.mean(librosa.feature.rms(y=y))),
                "clarity": self._calculate_speech_clarity(mfcc)
            },
            "transcript": self._generate_transcript(audio_path)
        }
    
    def _analyze_video_frames(self, video_path: str) -> Dict:
        """Analyze video frames for posture and engagement."""
        cap = cv2.VideoCapture(video_path)
        frame_metrics = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Analyze frame
            frame_metrics.append(self._analyze_frame(frame))
        
        cap.release()
        
        return {
            "frame_metrics": frame_metrics,
            "summary": self._summarize_frame_metrics(frame_metrics)
        }
    
    def _analyze_frame(self, frame: np.ndarray) -> Dict:
        """Analyze a single frame for posture and engagement."""
        # Add your frame analysis logic here
        return {}
    
    def _calculate_speech_pace(self, y: np.ndarray, sr: int) -> float:
        """Calculate speech pace."""
        # Add your speech pace calculation logic here
        return 0.0
    
    def _calculate_speech_clarity(self, mfcc: np.ndarray) -> float:
        """Calculate speech clarity score."""
        # Add your speech clarity calculation logic here
        return 0.0
    
    def _generate_transcript(self, audio_path: str) -> str:
        """Generate transcript from audio."""
        try:
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
                return self.recognizer.recognize_google(audio)
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return ""
    
    def _combine_metrics(self, audio_analysis: Dict, video_analysis: Dict) -> Dict:
        """Combine audio and video metrics for overall analysis."""
        return {
            "engagement_score": self._calculate_engagement(audio_analysis, video_analysis),
            "communication_effectiveness": self._calculate_effectiveness(audio_analysis, video_analysis)
        }
    
    def _calculate_engagement(self, audio_analysis: Dict, video_analysis: Dict) -> float:
        """Calculate overall engagement score."""
        # Add your engagement calculation logic here
        return 0.0
    
    def _calculate_effectiveness(self, audio_analysis: Dict, video_analysis: Dict) -> float:
        """Calculate communication effectiveness score."""
        # Add your effectiveness calculation logic here
        return 0.0
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from reflection text."""
        # Add your key points extraction logic here
        return []
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of reflection text."""
        # Add your sentiment analysis logic here
        return {}
    
    def _extract_action_items(self, text: str) -> List[str]:
        """Extract action items from reflection text."""
        # Add your action items extraction logic here
        return []
    
    def _extract_concerns(self, text: str) -> List[str]:
        """Extract concerns from reflection text."""
        # Add your concerns extraction logic here
        return []
    
    def _summarize_frame_metrics(self, metrics: List[Dict]) -> Dict:
        """Summarize frame metrics into overall scores."""
        # Add your summarization logic here
        return {} 