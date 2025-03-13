# Posture Recording and Analysis System

This system allows you to record posture videos and get them analyzed automatically. You can either record and send videos via email, or use the real-time streaming system.

## Email-Based Recording (Recommended)

This is the simplest way to use the system. You record a video on your phone/MacBook, send it via email, and receive the analysis results back via email.

### Email Provider Setup

You can use any of the following email providers:

1. SMTP2GO (Recommended)

   - Sign up for a free account at [smtp2go.com](https://smtp2go.com)
   - Get up to 1,000 emails per month free
   - Excellent deliverability (96%)
   - Easy setup process:
     1. Create an account
     2. Go to Settings > API Keys
     3. Generate a new API key
     4. Use this as your password in the configuration

2. Outlook

   - Use your existing Outlook/Hotmail account
   - Enable "Less secure app access" in account settings
   - Use your regular email and password

3. Yahoo
   - Use your existing Yahoo account
   - Generate an "App Password" in account settings
   - Use this as your password in the configuration

### Yahoo Mail Setup

Since you're using communication_analysis@yahoo.com, follow these steps to set up Yahoo Mail:

1. Generate an App Password (required for security):

   - Sign in to your Yahoo account
   - Go to Account Security settings (click on your name > Account info > Account security)
   - Scroll down to "Generate app password"
   - Select "Other app" from the dropdown
   - Enter "Posture Analysis" as the app name
   - Click "Generate"
   - Copy the generated 16-character password

2. Set up environment variables with your Yahoo credentials:

   ```bash
   # On Windows (Command Prompt)
   set EMAIL_ADDRESS=communication_analysis@yahoo.com
   set EMAIL_PASSWORD=your-16-char-app-password
   set EMAIL_PROVIDER=yahoo
   set ANALYSIS_EMAIL=communication_analysis@yahoo.com

   # On Mac/Linux
   export EMAIL_ADDRESS=communication_analysis@yahoo.com
   export EMAIL_PASSWORD=your-16-char-app-password
   export EMAIL_PROVIDER=yahoo
   export ANALYSIS_EMAIL=communication_analysis@yahoo.com
   ```

### Setup

1. Install Python 3.8 or higher
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:

   ```bash
   # On Windows (Command Prompt)
   set EMAIL_ADDRESS=your.email@example.com
   set EMAIL_PASSWORD=your-password-or-api-key
   set EMAIL_PROVIDER=smtp2go  # or outlook, yahoo
   set ANALYSIS_EMAIL=analysis.email@example.com

   # On Mac/Linux
   export EMAIL_ADDRESS=your.email@example.com
   export EMAIL_PASSWORD=your-password-or-api-key
   export EMAIL_PROVIDER=smtp2go  # or outlook, yahoo
   export ANALYSIS_EMAIL=analysis.email@example.com
   ```

### Recording and Sending Videos

1. Run the recording script:
   ```bash
   python src/utils/record_and_send.py
   ```
2. The script will:
   - Open your camera
   - Show a preview window
   - Record for 5 minutes (or press 'q' to stop early)
   - Automatically send the recording to the analysis email
   - Save a local copy in the `recordings` directory

### Analysis Server Setup

1. On your Windows computer, set up the environment variables as described above
2. Run the analysis server:
   ```bash
   python src/utils/email_recording.py
   ```
3. The server will:
   - Monitor the specified email address for new recordings
   - Process any received videos
   - Send back analysis results via email

## Real-Time Streaming System (Alternative)

If you prefer real-time analysis, you can use the streaming system instead.

### Windows Computer (Server)

1. Install Python 3.8 or higher
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python src/utils/remote_recording_server.py
   ```
4. Note your computer's IP address (you can find it using `ipconfig` in Command Prompt)

### Phone/MacBook (Client)

1. Install Python 3.8 or higher
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Edit the client configuration in `src/utils/remote_recorder_client.py`:
   ```python
   config = {
       "output_dir": "recordings",
       "server_host": "YOUR_WINDOWS_IP",  # Replace with your Windows computer's IP
       "server_port": 5000
   }
   ```
4. Run the client:
   ```bash
   python src/utils/remote_recorder_client.py
   ```

## Features

- Video recording with preview
- Email-based submission and analysis
- Real-time streaming option
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

   - Make sure you're using an App Password for Gmail
   - Check your email settings and permissions
   - Verify the email addresses are correct

2. Camera Issues:

   - Ensure the camera is not being used by another application
   - Check camera permissions on your device
   - Try restarting the recording application

3. Performance Issues:
   - Reduce the video resolution in the configuration
   - Check available disk space
   - Monitor system resources

## Security Notes

- The system uses Gmail's secure SMTP and IMAP protocols
- App Passwords are required for Gmail accounts
- Keep your email credentials secure
- Don't share your App Password with anyone

## Contributing

Feel free to submit issues and enhancement requests!
