"""Configuration management for the productivity agent system."""
import json
import logging
import os
from typing import Dict, Any

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from file or return default config."""
    default_config = {
        "meeting_time": "07:30",
        "timezone": "UTC",
        "research_topics": [
            "time management techniques",
            "productivity tools and systems",
            "habit formation",
            "focus and concentration improvement",
            "energy management",
            "task prioritization methods"
        ],
        "model_configs": {
            "pm_model": "llama2:7b",
            "research_model": "llama2:250m",
            "insights_model": "llama2:250m"
        },
        "research_interval": 600,  # 10 minutes in seconds
        "pre_meeting_buffer": 300,  # 5 minutes in seconds
        "logging": {
            "level": "INFO",
            "file": "logs/productivity_agent.log"
        }
    }
    
    if not config_path:
        return default_config
        
    try:
        with open(config_path, 'r') as f:
            user_config = json.load(f)
            # Merge user config with defaults
            return {**default_config, **user_config}
    except FileNotFoundError:
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        # Save default config
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in config file: {config_path}")
        return default_config 