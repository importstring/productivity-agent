"""Main entry point for the productivity agent system."""
import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import json

from src.agents.multi_agent_system import MultiAgentSystem
from src.utils.recording import RecordingManager
from src.config import load_config
from src.agents.specialized import NightlyAnalysisAgent

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
			
			# Initialize nightly analysis agent
			nightly_agent = NightlyAnalysisAgent()
			
			# Analyze latest recording
			analysis_result = await nightly_agent.analyze_latest_recording()
			
			if 'error' in analysis_result:
				logger.error(f"Error during nightly analysis: {analysis_result['error']}")
				return
			
			# Log analysis results
			logger.info("Nightly analysis completed successfully")
			logger.info("\nAnalysis Summary:")
			logger.info("-----------------")
			
			# Posture Analysis
			posture = analysis_result.get('posture_analysis', {})
			logger.info("\nPosture Metrics:")
			for metric, data in posture.items():
				if isinstance(data, dict) and 'average' in data:
					logger.info(f"- {metric.replace('_', ' ').title()}: {data['average']:.2f} (Trend: {data['trend']})")
			
			# Speech Analysis
			speech = analysis_result.get('speech_analysis', {})
			logger.info("\nSpeech Analysis:")
			if 'transcript' in speech:
				logger.info(f"Transcript: {speech['transcript']}")
			if 'clarity' in speech:
				logger.info(f"Clarity Score: {speech['clarity'].get('average', 0):.2f}")
			if 'speaking_rate' in speech:
				logger.info(f"Speaking Rate: {speech['speaking_rate']:.2f}")
			if 'pitch' in speech:
				pitch_data = speech['pitch']
				logger.info(f"Pitch Variation: {pitch_data.get('variance', 0):.2f}")
			if 'tone' in speech:
				tone_data = speech['tone']
				logger.info(f"Tone Quality:")
				logger.info(f"  - Warmth: {tone_data.get('warmth', 0):.2f}")
				logger.info(f"  - Brightness: {tone_data.get('brightness', 0):.2f}")
				logger.info(f"  - Clarity: {tone_data.get('clarity', 0):.2f}")
			
			# Engagement Analysis
			engagement = analysis_result.get('engagement_analysis', {})
			logger.info("\nEngagement Metrics:")
			for metric, data in engagement.items():
				if isinstance(data, dict) and 'average' in data:
					logger.info(f"- {metric.replace('_', ' ').title()}: {data['average']:.2f} (Trend: {data['trend']})")
			
			# Multimodal Analysis
			multimodal = analysis_result.get('multimodal_analysis', {})
			logger.info("\nMultimodal Communication Analysis:")
			if 'overall_coherence' in multimodal:
				coherence = multimodal['overall_coherence']
				logger.info(f"Overall Coherence: {coherence.get('average', 0):.2f} (Trend: {coherence.get('trend', 'stable')})")
			if 'speech_posture_alignment' in multimodal:
				alignment = multimodal['speech_posture_alignment']
				logger.info(f"Speech-Posture Alignment Score: {alignment.get('score', 0):.2f}")
				logger.info(f"Pattern Matches: {alignment.get('pattern_matches', 0)}")
			
			# Progress Metrics
			progress = analysis_result.get('progress_metrics', {})
			logger.info("\nProgress Overview:")
			if 'overall' in progress:
				overall = progress['overall']
				logger.info(f"Overall Progress Score: {overall.get('score', 0):.2f}")
				logger.info(f"Confidence: {overall.get('confidence', 0):.2f}")
				logger.info(f"Trend: {overall.get('trend', 'stable')}")
			
			# Category-specific Progress
			for category in ['posture', 'speech', 'engagement', 'multimodal']:
				if category in progress:
					cat_progress = progress[category]
					logger.info(f"\n{category.title()} Progress:")
					logger.info(f"- Average Improvement: {cat_progress.get('average_improvement', 0):.2f}")
					logger.info(f"- Consistency: {cat_progress.get('consistency', 0):.2f}")
					logger.info(f"- Trend: {cat_progress.get('trend', 'stable')}")
			
			# Improvement Suggestions
			suggestions = analysis_result.get('improvement_suggestions', [])
			if suggestions:
				logger.info("\nImprovement Suggestions:")
				for suggestion in suggestions:
					logger.info(f"- {suggestion}")
			
			# Save detailed analysis to file
			analysis_file = Path("data/analysis") / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
			analysis_file.parent.mkdir(parents=True, exist_ok=True)
			with open(analysis_file, 'w') as f:
				json.dump(analysis_result, f, indent=2)
			
			logger.info(f"\nDetailed analysis saved to: {analysis_file}")
			
			return analysis_result
			
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
