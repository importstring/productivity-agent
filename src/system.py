"""
Main system implementation for the Productivity Agent.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json
import aiohttp
from concurrent.futures import ThreadPoolExecutor

from .agents.specialized import (
    ProductManagerAgent,
    ResearchAgent,
    ReflectionAgent,
    QuestionGeneratorAgent,
    DailyCycleAgent,
    LearningAgent,
    PersonalDevelopmentAgent,
    NightResearchAgent
)

class MultiAgentSystem:
    """Main system class coordinating all agents."""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize agents
        self.pm_agent = ProductManagerAgent(self.config)
        self.research_agent = ResearchAgent(self.config)
        self.reflection_agent = ReflectionAgent(self.config)
        self.question_agent = QuestionGeneratorAgent(self.config)
        self.daily_cycle_agent = DailyCycleAgent(self.config)
        self.learning_agent = LearningAgent(self.config)
        self.personal_dev_agent = PersonalDevelopmentAgent(self.config)
        self.night_research_agent = NightResearchAgent(self.config)
        
        # Register agents with PM
        self.pm_agent.register_agent("research", self.research_agent)
        self.pm_agent.register_agent("reflection", self.reflection_agent)
        self.pm_agent.register_agent("question_generator", self.question_agent)
        self.pm_agent.register_agent("daily_cycle", self.daily_cycle_agent)
        self.pm_agent.register_agent("learning", self.learning_agent)
        self.pm_agent.register_agent("personal_dev", self.personal_dev_agent)
        self.pm_agent.register_agent("night_research", self.night_research_agent)
        
        # System state
        self.is_running = False
        self.research_topics = []
        self.active_research = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load system configuration."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}
            
    def _setup_logging(self) -> logging.Logger:
        """Setup system logging."""
        logger = logging.getLogger("MultiAgentSystem")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        fh = logging.FileHandler(log_dir / "system.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
        
    async def start(self):
        """Start the system."""
        try:
            self.is_running = True
            self.logger.info("Starting MultiAgentSystem")
            
            # Start night-time research
            await self._start_night_research()
            
            # Start daily cycle
            await self.process_daily_cycle()
            
            # Start continuous research
            asyncio.create_task(self._continuous_research())
            
        except Exception as e:
            self.logger.error(f"Error starting system: {e}")
            self.is_running = False
            
    async def stop(self):
        """Stop the system."""
        try:
            self.is_running = False
            self.logger.info("Stopping MultiAgentSystem")
            
            # Stop all background tasks
            for task in asyncio.all_tasks():
                task.cancel()
                
            # Wait for tasks to complete
            await asyncio.gather(*asyncio.all_tasks(), return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Error stopping system: {e}")
            
    async def _start_night_research(self):
        """Start night-time research process."""
        try:
            self.logger.info("Starting night-time research")
            
            # Start research at 9 PM
            current_time = datetime.now().time()
            research_start = datetime.strptime("21:00", "%H:%M").time()
            
            if current_time >= research_start:
                # If it's already past 9 PM, start immediately
                await self.night_research_agent.start_research()
            else:
                # Wait until 9 PM
                wait_seconds = (datetime.combine(datetime.today(), research_start) - 
                              datetime.combine(datetime.today(), current_time)).total_seconds()
                await asyncio.sleep(wait_seconds)
                await self.night_research_agent.start_research()
                
            # Wait until 7:30 AM to prepare questions
            await asyncio.sleep(12.5 * 3600)  # 12.5 hours
            
            # Get morning questions
            questions = await self.night_research_agent.get_questions()
            self.logger.info(f"Generated {len(questions)} morning questions")
            
            # Store questions for morning
            await self._store_morning_questions(questions)
            
        except Exception as e:
            self.logger.error(f"Error in night research: {e}")
            
    async def _store_morning_questions(self, questions: List[str]):
        """Store morning questions for retrieval."""
        try:
            questions_file = Path("data/morning_questions.json")
            questions_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(questions_file, 'w') as f:
                json.dump({
                    'questions': questions,
                    'timestamp': datetime.now().isoformat()
                }, f)
                
        except Exception as e:
            self.logger.error(f"Error storing morning questions: {e}")
            
    async def process_daily_cycle(self):
        """Process daily cycle tasks."""
        try:
            while self.is_running:
                current_time = datetime.now().time()
                
                # Morning tasks (7:30 AM)
                if current_time >= datetime.strptime("07:30", "%H:%M").time():
                    await self._handle_morning_tasks()
                    
                # Afternoon tasks (12:00 PM)
                elif current_time >= datetime.strptime("12:00", "%H:%M").time():
                    await self._handle_afternoon_tasks()
                    
                # Evening tasks (6:00 PM)
                elif current_time >= datetime.strptime("18:00", "%H:%M").time():
                    await self._handle_evening_tasks()
                    
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
        except Exception as e:
            self.logger.error(f"Error in daily cycle: {e}")
            
    async def _handle_morning_tasks(self):
        """Handle morning tasks."""
        try:
            # Load morning questions
            questions_file = Path("data/morning_questions.json")
            if questions_file.exists():
                with open(questions_file, 'r') as f:
                    data = json.load(f)
                    questions = data.get('questions', [])
                    
                # Process questions with personal development agent
                await self.personal_dev_agent.process({
                    'questions': questions,
                    'time_of_day': 'morning'
                })
                
            # Start presentation recording
            recording_config = await self.personal_dev_agent._setup_presentation_recording()
            self.logger.info(f"Started presentation recording with config: {recording_config}")
            
            # Start posture monitoring
            posture_config = await self.personal_dev_agent._setup_posture_monitoring()
            self.logger.info(f"Started posture monitoring with config: {posture_config}")
            
        except Exception as e:
            self.logger.error(f"Error handling morning tasks: {e}")
            
    async def _handle_afternoon_tasks(self):
        """Handle afternoon tasks."""
        try:
            # Process presentation recordings
            recording_data = await self._get_recording_data()
            if recording_data:
                feedback = await self.personal_dev_agent.analyze_presentation(recording_data)
                self.logger.info(f"Generated presentation feedback: {feedback}")
                
            # Process posture data
            posture_data = await self._get_posture_data()
            if posture_data:
                analysis = await self.personal_dev_agent.monitor_posture(posture_data)
                self.logger.info(f"Generated posture analysis: {analysis}")
                
        except Exception as e:
            self.logger.error(f"Error handling afternoon tasks: {e}")
            
    async def _handle_evening_tasks(self):
        """Handle evening tasks."""
        try:
            # Prepare for night research
            await self._prepare_night_research()
            
            # Start night research process
            await self._start_night_research()
            
        except Exception as e:
            self.logger.error(f"Error handling evening tasks: {e}")
            
    async def _prepare_night_research(self):
        """Prepare for night research."""
        try:
            # Get current schedule and fitness data
            schedule = await self._get_current_schedule()
            fitness_data = await self._get_fitness_data()
            
            # Update personal development agent
            await self.personal_dev_agent.process({
                'schedule': schedule,
                'fitness_data': fitness_data
            })
            
        except Exception as e:
            self.logger.error(f"Error preparing night research: {e}")
            
    async def _get_current_schedule(self) -> Dict:
        """Get current schedule data."""
        # TODO: Implement schedule retrieval
        return {}
        
    async def _get_fitness_data(self) -> Dict:
        """Get fitness data."""
        # TODO: Implement fitness data retrieval
        return {}
        
    async def _get_recording_data(self) -> Dict:
        """Get presentation recording data."""
        # TODO: Implement recording data retrieval
        return {}
        
    async def _get_posture_data(self) -> Dict:
        """Get posture monitoring data."""
        # TODO: Implement posture data retrieval
        return {}
        
    async def _continuous_research(self):
        """Run continuous research in the background."""
        try:
            while self.is_running:
                # Get new research topics
                topics = await self.research_agent.get_research_topics()
                
                # Process each topic
                for topic in topics:
                    if topic not in self.active_research:
                        self.active_research[topic] = asyncio.create_task(
                            self.research_agent.research_topic(topic)
                        )
                        
                # Clean up completed research
                completed_topics = [
                    topic for topic, task in self.active_research.items()
                    if task.done()
                ]
                for topic in completed_topics:
                    del self.active_research[topic]
                    
                # Wait before next iteration
                await asyncio.sleep(3600)  # Check every hour
                
        except Exception as e:
            self.logger.error(f"Error in continuous research: {e}")
            
    async def overnight_processing(self):
        """Process data and generate insights overnight."""
        try:
            # Analyze daily data
            analysis = await self.learning_agent.process({
                'schedule': await self._get_current_schedule(),
                'fitness_data': await self._get_fitness_data(),
                'presentation_data': await self._get_recording_data(),
                'posture_data': await self._get_posture_data()
            })
            
            # Generate insights
            insights = await self.reflection_agent.generate_insights(analysis)
            
            # Store insights
            await self._store_insights(insights)
            
        except Exception as e:
            self.logger.error(f"Error in overnight processing: {e}")
            
    async def _store_insights(self, insights: Dict):
        """Store generated insights."""
        try:
            insights_file = Path("data/insights.json")
            insights_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(insights_file, 'w') as f:
                json.dump({
                    'insights': insights,
                    'timestamp': datetime.now().isoformat()
                }, f)
                
        except Exception as e:
            self.logger.error(f"Error storing insights: {e}") 