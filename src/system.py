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
from .utils.recording import RecordingManager

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
        self.recording_manager = RecordingManager(self.config)
        
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
            # Get all relevant data
            schedule = await self._get_current_schedule()
            fitness_data = await self._get_fitness_data()
            recording_data = await self._get_recording_data()
            posture_data = await self._get_posture_data()
            
            # Get insights from previous day
            insights_file = Path("data/insights.json")
            previous_insights = {}
            if insights_file.exists():
                with open(insights_file, 'r') as f:
                    insights_data = json.load(f)
                    # Get insights from last 24 hours
                    current_time = datetime.now()
                    previous_insights = {
                        k: v for k, v in insights_data.get('insights', {}).items()
                        if (current_time - datetime.fromisoformat(v['timestamp'])).total_seconds() <= 86400
                    }
            
            # Get research topics from previous day
            research_file = Path("data/research.json")
            previous_research = {}
            if research_file.exists():
                with open(research_file, 'r') as f:
                    research_data = json.load(f)
                    # Get research from last 24 hours
                    current_time = datetime.now()
                    previous_research = {
                        k: v for k, v in research_data.get('topics', {}).items()
                        if (current_time - datetime.fromisoformat(v['timestamp'])).total_seconds() <= 86400
                    }
            
            # Prepare comprehensive data for night research
            research_data = {
                'schedule': schedule,
                'fitness_data': fitness_data,
                'recording_data': recording_data,
                'posture_data': posture_data,
                'previous_insights': previous_insights,
                'previous_research': previous_research,
                'system_state': {
                    'is_running': self.is_running,
                    'active_research': list(self.active_research.keys()),
                    'research_topics': self.research_topics
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Update personal development agent with comprehensive data
            await self.personal_dev_agent.process(research_data)
            
            # Store research preparation data
            prep_file = Path("data/night_research_prep.json")
            prep_file.parent.mkdir(parents=True, exist_ok=True)
            with open(prep_file, 'w') as f:
                json.dump(research_data, f, indent=2)
            
            self.logger.info("Night research preparation completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error preparing night research: {e}")
            
    async def _get_current_schedule(self) -> Dict:
        """Get current schedule data."""
        try:
            schedule_file = Path("data/schedule.json")
            if not schedule_file.exists():
                return {"error": "No schedule file found"}
                
            with open(schedule_file, 'r') as f:
                schedule_data = json.load(f)
                
            # Get current date and time
            current_date = datetime.now().date()
            current_time = datetime.now().time()
            
            # Find current and upcoming tasks
            current_tasks = []
            upcoming_tasks = []
            
            for task in schedule_data.get('tasks', []):
                task_date = datetime.fromisoformat(task['date']).date()
                task_time = datetime.fromisoformat(task['time']).time()
                
                if task_date == current_date:
                    if task_time <= current_time:
                        current_tasks.append(task)
                    else:
                        upcoming_tasks.append(task)
                elif task_date > current_date:
                    upcoming_tasks.append(task)
            
            return {
                'current_tasks': current_tasks,
                'upcoming_tasks': upcoming_tasks,
                'current_date': current_date.isoformat(),
                'current_time': current_time.isoformat(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting schedule data: {e}")
            return {"error": str(e)}
        
    async def _get_fitness_data(self) -> Dict:
        """Get fitness data."""
        try:
            fitness_file = Path("data/fitness.json")
            if not fitness_file.exists():
                return {"error": "No fitness data file found"}
                
            with open(fitness_file, 'r') as f:
                fitness_data = json.load(f)
            
            # Get latest workout data
            workouts = fitness_data.get('workouts', [])
            latest_workout = max(workouts, key=lambda x: x['timestamp']) if workouts else None
            
            # Calculate weekly averages
            current_date = datetime.now()
            week_ago = current_date - timedelta(days=7)
            
            recent_workouts = [
                w for w in workouts 
                if datetime.fromisoformat(w['timestamp']) >= week_ago
            ]
            
            weekly_stats = {
                'total_workouts': len(recent_workouts),
                'average_duration': sum(w.get('duration', 0) for w in recent_workouts) / len(recent_workouts) if recent_workouts else 0,
                'average_intensity': sum(w.get('intensity', 0) for w in recent_workouts) / len(recent_workouts) if recent_workouts else 0,
                'total_calories': sum(w.get('calories_burned', 0) for w in recent_workouts)
            }
            
            return {
                'latest_workout': latest_workout,
                'weekly_stats': weekly_stats,
                'fitness_goals': fitness_data.get('goals', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting fitness data: {e}")
            return {"error": str(e)}
        
    async def _get_recording_data(self) -> Dict:
        """Get presentation recording data."""
        try:
            recordings_dir = Path("data/recordings")
            if not recordings_dir.exists():
                return {"error": "No recordings directory found"}
                
            # Find most recent presentation recording
            recordings = list(recordings_dir.glob("presentation_*.avi"))
            if not recordings:
                return {"error": "No presentation recordings found"}
                
            latest_recording = max(recordings, key=lambda x: x.stat().st_mtime)
            analysis_file = latest_recording.with_suffix('.json')
            
            if not analysis_file.exists():
                return {"error": "Analysis file not found"}
                
            # Load analysis data
            with open(analysis_file, 'r') as f:
                analysis_data = json.load(f)
            
            # Get realtime metrics if available
            realtime_metrics = await self.recording_manager.get_realtime_metrics()
            
            return {
                "latest_recording": str(latest_recording),
                "analysis_file": str(analysis_file),
                "analysis_data": analysis_data,
                "realtime_metrics": realtime_metrics.__dict__ if realtime_metrics else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting recording data: {e}")
            return {"error": str(e)}
        
    async def _get_posture_data(self) -> Dict:
        """Get posture monitoring data."""
        try:
            # Get latest recording
            recordings_dir = Path("data/recordings")
            if not recordings_dir.exists():
                return {"error": "No recordings directory found"}
                
            # Find most recent recording
            recordings = list(recordings_dir.glob("posture_*.avi"))
            if not recordings:
                return {"error": "No recordings found"}
                
            latest_recording = max(recordings, key=lambda x: x.stat().st_mtime)
            analysis_file = latest_recording.with_suffix('.json')
            
            if not analysis_file.exists():
                return {"error": "Analysis file not found"}
                
            # Load analysis data
            with open(analysis_file, 'r') as f:
                analysis_data = json.load(f)
            
            # Get realtime metrics if available
            realtime_metrics = await self.recording_manager.get_realtime_metrics()
            
            return {
                "latest_recording": str(latest_recording),
                "analysis_file": str(analysis_file),
                "analysis_data": analysis_data,
                "realtime_metrics": realtime_metrics.__dict__ if realtime_metrics else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting posture data: {e}")
            return {"error": str(e)}
        
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