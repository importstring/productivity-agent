"""
Email-based recording submission and analysis system.
"""

import os
import cv2
import numpy as np
import mediapipe as mp
import logging
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import imaplib
import email
from email.header import decode_header
import time

# Email provider configurations
EMAIL_PROVIDERS = {
    'yahoo': {
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 465,  # Using SSL port for Yahoo
        'imap_server': 'imap.mail.yahoo.com',
        'imap_port': 993,
        'use_ssl': True
    },
    'smtp2go': {
        'smtp_server': 'mail.smtp2go.com',
        'smtp_port': 587,
        'imap_server': 'imap.smtp2go.com',
        'imap_port': 993,
        'use_ssl': False
    },
    'outlook': {
        'smtp_server': 'smtp-mail.outlook.com',
        'smtp_port': 587,
        'imap_server': 'outlook.office365.com',
        'imap_port': 993,
        'use_ssl': False
    }
}

class EmailRecordingManager:
    """Manages recording submission via email and analysis."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("EmailRecordingManager")
        
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Create necessary directories
        self.recordings_dir = Path(config.get("recording", {}).get("storage", {}).get("recordings_dir", "data/recordings"))
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        
        # Email configuration
        self.email = config.get("email", {}).get("address")
        self.password = config.get("email", {}).get("password")
        self.provider = config.get("email", {}).get("provider", "yahoo").lower()
        
        if self.provider not in EMAIL_PROVIDERS:
            raise ValueError(f"Unsupported email provider: {self.provider}")
        
        provider_config = EMAIL_PROVIDERS[self.provider]
        self.smtp_server = provider_config['smtp_server']
        self.smtp_port = provider_config['smtp_port']
        self.imap_server = provider_config['imap_server']
        self.imap_port = provider_config['imap_port']
        self.use_ssl = provider_config.get('use_ssl', False)
        
        # Initialize email connection
        self._setup_email()
    
    def _setup_email(self):
        """Setup email connection."""
        try:
            # Connect to IMAP server
            self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.imap.login(self.email, self.password)
            self.logger.info("Email connection established")
        except Exception as e:
            self.logger.error(f"Failed to setup email: {e}")
            raise
    
    def start_monitoring(self):
        """Start monitoring email for new recordings."""
        try:
            self.logger.info("Starting email monitoring...")
            
            while True:
                # Check for new emails
                self.imap.select('INBOX')
                _, messages = self.imap.search(None, 'UNSEEN')
                
                for num in messages[0].split():
                    try:
                        # Get email message
                        _, msg_data = self.imap.fetch(num, '(RFC822)')
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        # Process email
                        self._process_email(email_message)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing email: {e}")
                
                # Wait before next check
                time.sleep(300)  # Check every 5 minutes
                
        except Exception as e:
            self.logger.error(f"Error in email monitoring: {e}")
        finally:
            self.imap.close()
            self.imap.logout()
    
    def _process_email(self, email_message):
        """Process incoming email with recording."""
        try:
            # Get sender and subject
            sender = email_message.get('from', '')
            subject = email_message.get('subject', '')
            
            # Decode subject
            subject = decode_header(subject)[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            self.logger.info(f"Processing email from {sender} with subject: {subject}")
            
            # Process attachments
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                
                if part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if filename:
                    # Decode filename
                    filename = decode_header(filename)[0][0]
                    if isinstance(filename, bytes):
                        filename = filename.decode()
                    
                    # Save attachment
                    if filename.lower().endswith(('.mp4', '.avi', '.mov')):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filepath = self.recordings_dir / f"recording_{timestamp}_{filename}"
                        
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        
                        self.logger.info(f"Saved recording: {filepath}")
                        
                        # Process recording
                        self._process_recording(filepath)
                        
                        # Send analysis results
                        self._send_analysis_results(sender, filepath)
        except Exception as e:
            self.logger.error(f"Error processing email: {e}")
            raise
    
    def _process_recording(self, filepath: Path) -> Dict:
        """Process a recording and generate analysis."""
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
                    'total_frames_analyzed': len(metrics)
                }
            else:
                summary = {
                    'error': 'No valid metrics collected',
                    'total_frames_analyzed': 0
                }
            
            # Save analysis results
            analysis_file = filepath.with_suffix('.json')
            with open(analysis_file, 'w') as f:
                json.dump({
                    'filepath': str(filepath),
                    'metrics': metrics,
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error processing recording: {e}")
            return {'error': str(e)}
    
    def _analyze_pose(self, landmarks) -> Optional[Dict]:
        """Analyze pose landmarks and calculate metrics."""
        try:
            # Calculate metrics
            shoulder_alignment = self._calculate_shoulder_alignment(landmarks)
            back_straightness = self._calculate_back_straightness(landmarks)
            head_position = self._calculate_head_position(landmarks)
            neck_angle = self._calculate_neck_angle(landmarks)
            
            return {
                'shoulder_alignment': float(shoulder_alignment),
                'back_straightness': float(back_straightness),
                'head_position': float(head_position),
                'neck_angle': float(neck_angle),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing pose: {e}")
            return None
    
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
    
    def _send_analysis_results(self, recipient: str, filepath: Path):
        """Send analysis results via email."""
        try:
            # Read analysis results
            analysis_file = filepath.with_suffix('.json')
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = recipient
            msg['Subject'] = f"Posture Analysis Results - {filepath.name}"
            
            # Create email body
            body = "Here are your posture analysis results:\n\n"
            
            # Add summary statistics
            summary = analysis['summary']
            body += "Summary Statistics:\n"
            body += f"- Average Shoulder Alignment: {summary['average_shoulder_alignment']:.2f}\n"
            body += f"- Average Back Straightness: {summary['average_back_straightness']:.2f}\n"
            body += f"- Average Head Position: {summary['average_head_position']:.2f}\n"
            body += f"- Average Neck Angle: {summary['average_neck_angle']:.2f}\n"
            body += f"- Total Frames Analyzed: {summary['total_frames_analyzed']}\n\n"
            
            # Add recommendations
            body += "Recommendations:\n"
            if summary['average_shoulder_alignment'] < 0.8:
                body += "- Focus on keeping your shoulders level\n"
            if summary['average_back_straightness'] < 0.8:
                body += "- Work on maintaining a straight back\n"
            if summary['average_head_position'] < 0.8:
                body += "- Keep your head in a neutral position\n"
            if summary['average_neck_angle'] < 0.8:
                body += "- Avoid forward head posture\n"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach analysis file
            with open(analysis_file, 'rb') as f:
                attachment = MIMEApplication(f.read())
                attachment.add_header('Content-Disposition', 'attachment',
                                   filename=analysis_file.name)
                msg.attach(attachment)
            
            # Send email using appropriate connection method
            if self.use_ssl:
                # Use SSL connection
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=ssl.create_default_context()) as server:
                    server.login(self.email, self.password)
                    server.send_message(msg)
            else:
                # Use TLS connection
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls(context=ssl.create_default_context())
                    server.login(self.email, self.password)
                    server.send_message(msg)
            
            self.logger.info(f"Analysis results sent to {recipient}")
            
        except Exception as e:
            self.logger.error(f"Error sending analysis results: {e}")

def main():
    """Main function to run the email monitoring system."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configuration
    config = {
        "recording": {
            "storage": {
                "recordings_dir": "data/recordings"
            }
        },
        "email": {
            "address": os.getenv("EMAIL_ADDRESS", "communication_analysis@yahoo.com"),
            "password": os.getenv("EMAIL_PASSWORD"),  # Must be set via environment variable
            "provider": "yahoo"
        }
    }
    
    if not config["email"]["password"]:
        logging.error("EMAIL_PASSWORD environment variable must be set")
        return
    
    # Create and start manager
    manager = EmailRecordingManager(config)
    
    try:
        logging.info(f"Starting email monitoring for {config['email']['address']}")
        manager.start_monitoring()
    except KeyboardInterrupt:
        logging.info("System stopped by user")
    except Exception as e:
        logging.error(f"System error: {e}")

if __name__ == "__main__":
    main() 