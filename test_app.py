"""Test script for productivity agent in test mode."""
import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Set test mode environment variable
os.environ["TEST_MODE"] = "true"

from src.config import load_config
from main import setup_logging, SystemRouter

async def test_functionality():
    """Test main functionality in test mode."""
    # Load configuration
    config = load_config('src/config/system_config.json')
    
    # Setup logging
    setup_logging(config)
    
    logging.info("Starting test in TEST MODE")
    
    # Initialize system router
    router = SystemRouter()
    await router.start()
    
    try:
        # Test posture recording (shorten duration for test)
        logging.info("\n==== Testing posture recording ====")
        result = await router.handle_posture_recording(duration=3)
        logging.info(f"Posture recording result: {result}")
        
        # Test nightly analysis
        logging.info("\n==== Testing nightly analysis ====")
        result = await router.handle_nightly_analysis()
        logging.info(f"Nightly analysis completed with {len(result.get('improvement_suggestions', []))} suggestions")
        
        # Create a sample questions.json file for testing
        questions_dir = Path("data/questions")
        questions_dir.mkdir(parents=True, exist_ok=True)
        
        with open(questions_dir / "questions.json", 'w') as f:
            f.write("""
            {
                "questions": [
                    "How can I improve my public speaking skills?",
                    "What strategies help with time management?",
                    "How can I become more confident in meetings?"
                ]
            }
            """)
        
        # Test written questions
        logging.info("\n==== Testing written questions ====")
        result = await router.handle_written_questions()
        logging.info(f"Written questions processed: {result.get('total_questions', 0)}")
        
        # Create a sample input.json file for testing
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        with open(data_dir / "input.json", 'w') as f:
            f.write("""
            {
                "schedule": {
                    "meetings": [
                        {"title": "Team Standup", "time": "09:00", "duration": 30},
                        {"title": "Client Presentation", "time": "14:00", "duration": 60}
                    ]
                },
                "fitness": {
                    "steps": 8500,
                    "active_minutes": 35
                }
            }
            """)
        
        # Test data insertion
        logging.info("\n==== Testing data insertion ====")
        result = await router.handle_data_insertion()
        logging.info(f"Data insertion results: {result.get('results', {})}")
        
        logging.info("\nAll tests passed successfully!")
        
    finally:
        # Clean up
        await router.stop()

if __name__ == "__main__":
    asyncio.run(test_functionality()) 