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
import asyncio

# Add test mode flag
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"

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

    async def _collect_responses(self, data: Dict) -> Dict:
        """Collect and analyze responses."""
        try:
            # Get questions and responses
            questions = data.get('questions', [])
            responses = []
            
            for question in questions:
                # Generate response using LLM
                prompt = f"""
                Provide a thoughtful response to this question:
                {question}
                
                Consider:
                1. Personal development goals
                2. Previous experiences
                3. Current challenges
                4. Future aspirations
                """
                
                response = self.ollama.generate(
                    model='llama2',
                    prompt=prompt,
                    system="You are a personal development coach providing thoughtful responses."
                )
                
                responses.append({
                    'question': question,
                    'response': response['response'],
                    'timestamp': datetime.now().isoformat()
                })
            
            # Analyze response patterns
            analysis = self._analyze_responses(responses)
            
            return {
                'responses': responses,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error collecting responses: {e}")
            return {'error': str(e)}
    
    async def _analyze_recording(self, recording_data: Dict) -> Dict:
        """Analyze recording data for insights."""
        try:
            # Extract metrics from recording data
            metrics = recording_data.get('analysis_data', {}).get('metrics', [])
            if not metrics:
                return {"error": "No metrics found in recording data"}
            
            # Calculate averages and trends
            analysis = {
                'speaking_rate': self._calculate_average_and_trend([m.get('speaking_rate', 0) for m in metrics]),
                'clarity': self._calculate_average_and_trend([m.get('clarity', 0) for m in metrics]),
                'confidence': self._calculate_average_and_trend([m.get('confidence', 0) for m in metrics]),
                'engagement': self._calculate_average_and_trend([m.get('engagement', 0) for m in metrics])
            }
            
            # Identify patterns and anomalies
            patterns = self._identify_patterns(metrics)
            anomalies = self._detect_anomalies(metrics)
            
            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(analysis, patterns, anomalies)
            
            return {
                'analysis': analysis,
                'patterns': patterns,
                'anomalies': anomalies,
                'suggestions': suggestions,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing recording: {e}")
            return {'error': str(e)}
    
    def _calculate_average_and_trend(self, values: List[float]) -> Dict:
        """Calculate average and trend of a metric."""
        if not values:
            return {'average': 0, 'trend': 'stable'}
        
        average = sum(values) / len(values)
        
        # Calculate trend using linear regression
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            trend = 'increasing'
        elif slope < -0.1:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'average': float(average),
            'trend': trend
        }
    
    def _identify_patterns(self, metrics: List[Dict]) -> List[Dict]:
        """Identify patterns in metrics."""
        patterns = []
        
        # Look for consistent patterns
        for metric in ['speaking_rate', 'clarity', 'confidence', 'engagement']:
            values = [m.get(metric, 0) for m in metrics]
            if len(values) >= 3:
                # Check for consistent improvement
                if all(values[i] <= values[i+1] for i in range(len(values)-1)):
                    patterns.append({
                        'type': 'consistent_improvement',
                        'metric': metric,
                        'confidence': 0.8
                    })
                # Check for consistent decline
                elif all(values[i] >= values[i+1] for i in range(len(values)-1)):
                    patterns.append({
                        'type': 'consistent_decline',
                        'metric': metric,
                        'confidence': 0.8
                    })
        
        return patterns
    
    def _detect_anomalies(self, metrics: List[Dict]) -> List[Dict]:
        """Detect anomalies in metrics."""
        anomalies = []
        
        for metric in ['speaking_rate', 'clarity', 'confidence', 'engagement']:
            values = [m.get(metric, 0) for m in metrics]
            if len(values) >= 3:
                mean = np.mean(values)
                std = np.std(values)
                
                # Detect values more than 2 standard deviations from mean
                for i, value in enumerate(values):
                    if abs(value - mean) > 2 * std:
                        anomalies.append({
                            'metric': metric,
                            'value': float(value),
                            'timestamp': metrics[i].get('timestamp'),
                            'severity': 'high' if abs(value - mean) > 3 * std else 'medium'
                        })
        
        return anomalies
    
    def _generate_improvement_suggestions(self, analysis: Dict, patterns: List[Dict], anomalies: List[Dict]) -> List[str]:
        """Generate improvement suggestions based on analysis."""
        suggestions = []
        
        # Analyze trends
        for metric, data in analysis.items():
            if data['trend'] == 'decreasing':
                suggestions.append(f"Your {metric.replace('_', ' ')} has been declining. Consider practicing more to maintain consistency.")
            elif data['trend'] == 'increasing':
                suggestions.append(f"Great progress in {metric.replace('_', ' ')}! Keep up the good work.")
        
        # Address patterns
        for pattern in patterns:
            if pattern['type'] == 'consistent_decline':
                suggestions.append(f"Your {pattern['metric'].replace('_', ' ')} has been consistently declining. Consider reviewing your approach.")
        
        # Address anomalies
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                suggestions.append(f"Significant fluctuation detected in {anomaly['metric'].replace('_', ' ')}. Review what might have caused this change.")
        
        return suggestions

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
        self.logger = logging.getLogger(__name__)
        self.latest_recording = None
        self.analysis_results = []
        
    async def analyze_latest_recording(self) -> Dict:
        """Analyze the most recent recording session."""
        try:
            self.logger.info("Starting analysis of latest recording...")
            
            # In test mode, return mock analysis results
            if TEST_MODE:
                self.logger.info("TEST MODE: Returning mock analysis results")
                return self._generate_mock_analysis_results()
                
            # Find the latest recording
            recordings_dir = Path("data/recordings")
            if not recordings_dir.exists() or not any(recordings_dir.iterdir()):
                return {"error": "No recordings found"}
            
            # Get the latest recording file
            latest_recording = max(
                [f for f in recordings_dir.iterdir() if f.is_file()], 
                key=lambda x: x.stat().st_mtime
            )
            
            self.logger.info(f"Analyzing recording: {latest_recording}")
            
            # TODO: Implement actual analysis logic
            # This would include:
            # 1. Processing the video for posture analysis
            # 2. Processing the audio for speech analysis
            # 3. Extracting engagement metrics
            # 4. Multimodal analysis
            
            # For now, return a placeholder result
            return {
                "status": "success",
                "recording": str(latest_recording),
                "timestamp": datetime.now().isoformat(),
                "posture_analysis": {
                    "shoulder_alignment": {
                        "average": 0.85,
                        "min": 0.72,
                        "max": 0.94,
                        "trend": "improving"
                    },
                    "head_position": {
                        "average": 0.78,
                        "min": 0.65,
                        "max": 0.89,
                        "trend": "stable"
                    }
                },
                "speech_analysis": {
                    "clarity": {
                        "average": 0.82,
                        "min": 0.75,
                        "max": 0.90
                    },
                    "speaking_rate": 145.3,  # words per minute
                    "transcript": "This is a placeholder transcript."
                },
                "improvement_suggestions": [
                    "Consider maintaining more consistent eye contact",
                    "Practice slower speech during complex explanations",
                    "Work on reducing filler words like 'um' and 'uh'"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error during recording analysis: {e}")
            return {"error": str(e)}
            
    def _generate_mock_analysis_results(self) -> Dict:
        """Generate mock analysis results for testing."""
        return {
            "status": "success",
            "recording": "data/recordings/mock_recording.mp4",
            "timestamp": datetime.now().isoformat(),
            "posture_analysis": {
                "shoulder_alignment": {
                    "average": 0.85,
                    "min": 0.72,
                    "max": 0.94,
                    "trend": "improving"
                },
                "head_position": {
                    "average": 0.78,
                    "min": 0.65,
                    "max": 0.89,
                    "trend": "stable"
                },
                "spine_curvature": {
                    "average": 0.92,
                    "min": 0.85,
                    "max": 0.97,
                    "trend": "excellent"
                },
                "gesture_fluidity": {
                    "average": 0.75,
                    "min": 0.65,
                    "max": 0.85,
                    "trend": "improving"
                }
            },
            "speech_analysis": {
                "clarity": {
                    "average": 0.82,
                    "min": 0.75,
                    "max": 0.90
                },
                "speaking_rate": 145.3,  # words per minute
                "pitch": {
                    "average": 125.6,  # Hz
                    "variance": 25.3,
                    "modulation": 0.78
                },
                "tone": {
                    "warmth": 0.76,
                    "brightness": 0.82,
                    "clarity": 0.85
                },
                "transcript": "This is a mock transcript for testing purposes. The speech flows well and demonstrates good articulation with some areas for improvement in pacing and emphasis."
            },
            "engagement_analysis": {
                "eye_contact": {
                    "average": 0.72,
                    "min": 0.60,
                    "max": 0.85,
                    "trend": "needs improvement"
                },
                "facial_expressiveness": {
                    "average": 0.80,
                    "min": 0.70,
                    "max": 0.90,
                    "trend": "good"
                },
                "response_time": {
                    "average": 1.8,  # seconds
                    "min": 0.9,
                    "max": 3.2,
                    "trend": "stable"
                }
            },
            "multimodal_analysis": {
                "overall_coherence": {
                    "average": 0.83,
                    "trend": "improving"
                },
                "speech_posture_alignment": {
                    "score": 0.77,
                    "pattern_matches": 12
                }
            },
            "progress_metrics": {
                "overall": {
                    "score": 0.81,
                    "confidence": 0.85,
                    "trend": "positive"
                },
                "posture": {
                    "average_improvement": 0.05,
                    "consistency": 0.82,
                    "trend": "steady improvement"
                },
                "speech": {
                    "average_improvement": 0.08,
                    "consistency": 0.76,
                    "trend": "fluctuating"
                },
                "engagement": {
                    "average_improvement": 0.04,
                    "consistency": 0.79,
                    "trend": "stable"
                },
                "multimodal": {
                    "average_improvement": 0.06,
                    "consistency": 0.80,
                    "trend": "improving"
                }
            },
            "improvement_suggestions": [
                "Practice maintaining more consistent eye contact during explanations",
                "Work on varying your speaking pace more intentionally for emphasis",
                "Reduce filler words like 'um' and 'uh' by pausing instead",
                "Incorporate more purposeful gestures to emphasize key points",
                "Practice deeper breathing to support longer phrases"
            ]
        } 