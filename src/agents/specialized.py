from typing import Dict, List, Optional
from datetime import datetime
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from .base import BaseAgent
import ollama
import logging
import json
import os
from pathlib import Path
import io
import speech_recognition as sr
from pydub import AudioSegment

class ProductManagerAgent(BaseAgent):
    """Central coordinator agent that manages other agents and overall system state"""
    def __init__(self):
        super().__init__("PM", "coordinator")
        self.sub_agents = {}
        self.schedule = {}
        self.goals = []
        self.current_tasks = []
        
    def process(self, input_data: Dict) -> Dict:
        # Coordinate between agents
        # Manage schedules and priorities
        # Track progress towards goals
        result = {
            "status": "success",
            "actions_taken": [],
            "next_steps": []
        }
        
        # Process current tasks
        for task in self.current_tasks:
            if task["status"] == "pending":
                # Delegate to appropriate agent
                agent = self.sub_agents.get(task["assigned_agent"])
                if agent:
                    task_result = agent.process(task["data"])
                    task["status"] = "completed"
                    task["result"] = task_result
                    result["actions_taken"].append(task_result)
        
        # Update schedule and goals
        self._update_schedule()
        self._track_goals()
        
        return result
        
    def reflect(self) -> Dict:
        # Analyze system performance
        # Identify bottlenecks
        # Suggest improvements
        reflection = {
            "timestamp": datetime.now(),
            "performance_metrics": self._calculate_metrics(),
            "bottlenecks": self._identify_bottlenecks(),
            "improvement_suggestions": self._generate_suggestions()
        }
        self.add_to_memory(reflection)
        return reflection
        
    def _update_schedule(self) -> None:
        """Update the schedule based on current state and goals"""
        pass
        
    def _track_goals(self) -> None:
        """Track progress towards goals"""
        pass
        
    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        return {}
        
    def _identify_bottlenecks(self) -> List[str]:
        """Identify system bottlenecks"""
        return []
        
    def _generate_suggestions(self) -> List[str]:
        """Generate improvement suggestions"""
        return []

class ResearchAgent(BaseAgent):
    """Agent responsible for gathering and synthesizing information"""
    def __init__(self):
        super().__init__("Research", "information_gatherer")
        self.knowledge_base = {}
        self.research_topics = []
        
    def process(self, input_data: Dict) -> Dict:
        # Search for relevant information
        # Synthesize findings
        # Update knowledge base
        result = {
            "status": "success",
            "findings": [],
            "sources": []
        }
        
        # Process research request
        topic = input_data.get("topic")
        if topic:
            findings = self._conduct_research(topic)
            result["findings"] = findings
            self._update_knowledge_base(topic, findings)
            
        return result
        
    def reflect(self) -> Dict:
        # Evaluate research quality
        # Identify knowledge gaps
        # Suggest research directions
        reflection = {
            "timestamp": datetime.now(),
            "knowledge_coverage": self._analyze_coverage(),
            "gaps": self._identify_gaps(),
            "suggestions": self._generate_research_suggestions()
        }
        self.add_to_memory(reflection)
        return reflection
        
    def _conduct_research(self, topic: str) -> List[Dict]:
        """Conduct research on a specific topic"""
        return []
        
    def _update_knowledge_base(self, topic: str, findings: List[Dict]) -> None:
        """Update the knowledge base with new findings"""
        self.knowledge_base[topic] = findings
        
    def _analyze_coverage(self) -> Dict:
        """Analyze knowledge base coverage"""
        return {}
        
    def _identify_gaps(self) -> List[str]:
        """Identify gaps in knowledge"""
        return []
        
    def _generate_research_suggestions(self) -> List[str]:
        """Generate research suggestions"""
        return []

class ReflectionAgent(BaseAgent):
    """Agent that analyzes patterns and generates insights"""
    def __init__(self):
        super().__init__("Reflection", "analyzer")
        self.insights = []
        self.patterns = {}
        
    def process(self, input_data: Dict) -> Dict:
        # Analyze patterns in data
        # Generate insights
        # Track progress over time
        result = {
            "status": "success",
            "insights": [],
            "patterns": {}
        }
        
        # Process data for analysis
        data = input_data.get("data", [])
        if data:
            patterns = self._analyze_patterns(data)
            insights = self._generate_insights(patterns)
            result["patterns"] = patterns
            result["insights"] = insights
            self.insights.extend(insights)
            
        return result
        
    def reflect(self) -> Dict:
        # Evaluate insight quality
        # Identify analysis gaps
        # Suggest analysis improvements
        reflection = {
            "timestamp": datetime.now(),
            "insight_quality": self._evaluate_quality(),
            "gaps": self._identify_analysis_gaps(),
            "suggestions": self._generate_analysis_suggestions()
        }
        self.add_to_memory(reflection)
        return reflection
        
    def _analyze_patterns(self, data: List[Dict]) -> Dict:
        """Analyze patterns in the data"""
        return {}
        
    def _generate_insights(self, patterns: Dict) -> List[Dict]:
        """Generate insights from patterns"""
        return []
        
    def _evaluate_quality(self) -> Dict:
        """Evaluate the quality of insights"""
        return {}
        
    def _identify_analysis_gaps(self) -> List[str]:
        """Identify gaps in analysis"""
        return []
        
    def _generate_analysis_suggestions(self) -> List[str]:
        """Generate suggestions for analysis improvements"""
        return []

class QuestionGeneratorAgent(BaseAgent):
    """Agent responsible for generating personalized questions"""
    def __init__(self):
        super().__init__("QuestionGenerator", "interaction_designer")
        self.question_history = []
        self.question_templates = []
        
    def process(self, input_data: Dict) -> Dict:
        # Generate personalized questions
        # Track question effectiveness
        # Adapt question style
        result = {
            "status": "success",
            "questions": [],
            "context": {}
        }
        
        # Generate questions based on context
        context = input_data.get("context", {})
        questions = self._generate_questions(context)
        result["questions"] = questions
        result["context"] = context
        
        # Track questions
        self._track_questions(questions)
        
        return result
        
    def reflect(self) -> Dict:
        # Evaluate question quality
        # Analyze user engagement
        # Suggest question improvements
        reflection = {
            "timestamp": datetime.now(),
            "question_quality": self._evaluate_quality(),
            "engagement_metrics": self._analyze_engagement(),
            "suggestions": self._generate_improvement_suggestions()
        }
        self.add_to_memory(reflection)
        return reflection
        
    def _generate_questions(self, context: Dict) -> List[Dict]:
        """Generate personalized questions based on context"""
        return []
        
    def _track_questions(self, questions: List[Dict]) -> None:
        """Track generated questions"""
        self.question_history.extend(questions)
        
    def _evaluate_quality(self) -> Dict:
        """Evaluate the quality of questions"""
        return {}
        
    def _analyze_engagement(self) -> Dict:
        """Analyze user engagement with questions"""
        return {}
        
    def _generate_improvement_suggestions(self) -> List[str]:
        """Generate suggestions for question improvements"""
        return []

class DailyCycleAgent(BaseAgent):
    """Agent responsible for managing the daily question-answer cycle"""
    def __init__(self):
        super().__init__("DailyCycle", "workflow_manager")
        self.question_schedule = []
        self.responses = []
        self.recording_sessions = []
        
    def process(self, input_data: Dict) -> Dict:
        result = {
            "status": "success",
            "questions_sent": [],
            "responses_received": [],
            "recordings_analyzed": []
        }
        
        # Process based on time of day
        current_time = datetime.now().time()
        
        if self._is_morning_time(current_time):
            # Generate and send morning questions
            questions = self._generate_morning_questions()
            result["questions_sent"] = questions
            
        elif self._is_afternoon_time(current_time):
            # Generate and send afternoon questions
            questions = self._generate_afternoon_questions()
            result["questions_sent"] = questions
            
        elif self._is_evening_time(current_time):
            # Collect and process daily responses
            responses = self._collect_daily_responses()
            result["responses_received"] = responses
            
            # Analyze communication recordings if any
            recordings = self._analyze_recordings()
            result["recordings_analyzed"] = recordings
            
        return result
        
    def reflect(self) -> Dict:
        reflection = {
            "timestamp": datetime.now(),
            "cycle_metrics": self._calculate_cycle_metrics(),
            "engagement_analysis": self._analyze_engagement(),
            "improvement_suggestions": self._generate_suggestions()
        }
        self.add_to_memory(reflection)
        return reflection
        
    def _is_morning_time(self, current_time) -> bool:
        """Check if current time is morning (e.g., 6-12)"""
        return 6 <= current_time.hour < 12
        
    def _is_afternoon_time(self, current_time) -> bool:
        """Check if current time is afternoon (e.g., 12-18)"""
        return 12 <= current_time.hour < 18
        
    def _is_evening_time(self, current_time) -> bool:
        """Check if current time is evening (e.g., 18-24)"""
        return 18 <= current_time.hour < 24
        
    def _generate_morning_questions(self) -> List[Dict]:
        """Generate morning questions"""
        return [
            {
                "type": "morning",
                "question": "What are your top 3 priorities for today?",
                "context": "planning"
            },
            {
                "type": "morning",
                "question": "How did you sleep? What's your energy level?",
                "context": "wellness"
            }
        ]
        
    def _generate_afternoon_questions(self) -> List[Dict]:
        """Generate afternoon questions"""
        return [
            {
                "type": "afternoon",
                "question": "How are you progressing on your morning priorities?",
                "context": "progress"
            },
            {
                "type": "afternoon",
                "question": "What's been your biggest challenge so far today?",
                "context": "challenges"
            }
        ]
        
    def _collect_daily_responses(self) -> List[Dict]:
        """Collect and process daily responses"""
        # TODO: Implement response collection logic
        return []
        
    def _analyze_recordings(self) -> List[Dict]:
        """Analyze communication recordings"""
        # TODO: Implement recording analysis logic
        return []
        
    def _calculate_cycle_metrics(self) -> Dict:
        """Calculate metrics for the daily cycle"""
        return {
            "questions_sent": len(self.question_schedule),
            "responses_received": len(self.responses),
            "recordings_analyzed": len(self.recording_sessions)
        }
        
    def _analyze_engagement(self) -> Dict:
        """Analyze user engagement with questions"""
        return {}
        
    def _generate_suggestions(self) -> List[str]:
        """Generate suggestions for improving the daily cycle"""
        return []

class LearningAgent(BaseAgent):
    """Agent responsible for unsupervised learning and loss function optimization"""
    def __init__(self):
        super().__init__("Learning", "optimizer")
        self.knowledge_base = {}
        self.patterns = {}
        self.loss_history = []
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=5, random_state=42)
        
    def process(self, input_data: Dict) -> Dict:
        result = {
            "status": "success",
            "patterns_identified": [],
            "recommendations": [],
            "loss_value": 0.0
        }
        
        # Extract features from input data
        features = self._extract_features(input_data)
        
        # Perform clustering
        clusters = self._cluster_data(features)
        
        # Identify patterns
        patterns = self._identify_patterns(clusters)
        result["patterns_identified"] = patterns
        
        # Generate recommendations
        recommendations = self._generate_recommendations(patterns)
        result["recommendations"] = recommendations
        
        # Calculate loss
        loss = self._calculate_loss(features, patterns)
        result["loss_value"] = loss
        self.loss_history.append(loss)
        
        return result
        
    def reflect(self) -> Dict:
        reflection = {
            "timestamp": datetime.now(),
            "learning_metrics": self._calculate_metrics(),
            "pattern_analysis": self._analyze_patterns(),
            "optimization_suggestions": self._generate_suggestions()
        }
        self.add_to_memory(reflection)
        return reflection
        
    def _extract_features(self, data: Dict) -> np.ndarray:
        """Extract numerical features from input data"""
        # TODO: Implement feature extraction
        return np.array([])
        
    def _cluster_data(self, features: np.ndarray) -> np.ndarray:
        """Perform clustering on features"""
        if len(features) > 0:
            scaled_features = self.scaler.fit_transform(features)
            return self.kmeans.fit_predict(scaled_features)
        return np.array([])
        
    def _identify_patterns(self, clusters: np.ndarray) -> List[Dict]:
        """Identify patterns in clustered data"""
        patterns = []
        unique_clusters = np.unique(clusters)
        
        for cluster in unique_clusters:
            pattern = {
                "cluster_id": int(cluster),
                "size": int(np.sum(clusters == cluster)),
                "characteristics": self._get_cluster_characteristics(cluster)
            }
            patterns.append(pattern)
            
        return patterns
        
    def _get_cluster_characteristics(self, cluster_id: int) -> Dict:
        """Get characteristics of a specific cluster"""
        return {
            "center": self.kmeans.cluster_centers_[cluster_id].tolist(),
            "variance": np.var(self.kmeans.cluster_centers_[cluster_id]).tolist()
        }
        
    def _generate_recommendations(self, patterns: List[Dict]) -> List[str]:
        """Generate recommendations based on patterns"""
        recommendations = []
        
        for pattern in patterns:
            if pattern["size"] > 10:  # Significant pattern
                recommendations.extend(self._generate_pattern_recommendations(pattern))
                
        return recommendations
        
    def _generate_pattern_recommendations(self, pattern: Dict) -> List[str]:
        """Generate specific recommendations for a pattern"""
        return []
        
    def _calculate_loss(self, features: np.ndarray, patterns: List[Dict]) -> float:
        """Calculate loss function value"""
        if len(features) == 0:
            return 0.0
            
        # Calculate reconstruction error
        scaled_features = self.scaler.transform(features)
        distances = self.kmeans.transform(scaled_features)
        reconstruction_error = np.min(distances, axis=1).mean()
        
        # Calculate pattern diversity loss
        pattern_sizes = [p["size"] for p in patterns]
        diversity_loss = 1.0 - (np.std(pattern_sizes) / np.mean(pattern_sizes))
        
        # Combine losses
        total_loss = reconstruction_error + 0.5 * diversity_loss
        
        return float(total_loss)
        
    def _calculate_metrics(self) -> Dict:
        """Calculate learning metrics"""
        return {
            "total_patterns": len(self.patterns),
            "avg_loss": np.mean(self.loss_history) if self.loss_history else 0.0,
            "loss_trend": self._calculate_loss_trend()
        }
        
    def _calculate_loss_trend(self) -> str:
        """Calculate the trend of loss values"""
        if len(self.loss_history) < 2:
            return "stable"
            
        recent_losses = self.loss_history[-5:]
        if np.all(np.diff(recent_losses) < 0):
            return "improving"
        elif np.all(np.diff(recent_losses) > 0):
            return "worsening"
        else:
            return "stable"
            
    def _analyze_patterns(self) -> Dict:
        """Analyze identified patterns"""
        return {}
        
    def _generate_suggestions(self) -> List[str]:
        """Generate suggestions for improving learning"""
        return []

class PersonalDevelopmentAgent:
    """Agent responsible for personal development and daily routines."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.knowledge_base = {}
        self.daily_questions = []
        self.workout_plan = None
        self.presentation_feedback = []
        self.posture_data = []
        self.communication_insights = []
        self.schedule_analysis = {}
        self.ollama = ollama.Client()
        
    async def process(self, input_data: Dict) -> Dict:
        """Process input data and generate personalized development tasks."""
        try:
            # Analyze schedule
            schedule_analysis = await self._analyze_schedule(input_data.get('schedule', {}))
            
            # Generate questions based on research
            questions = await self._generate_questions(schedule_analysis)
            
            # Prepare workout plan
            workout_plan = await self._prepare_workout(input_data.get('fitness_data', {}))
            
            # Set up presentation recording
            recording_config = await self._setup_presentation_recording()
            
            # Initialize posture monitoring
            posture_config = await self._setup_posture_monitoring()
            
            return {
                'schedule_analysis': schedule_analysis,
                'daily_questions': questions,
                'workout_plan': workout_plan,
                'recording_config': recording_config,
                'posture_config': posture_config
            }
            
        except Exception as e:
            logging.error(f"Error in PersonalDevelopmentAgent.process: {e}")
            return {'error': str(e)}
    
    async def _analyze_schedule(self, schedule: Dict) -> Dict:
        """Analyze daily schedule and identify patterns."""
        try:
            # Use Ollama to analyze schedule patterns
            prompt = f"""
            Analyze this schedule and identify:
            1. Peak productivity hours
            2. Potential stress points
            3. Breaks and recovery periods
            4. Meeting patterns
            5. Task distribution
            
            Schedule: {json.dumps(schedule)}
            """
            
            response = self.ollama.generate(
                model='llama2',
                prompt=prompt,
                system="You are a productivity analyst specializing in schedule optimization."
            )
            
            return {
                'analysis': response['response'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing schedule: {e}")
            return {'error': str(e)}
    
    async def _generate_questions(self, schedule_analysis: Dict) -> List[str]:
        """Generate personalized questions based on schedule analysis."""
        try:
            prompt = f"""
            Based on this schedule analysis, generate 5 personalized questions that will help:
            1. Assess daily readiness
            2. Identify potential challenges
            3. Set realistic goals
            4. Monitor emotional state
            5. Track progress
            
            Schedule Analysis: {json.dumps(schedule_analysis)}
            """
            
            response = self.ollama.generate(
                model='llama2',
                prompt=prompt,
                system="You are a personal development coach creating insightful questions."
            )
            
            # Parse questions from response
            questions = [q.strip() for q in response['response'].split('\n') if q.strip()]
            return questions[:5]  # Return top 5 questions
            
        except Exception as e:
            logging.error(f"Error generating questions: {e}")
            return []
    
    async def _prepare_workout(self, fitness_data: Dict) -> Dict:
        """Prepare personalized workout plan."""
        try:
            prompt = f"""
            Create a personalized workout plan considering:
            1. Available time
            2. Energy levels
            3. Previous workout history
            4. Fitness goals
            
            Fitness Data: {json.dumps(fitness_data)}
            """
            
            response = self.ollama.generate(
                model='llama2',
                prompt=prompt,
                system="You are a professional fitness trainer creating personalized workout plans."
            )
            
            return {
                'plan': response['response'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error preparing workout: {e}")
            return {'error': str(e)}
    
    async def _setup_presentation_recording(self) -> Dict:
        """Configure presentation recording settings."""
        return {
            'video': {
                'resolution': '1080p',
                'fps': 30,
                'codec': 'h264'
            },
            'audio': {
                'sample_rate': 44100,
                'channels': 2,
                'format': 'wav'
            },
            'storage_path': str(Path('data/presentations')),
            'analysis_interval': 300  # 5 minutes
        }
    
    async def _setup_posture_monitoring(self) -> Dict:
        """Configure posture monitoring settings."""
        return {
            'check_interval': 300,  # 5 minutes
            'alert_threshold': 0.7,  # 70% incorrect posture
            'metrics': [
                'shoulder_alignment',
                'back_straightness',
                'head_position',
                'neck_angle'
            ],
            'feedback_type': ['visual', 'audio']
        }
    
    async def monitor_posture(self, posture_data: Dict) -> Dict:
        """Monitor and provide feedback on posture."""
        try:
            prompt = f"""
            Analyze this posture data and provide:
            1. Current posture assessment
            2. Improvement suggestions
            3. Health implications
            4. Corrective exercises
            
            Posture Data: {json.dumps(posture_data)}
            """
            
            response = self.ollama.generate(
                model='llama2',
                prompt=prompt,
                system="You are a posture specialist providing real-time feedback."
            )
            
            return {
                'analysis': response['response'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error monitoring posture: {e}")
            return {'error': str(e)}
    
    async def analyze_presentation(self, recording_data: Dict) -> Dict:
        """Analyze presentation recording for improvement suggestions."""
        try:
            prompt = f"""
            Analyze this presentation recording and provide feedback on:
            1. Speaking pace and clarity
            2. Body language
            3. Engagement level
            4. Content organization
            5. Improvement areas
            
            Recording Data: {json.dumps(recording_data)}
            """
            
            response = self.ollama.generate(
                model='llama2',
                prompt=prompt,
                system="You are a presentation skills coach providing detailed feedback."
            )
            
            return {
                'feedback': response['response'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing presentation: {e}")
            return {'error': str(e)}
    
    async def reflect(self) -> Dict:
        """Perform self-analysis and generate insights."""
        try:
            metrics = {
                'questions_generated': len(self.daily_questions),
                'presentation_feedback_count': len(self.presentation_feedback),
                'posture_checks': len(self.posture_data),
                'schedule_analyses': len(self.schedule_analysis)
            }
            
            return {
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error in PersonalDevelopmentAgent.reflect: {e}")
            return {'error': str(e)}

class NightResearchAgent:
    """Agent responsible for night-time research and processing."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.research_topics = []
        self.insights = {}
        self.ollama = ollama.Client()
        self.research_start_time = "21:00"  # 9 PM
        self.research_end_time = "07:00"   # 7 AM
        self.questions_ready_time = "07:30" # 7:30 AM
        
    async def start_research(self) -> Dict:
        """Start the night-time research process."""
        try:
            # Initialize research topics
            self.research_topics = await self._generate_research_topics()
            
            # Process each topic
            for topic in self.research_topics:
                insights = await self._research_topic(topic)
                self.insights[topic] = insights
            
            # Generate morning questions
            questions = await self._prepare_morning_questions()
            
            return {
                'status': 'completed',
                'topics_researched': len(self.research_topics),
                'questions_generated': len(questions),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error in NightResearchAgent.start_research: {e}")
            return {'error': str(e)}
    
    async def _generate_research_topics(self) -> List[str]:
        """Generate research topics based on user's goals and schedule."""
        try:
            prompt = """
            Generate research topics for personal development focusing on:
            1. Productivity optimization
            2. Communication skills
            3. Presentation techniques
            4. Time management
            5. Work-life balance
            6. Stress management
            7. Learning strategies
            8. Health and wellness
            
            Consider recent trends and best practices in each area.
            """
            
            response = self.ollama.generate(
                model='llama2',
                prompt=prompt,
                system="You are a research specialist identifying relevant personal development topics."
            )
            
            # Parse topics from response
            topics = [t.strip() for t in response['response'].split('\n') if t.strip()]
            return topics[:8]  # Return top 8 topics
            
        except Exception as e:
            logging.error(f"Error generating research topics: {e}")
            return []
    
    async def _research_topic(self, topic: str) -> Dict:
        """Research a specific topic using Ollama."""
        try:
            prompt = f"""
            Research the following topic and provide:
            1. Key insights and findings
            2. Practical applications
            3. Recent developments
            4. Expert recommendations
            5. Actionable steps
            
            Topic: {topic}
            """
            
            response = self.ollama.generate(
                model='llama2',
                prompt=prompt,
                system="You are a personal development researcher providing comprehensive insights."
            )
            
            return {
                'topic': topic,
                'insights': response['response'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error researching topic {topic}: {e}")
            return {'error': str(e)}
    
    async def _prepare_morning_questions(self) -> List[str]:
        """Prepare personalized questions for the morning based on research."""
        try:
            # Combine insights from all topics
            combined_insights = "\n".join([
                f"Topic: {topic}\nInsights: {insights['insights']}"
                for topic, insights in self.insights.items()
            ])
            
            prompt = f"""
            Based on this research, generate 5 personalized questions that will:
            1. Assess daily readiness and mindset
            2. Identify potential challenges and solutions
            3. Set realistic goals and expectations
            4. Monitor emotional and physical state
            5. Track progress and adjustments needed
            
            Research Insights: {combined_insights}
            """
            
            response = self.ollama.generate(
                model='llama2',
                prompt=prompt,
                system="You are a personal development coach creating insightful morning questions."
            )
            
            # Parse questions from response
            questions = [q.strip() for q in response['response'].split('\n') if q.strip()]
            return questions[:5]  # Return top 5 questions
            
        except Exception as e:
            logging.error(f"Error preparing morning questions: {e}")
            return []
    
    async def get_questions(self) -> List[str]:
        """Retrieve the prepared morning questions."""
        return await self._prepare_morning_questions()
    
    async def reflect(self) -> Dict:
        """Perform self-analysis and generate insights."""
        try:
            metrics = {
                'topics_researched': len(self.research_topics),
                'insights_generated': len(self.insights),
                'questions_prepared': len(await self._prepare_morning_questions())
            }
            
            return {
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error in NightResearchAgent.reflect: {e}")
            return {'error': str(e)}

class NightlyAnalysisAgent(BaseAgent):
    """Agent responsible for comprehensive nightly analysis of recordings"""
    def __init__(self):
        super().__init__("NightlyAnalysis", "analysis")
        self.latest_recording = None
        self.analysis_results = []
        
    async def analyze_latest_recording(self) -> Dict:
        """Analyze the most recent recording session."""
        try:
            # Get latest recording from data directory
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
                
            # Perform comprehensive analysis
            posture_analysis = self._analyze_posture(analysis_data)
            speech_analysis = self._analyze_speech(analysis_data)
            engagement_analysis = self._analyze_engagement(analysis_data)
            multimodal_analysis = self._analyze_multimodal_coherence(analysis_data)
            
            # Generate personalized baselines if not exists
            baseline_data = self._load_or_create_baseline()
            baseline_comparison = self._compare_with_baseline({
                "posture": posture_analysis,
                "speech": speech_analysis,
                "engagement": engagement_analysis,
                "multimodal": multimodal_analysis
            }, baseline_data)
            
            # Update baseline with new data
            self._update_baseline(baseline_data, {
                "posture": posture_analysis,
                "speech": speech_analysis,
                "engagement": engagement_analysis,
                "multimodal": multimodal_analysis
            })
            
            # Generate comprehensive analysis
            comprehensive_analysis = {
                "recording_file": str(latest_recording),
                "timestamp": datetime.now().isoformat(),
                "posture_analysis": posture_analysis,
                "speech_analysis": speech_analysis,
                "engagement_analysis": engagement_analysis,
                "multimodal_analysis": multimodal_analysis,
                "baseline_comparison": baseline_comparison,
                "improvement_suggestions": self._generate_suggestions(analysis_data),
                "progress_metrics": self._calculate_progress_metrics(baseline_comparison)
            }
            
            self.latest_recording = comprehensive_analysis
            self.analysis_results.append(comprehensive_analysis)
            
            return comprehensive_analysis
            
        except Exception as e:
            logging.error(f"Error in nightly analysis: {e}")
            return {"error": str(e)}
    
    def _load_or_create_baseline(self) -> Dict:
        """Load existing baseline or create new one."""
        try:
            baseline_file = Path("data/baselines/user_baseline.json")
            if baseline_file.exists():
                with open(baseline_file, 'r') as f:
                    return json.load(f)
            
            # Create new baseline
            baseline = {
                "posture": {
                    "shoulder_alignment": {"avg": 0.0, "count": 0},
                    "back_straightness": {"avg": 0.0, "count": 0},
                    "head_position": {"avg": 0.0, "count": 0},
                    "neck_angle": {"avg": 0.0, "count": 0}
                },
                "speech": {
                    "clarity": {"avg": 0.0, "count": 0},
                    "speaking_rate": {"avg": 0.0, "count": 0},
                    "pitch_variance": {"avg": 0.0, "count": 0}
                },
                "engagement": {
                    "overall_confidence": {"avg": 0.0, "count": 0},
                    "engagement_level": {"avg": 0.0, "count": 0}
                },
                "multimodal": {
                    "coherence": {"avg": 0.0, "count": 0},
                    "alignment": {"avg": 0.0, "count": 0}
                },
                "last_updated": datetime.now().isoformat()
            }
            
            # Ensure directory exists
            baseline_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save baseline
            with open(baseline_file, 'w') as f:
                json.dump(baseline, f, indent=2)
            
            return baseline
            
        except Exception as e:
            logging.error(f"Error loading/creating baseline: {e}")
            return {}
            
    def _update_baseline(self, baseline: Dict, new_data: Dict) -> None:
        """Update baseline with new analysis data."""
        try:
            # Update posture metrics
            for metric, data in new_data["posture"].items():
                if isinstance(data, dict) and "average" in data:
                    self._update_running_average(
                        baseline["posture"][metric],
                        data["average"]
                    )
            
            # Update speech metrics
            for metric, data in new_data["speech"].items():
                if isinstance(data, dict) and "average" in data:
                    self._update_running_average(
                        baseline["speech"][metric],
                        data["average"]
                    )
            
            # Update engagement metrics
            for metric, data in new_data["engagement"].items():
                if isinstance(data, dict) and "average" in data:
                    self._update_running_average(
                        baseline["engagement"][metric],
                        data["average"]
                    )
            
            # Update multimodal metrics
            for metric, data in new_data["multimodal"].items():
                if isinstance(data, dict) and "average" in data:
                    self._update_running_average(
                        baseline["multimodal"][metric],
                        data["average"]
                    )
            
            baseline["last_updated"] = datetime.now().isoformat()
            
            # Save updated baseline
            baseline_file = Path("data/baselines/user_baseline.json")
            with open(baseline_file, 'w') as f:
                json.dump(baseline, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error updating baseline: {e}")
            
    def _update_running_average(self, metric: Dict, new_value: float) -> None:
        """Update running average with new value."""
        current_avg = metric["avg"]
        count = metric["count"]
        
        # Update average
        metric["avg"] = (current_avg * count + new_value) / (count + 1)
        metric["count"] += 1
            
    def _compare_with_baseline(self, current_data: Dict, baseline: Dict) -> Dict:
        """Compare current analysis with baseline."""
        try:
            comparison = {}
            
            # Compare each category
            for category in ["posture", "speech", "engagement", "multimodal"]:
                comparison[category] = {}
                for metric, data in current_data[category].items():
                    if isinstance(data, dict) and "average" in data:
                        baseline_value = baseline[category][metric]["avg"]
                        current_value = data["average"]
                        
                        comparison[category][metric] = {
                            "current": float(current_value),
                            "baseline": float(baseline_value),
                            "improvement": float(current_value - baseline_value),
                            "percent_change": float((current_value - baseline_value) / baseline_value * 100) if baseline_value > 0 else 0.0
                        }
            
            return comparison
            
        except Exception as e:
            logging.error(f"Error comparing with baseline: {e}")
            return {}
            
    def _calculate_progress_metrics(self, baseline_comparison: Dict) -> Dict:
        """Calculate overall progress metrics."""
        try:
            progress_metrics = {}
            
            for category, metrics in baseline_comparison.items():
                category_improvements = []
                for metric, data in metrics.items():
                    if isinstance(data, dict) and "improvement" in data:
                        category_improvements.append(data["improvement"])
                
                if category_improvements:
                    progress_metrics[category] = {
                        "average_improvement": float(np.mean(category_improvements)),
                        "consistency": float(1.0 - np.std(category_improvements)),
                        "trend": self._calculate_trend(category_improvements)
                    }
            
            # Calculate overall progress score
            all_improvements = [
                m["improvement"]
                for c in baseline_comparison.values()
                for m in c.values()
                if isinstance(m, dict) and "improvement" in m
            ]
            
            if all_improvements:
                progress_metrics["overall"] = {
                    "score": float(np.mean(all_improvements)),
                    "confidence": float(min(1.0, len(all_improvements) / 20)),
                    "trend": self._calculate_trend(all_improvements)
                }
            
            return progress_metrics
            
        except Exception as e:
            logging.error(f"Error calculating progress metrics: {e}")
            return {}
    
    def _analyze_posture(self, data: Dict) -> Dict:
        """Analyze posture metrics in detail."""
        metrics = data.get('metrics', [])
        if not metrics:
            return {"error": "No metrics found"}
            
        # Calculate detailed posture metrics
        shoulder_alignment = [m['shoulder_alignment'] for m in metrics]
        back_straightness = [m['back_straightness'] for m in metrics]
        head_position = [m['head_position'] for m in metrics]
        neck_angle = [m['neck_angle'] for m in metrics]
        
        return {
            "shoulder_alignment": {
                "average": np.mean(shoulder_alignment),
                "variance": np.var(shoulder_alignment),
                "trend": self._calculate_trend(shoulder_alignment)
            },
            "back_straightness": {
                "average": np.mean(back_straightness),
                "variance": np.var(back_straightness),
                "trend": self._calculate_trend(back_straightness)
            },
            "head_position": {
                "average": np.mean(head_position),
                "variance": np.var(head_position),
                "trend": self._calculate_trend(head_position)
            },
            "neck_angle": {
                "average": np.mean(neck_angle),
                "variance": np.var(neck_angle),
                "trend": self._calculate_trend(neck_angle)
            }
        }
    
    def _analyze_speech(self, data: Dict) -> Dict:
        """Analyze speech patterns and metrics."""
        try:
            audio_file = Path(data.get('filepath', '')).with_suffix('.wav')
            if not audio_file.exists():
                return {"error": "Audio file not found"}
                
            # Load audio file
            audio = AudioSegment.from_wav(str(audio_file))
            
            # Calculate speech metrics
            return {
                "pitch": self._analyze_pitch(audio),
                "tone": self._analyze_tone(audio),
                "variance": self._analyze_variance(audio),
                "clarity": self._analyze_clarity(audio),
                "speaking_rate": self._calculate_speaking_rate(audio),
                "transcript": self._generate_transcript(audio)
            }
        except Exception as e:
            logging.error(f"Error analyzing speech: {e}")
            return {"error": str(e)}
    
    def _analyze_engagement(self, data: Dict) -> Dict:
        """Analyze overall engagement metrics."""
        metrics = data.get('metrics', [])
        if not metrics:
            return {"error": "No metrics found"}
            
        confidence_scores = [m.get('confidence', 0) for m in metrics]
        engagement_scores = [m.get('engagement', 0) for m in metrics]
        
        return {
            "overall_confidence": {
                "average": np.mean(confidence_scores),
                "variance": np.var(confidence_scores),
                "trend": self._calculate_trend(confidence_scores)
            },
            "engagement_level": {
                "average": np.mean(engagement_scores),
                "variance": np.var(engagement_scores),
                "trend": self._calculate_trend(engagement_scores)
            }
        }
    
    def _generate_suggestions(self, data: Dict) -> List[str]:
        """Generate improvement suggestions based on analysis."""
        suggestions = []
        
        # Analyze posture metrics
        posture = self._analyze_posture(data)
        if posture.get('shoulder_alignment', {}).get('average', 1) < 0.8:
            suggestions.append("Work on maintaining level shoulders during sessions")
        if posture.get('back_straightness', {}).get('average', 1) < 0.8:
            suggestions.append("Focus on maintaining a straighter back posture")
        if posture.get('head_position', {}).get('average', 1) < 0.8:
            suggestions.append("Try to keep your head more centered and level")
            
        # Analyze speech metrics
        speech = self._analyze_speech(data)
        if speech.get('clarity', {}).get('average', 1) < 0.8:
            suggestions.append("Work on clearer articulation in speech")
        if speech.get('variance', {}).get('score', 1) < 0.7:
            suggestions.append("Try to add more vocal variety in your speech")
            
        return suggestions
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values."""
        if len(values) < 2:
            return "insufficient_data"
            
        slope = np.polyfit(range(len(values)), values, 1)[0]
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"
    
    def _analyze_pitch(self, audio: AudioSegment) -> Dict:
        """Analyze pitch patterns in audio."""
        samples = np.array(audio.get_array_of_samples())
        return {
            "average": float(np.mean(samples)),
            "variance": float(np.var(samples)),
            "range": float(np.ptp(samples))
        }
    
    def _analyze_tone(self, audio: AudioSegment) -> Dict:
        """Analyze tone quality in audio."""
        samples = np.array(audio.get_array_of_samples())
        return {
            "warmth": self._calculate_warmth(samples),
            "brightness": self._calculate_brightness(samples),
            "clarity": self._calculate_clarity_score(samples)
        }
    
    def _analyze_variance(self, audio: AudioSegment) -> Dict:
        """Analyze variance in speech patterns."""
        samples = np.array(audio.get_array_of_samples())
        return {
            "dynamic_range": float(np.ptp(samples)),
            "variability": float(np.var(samples)),
            "score": float(min(1.0, np.var(samples) / (2 ** 30)))
        }
    
    def _analyze_clarity(self, audio: AudioSegment) -> Dict:
        """Analyze speech clarity."""
        samples = np.array(audio.get_array_of_samples())
        signal = samples[np.abs(samples) > np.mean(np.abs(samples))]
        noise = samples[np.abs(samples) <= np.mean(np.abs(samples))]
        
        snr = np.mean(np.abs(signal)) / (np.mean(np.abs(noise)) if len(noise) > 0 else 1)
        return {
            "signal_to_noise": float(snr),
            "average": float(min(1.0, snr / 10.0))
        }
    
    def _calculate_speaking_rate(self, audio: AudioSegment) -> float:
        """Calculate speaking rate from audio."""
        samples = np.array(audio.get_array_of_samples())
        energy = np.abs(samples)
        threshold = np.mean(energy) * 1.5
        speech_segments = np.where(energy > threshold)[0]
        
        if len(speech_segments) == 0:
            return 0.0
            
        segment_durations = np.diff(speech_segments)
        return float(np.mean(segment_durations) / audio.frame_rate)
    
    def _generate_transcript(self, audio: AudioSegment) -> str:
        """Generate transcript from audio using speech recognition."""
        try:
            recognizer = sr.Recognizer()
            with io.BytesIO() as wav_io:
                audio.export(wav_io, format="wav")
                with sr.AudioFile(wav_io) as source:
                    audio_data = recognizer.record(source)
                    return recognizer.recognize_google(audio_data)
        except Exception as e:
            logging.error(f"Error generating transcript: {e}")
            return "Transcript generation failed"
    
    def _calculate_warmth(self, samples: np.ndarray) -> float:
        """Calculate warmth score from audio samples."""
        return float(min(1.0, np.mean(np.abs(samples)) / (2 ** 15)))
    
    def _calculate_brightness(self, samples: np.ndarray) -> float:
        """Calculate brightness score from audio samples."""
        return float(min(1.0, np.var(samples) / (2 ** 30)))
    
    def _calculate_clarity_score(self, samples: np.ndarray) -> float:
        """Calculate clarity score from audio samples."""
        return float(min(1.0, np.mean(np.abs(samples)) / (2 ** 15)))
        
    def _analyze_multimodal_coherence(self, data: Dict) -> Dict:
        """Analyze coherence between verbal and non-verbal communication."""
        try:
            speech_data = self._analyze_speech(data)
            posture_data = self._analyze_posture(data)
            engagement_data = self._analyze_engagement(data)
            
            # Calculate temporal alignment
            speech_times = [m.get('timestamp') for m in data.get('metrics', [])]
            posture_times = [m.get('timestamp') for m in data.get('metrics', [])]
            
            # Analyze coherence metrics
            coherence_scores = []
            for i in range(len(speech_times)):
                speech_features = self._extract_speech_features(data, i)
                posture_features = self._extract_posture_features(data, i)
                coherence_scores.append(self._calculate_coherence(speech_features, posture_features))
            
            return {
                "overall_coherence": {
                    "average": float(np.mean(coherence_scores)),
                    "variance": float(np.var(coherence_scores)),
                    "trend": self._calculate_trend(coherence_scores)
                },
                "speech_posture_alignment": self._analyze_alignment(speech_data, posture_data),
                "engagement_consistency": self._analyze_consistency(engagement_data)
            }
            
        except Exception as e:
            logging.error(f"Error analyzing multimodal coherence: {e}")
            return {"error": str(e)}
    
    def _extract_speech_features(self, data: Dict, index: int) -> Dict:
        """Extract speech features for coherence analysis."""
        metrics = data.get('metrics', [])[index]
        return {
            "speaking_rate": metrics.get('speaking_rate', 0),
            "pitch": metrics.get('pitch', 0),
            "clarity": metrics.get('clarity', 0)
        }
    
    def _extract_posture_features(self, data: Dict, index: int) -> Dict:
        """Extract posture features for coherence analysis."""
        metrics = data.get('metrics', [])[index]
        return {
            "shoulder_alignment": metrics.get('shoulder_alignment', 0),
            "back_straightness": metrics.get('back_straightness', 0),
            "head_position": metrics.get('head_position', 0)
        }
    
    def _calculate_coherence(self, speech_features: Dict, posture_features: Dict) -> float:
        """Calculate coherence score between speech and posture features."""
        # Normalize features
        speech_values = np.array(list(speech_features.values()))
        posture_values = np.array(list(posture_features.values()))
        
        # Calculate correlation
        correlation = np.corrcoef(speech_values, posture_values)[0, 1]
        return float(max(0, (correlation + 1) / 2))  # Convert to 0-1 scale
    
    def _analyze_alignment(self, speech_data: Dict, posture_data: Dict) -> Dict:
        """Analyze alignment between speech and posture patterns."""
        try:
            speech_patterns = self._identify_speech_patterns(speech_data)
            posture_patterns = self._identify_posture_patterns(posture_data)
            
            alignment_scores = []
            for sp in speech_patterns:
                for pp in posture_patterns:
                    if self._check_temporal_overlap(sp, pp):
                        alignment_scores.append(self._calculate_pattern_alignment(sp, pp))
            
            return {
                "score": float(np.mean(alignment_scores)) if alignment_scores else 0.0,
                "pattern_matches": len(alignment_scores),
                "confidence": float(min(1.0, len(alignment_scores) / 10))
            }
            
        except Exception as e:
            logging.error(f"Error analyzing alignment: {e}")
            return {"error": str(e)}
    
    def _identify_speech_patterns(self, speech_data: Dict) -> List[Dict]:
        """Identify significant speech patterns."""
        patterns = []
        metrics = speech_data.get('metrics', [])
        
        # Use sliding window to detect patterns
        window_size = 5
        for i in range(len(metrics) - window_size + 1):
            window = metrics[i:i + window_size]
            pattern = self._detect_speech_pattern(window)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def _identify_posture_patterns(self, posture_data: Dict) -> List[Dict]:
        """Identify significant posture patterns."""
        patterns = []
        metrics = posture_data.get('metrics', [])
        
        # Use sliding window to detect patterns
        window_size = 5
        for i in range(len(metrics) - window_size + 1):
            window = metrics[i:i + window_size]
            pattern = self._detect_posture_pattern(window)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def _detect_speech_pattern(self, window: List[Dict]) -> Optional[Dict]:
        """Detect a significant speech pattern in a window of metrics."""
        try:
            # Extract key metrics
            speaking_rates = [m.get('speaking_rate', 0) for m in window]
            clarity_scores = [m.get('clarity', {}).get('average', 0) for m in window]
            
            # Calculate pattern characteristics
            rate_trend = self._calculate_trend(speaking_rates)
            clarity_trend = self._calculate_trend(clarity_scores)
            
            if rate_trend != "stable" or clarity_trend != "stable":
                return {
                    "start_time": window[0].get('timestamp'),
                    "end_time": window[-1].get('timestamp'),
                    "rate_trend": rate_trend,
                    "clarity_trend": clarity_trend,
                    "confidence": float(min(1.0, np.mean(clarity_scores)))
                }
            
            return None
            
        except Exception as e:
            logging.error(f"Error detecting speech pattern: {e}")
            return None
    
    def _detect_posture_pattern(self, window: List[Dict]) -> Optional[Dict]:
        """Detect a significant posture pattern in a window of metrics."""
        try:
            # Extract key metrics
            alignments = [m.get('shoulder_alignment', 0) for m in window]
            straightness = [m.get('back_straightness', 0) for m in window]
            
            # Calculate pattern characteristics
            alignment_trend = self._calculate_trend(alignments)
            straightness_trend = self._calculate_trend(straightness)
            
            if alignment_trend != "stable" or straightness_trend != "stable":
                return {
                    "start_time": window[0].get('timestamp'),
                    "end_time": window[-1].get('timestamp'),
                    "alignment_trend": alignment_trend,
                    "straightness_trend": straightness_trend,
                    "confidence": float(min(1.0, np.mean(alignments)))
                }
            
            return None
            
        except Exception as e:
            logging.error(f"Error detecting posture pattern: {e}")
            return None
    
    def _check_temporal_overlap(self, pattern1: Dict, pattern2: Dict) -> bool:
        """Check if two patterns overlap in time."""
        start1 = datetime.fromisoformat(pattern1['start_time'])
        end1 = datetime.fromisoformat(pattern1['end_time'])
        start2 = datetime.fromisoformat(pattern2['start_time'])
        end2 = datetime.fromisoformat(pattern2['end_time'])
        
        return (start1 <= end2) and (start2 <= end1)
    
    def _calculate_pattern_alignment(self, speech_pattern: Dict, posture_pattern: Dict) -> float:
        """Calculate alignment score between speech and posture patterns."""
        # Compare trend directions
        speech_trends = [speech_pattern['rate_trend'], speech_pattern['clarity_trend']]
        posture_trends = [posture_pattern['alignment_trend'], posture_pattern['straightness_trend']]
        
        # Calculate trend alignment
        trend_matches = sum(1 for st in speech_trends for pt in posture_trends if st == pt)
        trend_score = trend_matches / (len(speech_trends) * len(posture_trends))
        
        # Weight by confidence
        confidence = min(speech_pattern['confidence'], posture_pattern['confidence'])
        
        return float(trend_score * confidence)
    
    def _analyze_consistency(self, engagement_data: Dict) -> Dict:
        """Analyze consistency of engagement patterns."""
        try:
            metrics = engagement_data.get('metrics', [])
            if not metrics:
                return {"error": "No engagement metrics found"}
            
            # Calculate engagement stability
            engagement_scores = [m.get('engagement', 0) for m in metrics]
            confidence_scores = [m.get('confidence', 0) for m in metrics]
            
            # Detect significant changes
            changes = self._detect_significant_changes(engagement_scores)
            
            return {
                "stability": {
                    "score": float(1.0 - np.std(engagement_scores)),
                    "confidence": float(np.mean(confidence_scores))
                },
                "changes": changes,
                "trend": self._calculate_trend(engagement_scores)
            }
            
        except Exception as e:
            logging.error(f"Error analyzing consistency: {e}")
            return {"error": str(e)}
    
    def _detect_significant_changes(self, scores: List[float]) -> List[Dict]:
        """Detect significant changes in a series of scores."""
        changes = []
        window_size = 3
        threshold = 0.2  # 20% change threshold
        
        for i in range(len(scores) - window_size + 1):
            window = scores[i:i + window_size]
            avg_before = np.mean(window[:window_size//2])
            avg_after = np.mean(window[window_size//2:])
            
            if abs(avg_after - avg_before) > threshold:
                changes.append({
                    "index": i + window_size//2,
                    "magnitude": float(avg_after - avg_before),
                    "confidence": float(min(1.0, abs(avg_after - avg_before) / threshold))
                })
        
        return changes 