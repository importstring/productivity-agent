# Posture Recording and Analysis System

This system allows you to record posture videos and get them analyzed automatically using email-based submission.

## Setup Instructions

### 1. Yahoo Mail Setup

The system is configured to use communication_analysis@yahoo.com. You'll need to:

1. Generate an App Password (required for security):

   - Sign in to your Yahoo account
   - Go to Account Security settings (click on your name > Account info > Account security)
   - Scroll down to "Generate app password"
   - Select "Other app" from the dropdown
   - Enter "Posture Analysis" as the app name
   - Click "Generate"
   - Copy the generated 16-character password

2. Set up environment variables:

   ```bash
   # On Windows (Command Prompt)
   set EMAIL_PASSWORD=your-16-char-app-password

   # On Mac/Linux
   export EMAIL_PASSWORD=your-16-char-app-password
   ```

### 2. Install Dependencies

1. Install Python 3.8 or higher
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Record and Send Videos

1. Run the recording script:
   ```bash
   python src/utils/record_and_send.py
   ```
2. The script will:
   - Open your camera
   - Show a preview window
   - Record for 5 minutes (or press 'q' to stop early)
   - Automatically send the recording to communication_analysis@yahoo.com
   - Save a local copy in the `recordings` directory

### 4. Analysis Server Setup

1. On your Windows computer, set up the same environment variable:
   ```bash
   set EMAIL_PASSWORD=your-16-char-app-password
   ```
2. Run the analysis server:
   ```bash
   python src/utils/email_recording.py
   ```
3. The server will:
   - Monitor communication_analysis@yahoo.com for new recordings
   - Process any received videos
   - Send back analysis results via email

## Features

- Video recording with preview
- Email-based submission and analysis
- Pose detection and analysis using MediaPipe
- Calculation of posture metrics:
  - Shoulder alignment
  - Back straightness
  - Head position
  - Neck angle
- Automatic saving of recordings and analysis summaries
- Personalized recommendations based on analysis

## Output

The system generates two types of files for each recording session:

1. Video file: `recordings/recording_YYYYMMDD_HHMMSS.mp4`
2. Analysis summary: `recordings/recording_YYYYMMDD_HHMMSS.json`

The summary file contains:

- Session duration
- Average posture metrics
- Frame-by-frame metrics history
- Personalized recommendations

## Troubleshooting

1. Email Issues:

   - Make sure you're using the App Password, not your regular Yahoo password
   - Check your Yahoo spam folder if emails aren't arriving
   - Verify that the App Password was generated correctly

2. Camera Issues:

   - Ensure the camera is not being used by another application
   - Check camera permissions on your device
   - Try restarting the recording application

3. Performance Issues:
   - Reduce the video resolution in the configuration
   - Check available disk space
   - Monitor system resources

## Security Notes

- The system uses Yahoo Mail's secure SSL/TLS protocols
- App Passwords are required for security
- Keep your App Password secure and never share it
- The system only communicates with communication_analysis@yahoo.com

## Contributing

Feel free to submit issues and enhancement requests!
