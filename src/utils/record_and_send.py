"""
Simple script to record and send videos via email.
"""

import cv2
import numpy as np
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from pathlib import Path
import os
import time
from typing import Dict

# Email provider configurations
EMAIL_PROVIDERS = {
    'yahoo': {
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 465,  # Using SSL port for Yahoo
        'use_ssl': True
    },
    'smtp2go': {
        'smtp_server': 'mail.smtp2go.com',
        'smtp_port': 587,
        'use_ssl': False
    },
    'outlook': {
        'smtp_server': 'smtp-mail.outlook.com',
        'smtp_port': 587,
        'use_ssl': False
    }
}

class VideoRecorder:
    """Simple video recorder with email sending capability."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("VideoRecorder")
        
        # Create recordings directory
        self.output_dir = Path(config.get("output_dir", "recordings"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Email configuration
        self.email = config.get("email", {}).get("address")
        self.password = config.get("email", {}).get("password")
        self.provider = config.get("email", {}).get("provider", "yahoo").lower()
        
        if self.provider not in EMAIL_PROVIDERS:
            raise ValueError(f"Unsupported email provider: {self.provider}")
        
        provider_config = EMAIL_PROVIDERS[self.provider]
        self.smtp_server = provider_config['smtp_server']
        self.smtp_port = provider_config['smtp_port']
        self.use_ssl = provider_config.get('use_ssl', False)
        self.recipient = config.get("email", {}).get("recipient")
    
    def record_video(self, duration: int = 300):
        """Record a video for the specified duration."""
        try:
            # Initialize camera
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
            
            # Create output file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"posture_recording_{timestamp}.mp4"
            filepath = self.output_dir / filename
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                str(filepath),
                fourcc,
                fps,
                (width, height)
            )
            
            # Record video
            start_time = time.time()
            self.logger.info(f"Starting recording for {duration} seconds...")
            
            while (time.time() - start_time) < duration:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Write frame
                out.write(frame)
                
                # Show preview
                cv2.imshow('Recording...', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Clean up
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            
            self.logger.info(f"Recording saved: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error recording video: {e}")
            if 'cap' in locals():
                cap.release()
            if 'out' in locals():
                out.release()
            if 'cv2' in locals():
                cv2.destroyAllWindows()
            return None
    
    def send_video(self, filepath: Path):
        """Send video file via email."""
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = self.recipient
            msg['Subject'] = f"Posture Recording - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Add message body
            body = "Please find attached my posture recording for analysis."
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach video file
            with open(filepath, 'rb') as f:
                attachment = MIMEApplication(f.read())
                attachment.add_header('Content-Disposition', 'attachment',
                                   filename=filepath.name)
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
            
            self.logger.info(f"Video sent to {self.recipient}")
            
        except Exception as e:
            self.logger.error(f"Error sending video: {e}")

def main():
    """Main function to run the video recorder."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configuration
    config = {
        "output_dir": "recordings",
        "email": {
            "address": os.getenv("EMAIL_ADDRESS"),
            "password": os.getenv("EMAIL_PASSWORD"),
            "recipient": os.getenv("ANALYSIS_EMAIL")
        }
    }
    
    # Create recorder
    recorder = VideoRecorder(config)
    
    try:
        # Record video (5 minutes by default)
        filepath = recorder.record_video(duration=300)
        
        if filepath:
            # Send video
            recorder.send_video(filepath)
            
            print("\nRecording completed and sent for analysis.")
            print("You will receive the analysis results via email.")
        else:
            print("\nFailed to record video.")
    
    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main() 