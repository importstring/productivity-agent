"""Main entry point for the productivity agent system."""
import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
import json

from src.agents.multi_agent_system import MultiAgentSystem
from src.utils.recording import RecordingManager
from src.config import load_config
from src.agents.specialized import NightlyAnalysisAgent
from src.agents.question_recorder import QuestionRecorder

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
		try:
			self.config = load_config()
			self.system = MultiAgentSystem(self.config)
			self.recording_manager = RecordingManager(self.config)
			self.is_running = True
		except Exception as e:
			logger.error(f"Failed to initialize SystemRouter: {e}")
			raise
	
	async def start(self):
		"""Start the system and initialize all components."""
		try:
			logger.info("Starting Productivity Agent system...")
			await self.system.initialize()
			logger.info("System initialized successfully")
		except Exception as e:
			logger.error(f"Failed to start system: {e}")
			self.is_running = False
			raise
	
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
			
			# Create data directory if it doesn't exist
			os.makedirs("data/recordings", exist_ok=True)
			
			# Start recording
			result = await self.recording_manager.start_recording(session_id)
			if 'error' in result:
				logger.error(f"Failed to start recording: {result['error']}")
				return
			
			# Monitor posture for specified duration
			start_time = datetime.now()
			while (datetime.now() - start_time).total_seconds() < duration:
				try:
					metrics = await self.recording_manager.get_realtime_metrics()
					if metrics:
						logger.info(f"Posture metrics: {metrics}")
				except Exception as e:
					logger.warning(f"Error getting metrics: {e}")
				await asyncio.sleep(1)
			
			# Stop recording
			result = await self.recording_manager.stop_recording()
			if 'error' in result:
				logger.error(f"Failed to stop recording: {result['error']}")
				return
			
			logger.info(f"Recording completed: {result['filepath']}")
			
		except Exception as e:
			logger.error(f"Error during posture recording: {e}")
			raise

	async def handle_nightly_analysis(self):
		"""Handle nightly analysis session."""
		try:
			logger.info("Starting nightly analysis...")
			
			# Initialize nightly analysis agent
			nightly_agent = NightlyAnalysisAgent()
			
			# Create analysis directory if it doesn't exist
			os.makedirs("data/analysis", exist_ok=True)
			
			# Analyze latest recording
			analysis_result = await nightly_agent.analyze_latest_recording()
			
			if 'error' in analysis_result:
				logger.error(f"Error during nightly analysis: {analysis_result['error']}")
				return
			
			# Save detailed analysis to file
			analysis_file = Path("data/analysis") / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
			with open(analysis_file, 'w') as f:
				json.dump(analysis_result, f, indent=2)
			
			logger.info(f"Analysis saved to: {analysis_file}")
			return analysis_result
			
		except Exception as e:
			logger.error(f"Error during nightly analysis: {e}")
			raise

	async def handle_verbal_questions(self):
		"""Handle verbal question answering session."""
		try:
			logger.info("Starting verbal question answering session...")
			
			# Create questions directory if it doesn't exist
			os.makedirs("data/questions", exist_ok=True)
			
			# Initialize question recorder
			question_recorder = QuestionRecorder(self.config)
			
			# Start recording session
			session_id = f"verbal_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
			result = await question_recorder.start_recording(session_id)
			
			if 'error' in result:
				logger.error(f"Failed to start recording: {result['error']}")
				return
			
			try:
				# Monitor response metrics in real-time
				start_time = datetime.now()
				while (datetime.now() - start_time).total_seconds() < 300:  # 5-minute session
					metrics = await question_recorder.get_realtime_metrics()
					if metrics:
						logger.info(f"Response metrics: {metrics}")
					await asyncio.sleep(1)
			except asyncio.CancelledError:
				logger.info("Recording session cancelled")
			finally:
				# Stop recording and get analysis
				result = await question_recorder.stop_recording()
				if 'error' in result:
					logger.error(f"Failed to stop recording: {result['error']}")
					return
			
			return result
			
		except Exception as e:
			logger.error(f"Error during verbal question session: {e}")
			raise

	async def handle_written_questions(self):
		"""Handle written question answering session."""
		try:
			logger.info("Starting written question answering session...")
			
			# Create questions directory if it doesn't exist
			questions_dir = Path("data/questions")
			questions_dir.mkdir(parents=True, exist_ok=True)
			
			# Get questions from file
			questions_file = questions_dir / "questions.json"
			if not questions_file.exists():
				logger.error("No questions file found")
				return {"error": "No questions file found"}
			
			with open(questions_file, 'r') as f:
				questions_data = json.load(f)
				questions = questions_data.get('questions', [])
			
			if not questions:
				logger.error("No questions available")
				return {"error": "No questions available"}
			
			# Process each question
			responses = []
			for question in questions:
				try:
					# Get response from system
					response = await self.system.process_question({
						'question': question,
						'type': 'written',
						'timestamp': datetime.now().isoformat()
					})
					
					responses.append({
						'question': question,
						'response': response,
						'timestamp': datetime.now().isoformat()
					})
				except Exception as e:
					logger.error(f"Error processing question '{question}': {e}")
					responses.append({
						'question': question,
						'error': str(e),
						'timestamp': datetime.now().isoformat()
					})
			
			# Save responses
			responses_file = questions_dir / f"responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
			with open(responses_file, 'w') as f:
				json.dump({
					'responses': responses,
					'timestamp': datetime.now().isoformat()
				}, f, indent=2)
			
			logger.info(f"Written question session completed. Processed {len(responses)} questions")
			return {
				'total_questions': len(responses),
				'responses': responses,
				'timestamp': datetime.now().isoformat()
			}
			
		except Exception as e:
			logger.error(f"Error during written question session: {e}")
			raise

	async def handle_data_insertion(self):
		"""Handle data insertion session."""
		try:
			logger.info("Starting data insertion session...")
			
			# Create data directories if they don't exist
			data_dirs = ['schedule', 'fitness', 'research', 'insights']
			for dir_name in data_dirs:
				os.makedirs(f"data/{dir_name}", exist_ok=True)
			
			# Get data from input file
			input_file = Path("data/input.json")
			if not input_file.exists():
				logger.error("No input file found")
				return {"error": "No input file found"}
			
			with open(input_file, 'r') as f:
				input_data = json.load(f)
			
			# Process different types of data
			results = {}
			
			for data_type in data_dirs:
				if data_type in input_data:
					try:
						output_file = Path(f"data/{data_type}/{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
						with open(output_file, 'w') as f:
							json.dump(input_data[data_type], f, indent=2)
						results[data_type] = "Updated successfully"
					except Exception as e:
						logger.error(f"Error processing {data_type} data: {e}")
						results[data_type] = f"Error: {str(e)}"
			
			logger.info("Data insertion completed")
			logger.info(f"Results: {results}")
			
			return {
				'results': results,
				'timestamp': datetime.now().isoformat()
			}
			
		except Exception as e:
			logger.error(f"Error during data insertion: {e}")
			raise

async def main():
	"""Main function to run the productivity agent system."""
	try:
		# Load configuration
		config = load_config('src/config/system_config.json')
		
		# Setup logging
		setup_logging(config)
		
		# Initialize the system router
		router = SystemRouter()
		await router.start()
		
		try:
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
				
				try:
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
				except Exception as e:
					logger.error(f"Error processing choice '{choice}': {e}")
					print(f"Error: {e}")
				
				print("\nPress Enter to continue...")
				input()
				
		except KeyboardInterrupt:
			logger.info("Received keyboard interrupt")
		finally:
			await router.stop()
			
	except Exception as e:
		logger.error(f"Fatal error: {e}")
		raise

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("\nShutting down...")
	except Exception as e:
		print(f"Fatal error: {e}")
		logging.error(f"Fatal error: {e}")
