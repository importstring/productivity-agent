# Productivity Agent System

A comprehensive system for improving personal productivity, communication skills, and presentation abilities through automated recording, analysis, and feedback.

## Setup Instructions

### 1. Install Dependencies

1. Install Python 3.8 or higher
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Configuration

The system uses a configuration file located at `src/config/system_config.json`. This file contains settings for:

- Logging configuration
- Agent parameters
- Data storage paths

### 3. Running the Application

#### Standard Mode

Run the main application:

```bash
python main.py
```

The application will present a menu with options:

1. Record posture (5 minutes)
2. Run nightly analysis
3. Answer verbal questions
4. Answer written questions
5. Insert data
   q. Quit

#### Test Mode

To run the application in test mode (which uses mock data and doesn't require external services):

```bash
export TEST_MODE=true
python main.py
```

Or run the automated test script:

```bash
python test_app.py
```

## System Components

### Multi-Agent System

The productivity agent uses a multi-agent system with specialized agents:

- **Product Manager Agent**: Coordinates the overall productivity enhancement process
- **Research Agent**: Gathers information on productivity topics
- **Insights Agent**: Analyzes data and generates actionable insights
- **Nightly Analysis Agent**: Performs comprehensive analysis of recordings

### Recording Capabilities

- **Posture Recording**: Records and analyzes body posture during presentations
- **Speech Recording**: Analyzes speech patterns, clarity, and tone
- **Question Answering**: Records and analyzes responses to questions

### Data Management

The system stores data in organized directories:

- `data/recordings`: Video and audio recordings
- `data/analysis`: Analysis results
- `data/questions`: Questions and responses
- `data/schedule`, `data/fitness`, etc.: Topic-specific data

## Daily Workflow

### Morning Routine

1. Review the nightly analysis
2. Record a practice session
3. Answer verbal questions
4. Get real-time feedback on posture and speech

### Evening Routine

1. Answer written questions
2. Insert data from the day
3. Set up nightly analysis to run on Windows machine

## Usage Examples

### Recording Posture

Select option 1 from the main menu to start a posture recording session. The system will:

- Record video for 5 minutes
- Analyze your posture in real-time
- Save the recording for later analysis

### Answering Questions

Create a `questions.json` file in the `data/questions` directory with your questions:

```json
{
  "questions": [
    "How can I improve my public speaking skills?",
    "What strategies help with time management?"
  ]
}
```

Then select option 4 from the main menu to get responses.

## Advanced Features

### Remote Processing

The system supports recording on one device and processing on another (e.g., Windows machine):

1. Record on your main device
2. Transfer the recordings to your Windows machine
3. Run nightly analysis on the Windows machine

### Custom Prompts

The system can provide random prompts for speaking practice during recording sessions, helping you improve impromptu speaking skills.

## Troubleshooting

If you encounter issues:

1. Check the logs in the `logs` directory
2. Run in test mode to verify basic functionality
3. Ensure all dependencies are installed correctly

## Contributing

Feel free to submit issues and enhancement requests!
