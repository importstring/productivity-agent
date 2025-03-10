"""Main entry point for the productivity agent system."""
import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from src.agents.multi_agent_system import MultiAgentSystem
from src.utils.recording import RecordingManager
from src.config import load_config

# Initialize logger
logger = logging.getLogger(__name__)

def setup_logging(config):
	"""Setup logging configuration."""
	log_config = config.get('logging', {})
	log_level = getattr(logging, log_config.get('level', 'INFO'))
	log_file = log_config.get('file', 'logs/productivity_agent.log')
	
	# Create logs directory if it doesn't exist
	os.makedirs(os.path.dirname(log_file), exist_ok=True)
	
	logging.basicConfig(
		level=log_level,
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		handlers=[
			logging.FileHandler(log_file),
			logging.StreamHandler()
		]
	)

class SystemRouter:
	"""Central router for the Productivity Agent system."""
	
	def __init__(self):
		self.config = load_config()
		self.system = MultiAgentSystem(self.config)
		self.recording_manager = RecordingManager(self.config)
		self.is_running = True
	
	async def start(self):
		"""Start the system and initialize all components."""
		try:
			logger.info("Starting Productivity Agent system...")
			await self.system.initialize()
			logger.info("System initialized successfully")
		except Exception as e:
			logger.error(f"Failed to start system: {e}")
			self.is_running = False
	
	async def stop(self):
		"""Stop the system and cleanup resources."""
		try:
			logger.info("Stopping Productivity Agent system...")
			await self.system.cleanup()
			logger.info("System stopped successfully")
		except Exception as e:
			logger.error(f"Error during system shutdown: {e}")
		finally:
			self.is_running = False
	
	async def handle_posture_recording(self, duration: int = 300):
		"""Handle posture recording session."""
		try:
			session_id = f"posture_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
			logger.info(f"Starting posture recording session: {session_id}")
			
			# Start recording
			result = await self.recording_manager.start_recording(session_id)
			if 'error' in result:
				logger.error(f"Failed to start recording: {result['error']}")
				return
			
			# Monitor posture for specified duration
			start_time = datetime.now()
			while (datetime.now() - start_time).total_seconds() < duration:
				metrics = await self.recording_manager.get_realtime_metrics()
				if metrics:
					logger.info(f"Posture metrics: {metrics}")
				await asyncio.sleep(1)
			
			# Stop recording
			result = await self.recording_manager.stop_recording()
			if 'error' in result:
				logger.error(f"Failed to stop recording: {result['error']}")
				return
			
			logger.info(f"Recording completed: {result['filepath']}")
			
		except Exception as e:
			logger.error(f"Error during posture recording: {e}")
	
	async def handle_nightly_analysis(self):
		"""Handle nightly analysis session."""
		try:
			logger.info("Starting nightly analysis...")
			await self.system.night_research_agent.start_research()
			logger.info("Nightly analysis completed")
		except Exception as e:
			logger.error(f"Error during nightly analysis: {e}")
	
	async def handle_verbal_questions(self):
		"""Handle verbal question answering session."""
		try:
			logger.info("Starting verbal question answering session...")
			# TODO: Implement verbal question handling
			logger.info("Verbal question session completed")
		except Exception as e:
			logger.error(f"Error during verbal question session: {e}")
	
	async def handle_written_questions(self):
		"""Handle written question answering session."""
		try:
			logger.info("Starting written question answering session...")
			# TODO: Implement written question handling
			logger.info("Written question session completed")
		except Exception as e:
			logger.error(f"Error during written question session: {e}")
	
	async def handle_data_insertion(self):
		"""Handle data insertion session."""
		try:
			logger.info("Starting data insertion session...")
			# TODO: Implement data insertion handling
			logger.info("Data insertion completed")
		except Exception as e:
			logger.error(f"Error during data insertion: {e}")

async def main():
	"""Main function to run the productivity agent system."""
	# Load configuration
	config = load_config('src/config/system_config.json')
	
	# Setup logging
	setup_logging(config)
	
	# Initialize the multi-agent system
	system = MultiAgentSystem(config)
	
	try:
		logging.info("Starting productivity agent system...")
		await system.initialize()
		
		router = SystemRouter()
		
		while router.is_running:
			print("\nProductivity Agent System")
			print("------------------------")
			print("1. Record posture (5 minutes)")
			print("2. Run nightly analysis")
			print("3. Answer verbal questions")
			print("4. Answer written questions")
			print("5. Insert data")
			print("q. Quit")
			
			choice = input("\nEnter your choice: ").strip().lower()
			
			if choice == 'q':
				break
			elif choice == '1':
				await router.handle_posture_recording()
			elif choice == '2':
				await router.handle_nightly_analysis()
			elif choice == '3':
				await router.handle_verbal_questions()
			elif choice == '4':
				await router.handle_written_questions()
			elif choice == '5':
				await router.handle_data_insertion()
			else:
				print("Invalid choice. Please try again.")
			
			print("\nPress Enter to continue...")
			input()
	
	except KeyboardInterrupt:
		logging.info("Shutting down productivity agent system...")
		await system.cleanup()
	except Exception as e:
		logging.error(f"Error running productivity agent system: {e}")
		await system.cleanup()
		raise

if __name__ == "__main__":
	asyncio.run(main())
