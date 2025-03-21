"""Multi-agent system implementation for productivity enhancement."""
import asyncio
import datetime
import logging
import webbrowser
from urllib.parse import quote_plus
from typing import List, Dict, Any
import ollama
import pytz
import time

class BaseAgent:
    def __init__(self, model_name: str, system_prompt: str):
        self.model_name = model_name
        self.system_prompt = system_prompt
        
    async def query(self, prompt: str) -> str:
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                system=self.system_prompt
            )
            return response['response']
        except Exception as e:
            logging.error(f"Error querying Ollama: {e}")
            return f"Error: {str(e)}"
        
    async def research(self, query):
        query = quote_plus(query)
        return webbrowser.open(
            f"https://www.google.com/search?q={query}"
        )
    
    async def reason(self, task="check csv file for details", time=None, use_csv=False, queries=None):
        """
        Time in seconds
        """
        def get_queries(queries, time):
            if time:
                start = datetime.now()
                self.query('testing speeds.')
                end = datetime.now()
                return time // datetime.timedelta(start, end)
            return queries

        def generate_inital_prompt(task, queries):
            return (
                f"""
                Your task is to do: {task}
                You have {queries} questions you can ask yourself. Think of them as a chain of thought framework where your goal is to finish a task or delegate further tasks. 
                Include the phrase:
                {r"<<RESEARCH:'YOURQUERYHERE'>>"} to search the web
                Include the phrase:
                {r"<<REASON:'YOURQUERYHERE'>>"} to think something through. 
                """    
            )

        def generate_prompt(task, queries, history):
            return (
                f"""
                Your task is to do: {task}
                You now have {queries} questions you can ask yourself or the web. Think of queries to yourself as a chain of thought framework where your goal is to finish a task or delegate further tasks. 
                For example if you wanted to add 23 + 55
                1(3+8)+10(5+2)
                you would need two queries as it is a two step equation
                Include the phrase:
                {r"<<RESEARCH>>"} to search the web
                Include the phrase:
                {r"<<REASON>>"} to think something through. 
                Here is the previous conversation history:
                {history}
                """    
            )

        def get_tasks():
            pass

        def process_response():
            pass

        def begin_reasoning(self, history, queries, task, inital_prompt):
            actions = {
                "<<RESEARCH>>": self.research,
                "<<REASON>>": self.reason
            }
            active_tool = '<<REASON>>'
            mappings = {
                '<<RESEARCH>>': 'research',
                '<<REASON>>': 'reason'
            }

            for used_queries in range(queries, 1, -1):
                if mappings[active_tool] == 'reason':
                    query = generate_prompt(task, used_queries, history)
                    response = self.query()
                    history[query] = response
                    if '<<REASON>>' not in response:
                       list_response = list(response)
                       for i in range(0, len(list_response)-1, 2):
                            if '<' in [list_response[i], list_response[i+1]]:
                                if list_response[i] == list_response[i+1]:
                                    for i in range(6+i):
                                        list_response.pop(0)
                                else:
                                    pass # TODO: Complete this

                                for i in range(len(list_response) - 1, 0, 2):
                                    if '>' in [list_response[i], list_response[i+1]]:
                                        if list_response[i] == list_response[i+1]:
                                            iterations = len(list_response) - 1 - i - 1
                                            for i in range(iterations):
                                                list_response.pop(len(list_response-1))
                else:
                    response = self.research(query)
                    

        
        # Initialize starting variables
        history = {}
        queries = get_queries()
        task = get_tasks()
        inital_prompt = generate_inital_prompt(task, queries)

        # Start loop
        self.begin_reasoning(history, queries, task, inital_prompt)
    
  
                  
            
        

        

class ProductManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            'llama2:7b',
            "You are a Product Manager AI focused on improving human productivity. You coordinate research and insights to generate actionable plans."
        )
        self.next_meeting_time = None
        self.questions_for_user: List[str] = []
        self.action_items: List[str] = []
        
    def set_next_meeting(self, time_str: str = "07:30"):
        """Set next meeting time to 7:30 AM tomorrow if today's has passed."""
        now = datetime.datetime.now(pytz.UTC)
        today_meeting = now.replace(
            hour=int(time_str.split(":")[0]),
            minute=int(time_str.split(":")[1]),
            second=0,
            microsecond=0
        )
        
        self.next_meeting_time = today_meeting if now < today_meeting else today_meeting + datetime.timedelta(days=1)
        
    def time_until_meeting(self) -> datetime.timedelta:
        """Calculate time remaining until next meeting."""
        if not self.next_meeting_time:
            self.set_next_meeting()
        return self.next_meeting_time - datetime.datetime.now(pytz.UTC)

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            'llama2:250m',
            "You are a Research AI focused on gathering and analyzing productivity-related information."
        )
        
    async def research_topic(self, topic: str) -> str:
        """Research a specific productivity-related topic."""
        return await self.query(f"Research the following productivity topic and provide key findings: {topic}")
    def search(self, query):
        query = quote_plus(query)
        url = f"https://www.google.com/search?q={query}"
        return webbrowser.open(url)

class InsightsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            'llama2:250m',
            "You are an Insights AI focused on analyzing productivity data and generating actionable insights."
        )
        
    async def analyze_data(self, data: str) -> Dict[str, Any]:
        """Analyze research data and generate insights."""
        response = await self.query(f"Analyze this productivity data and provide actionable insights: {data}")
        # TODO: Parse response into structured insights
        return {"raw_insights": response}

class MultiAgentSystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pm_agent = ProductManagerAgent()
        self.research_agent = ResearchAgent()
        self.insights_agent = InsightsAgent()
        self.research_topics: List[str] = [
            "time management techniques",
            "productivity tools and systems",
            "habit formation",
            "focus and concentration improvement",
            "energy management",
            "task prioritization methods"
        ]
        
    async def initialize(self):
        """Initialize the multi-agent system."""
        self.pm_agent.set_next_meeting()
        logging.info(f"Next meeting scheduled for: {self.pm_agent.next_meeting_time}")
        await self.start_continuous_research()
        
    async def start_continuous_research(self):
        """Start continuous research loop."""
        while True:
            time_remaining = self.pm_agent.time_until_meeting()
            logging.info(f"Time until next meeting: {time_remaining}")
            
            # Prioritize research based on remaining time
            for topic in self.research_topics:
                research_data = await self.research_agent.research_topic(topic)
                insights = await self.insights_agent.analyze_data(research_data)
                
                # Generate questions for unknown areas
                questions = await self.generate_questions(insights)
                self.pm_agent.questions_for_user.extend(questions)
                
                # Sleep briefly to prevent overwhelming the system
                await asyncio.sleep(1)
                
            # Check if it's almost meeting time
            if time_remaining.total_seconds() < 300:  # 5 minutes before meeting
                await self.prepare_for_meeting()
                await asyncio.sleep(300)  # Wait for next cycle
            else:
                await asyncio.sleep(600)  # Check every 10 minutes
                
    async def generate_questions(self, insights: Dict[str, Any]) -> List[str]:
        """Generate questions for unknown areas based on insights."""
        prompt = f"Based on these insights, what questions should we ask the user to improve their productivity?\nInsights: {insights['raw_insights']}"
        response = await self.pm_agent.query(prompt)
        # TODO: Parse response into list of questions
        return [response]  # Simplified for now
        
    async def prepare_for_meeting(self):
        """Prepare for the morning meeting with the user."""
        # Summarize findings and prepare action items
        all_questions = self.pm_agent.questions_for_user
        self.pm_agent.questions_for_user = []  # Clear for next cycle
        
        # Generate actionable recommendations
        prompt = f"Based on our research and these questions: {all_questions}, generate specific actionable recommendations for the user's day."
        recommendations = await self.pm_agent.query(prompt)
        self.pm_agent.action_items = [recommendations]  # Simplified for now
        
    async def cleanup(self):
        """Clean up system resources."""
        # Implement cleanup logic here
        pass

    def _parse_insights(self, response: str) -> Dict:
        """Parse response into structured insights."""
        try:
            # Split response into sections
            sections = response.split('\n\n')
            insights = {}
            
            for section in sections:
                if not section.strip():
                    continue
                    
                # Extract section title and content
                lines = section.split('\n')
                title = lines[0].strip().lower().replace(':', '')
                content = '\n'.join(lines[1:]).strip()
                
                # Parse content based on section type
                if title == 'key findings':
                    insights['key_findings'] = self._parse_list(content)
                elif title == 'improvements':
                    insights['improvements'] = self._parse_list(content)
                elif title == 'recommendations':
                    insights['recommendations'] = self._parse_list(content)
                elif title == 'next steps':
                    insights['next_steps'] = self._parse_list(content)
                else:
                    insights[title] = content
            
            return {
                'insights': insights,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error parsing insights: {e}")
            return {'error': str(e)}
    
    def _parse_list(self, content: str) -> List[str]:
        """Parse content into a list of items."""
        items = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('*'):
                items.append(line[1:].strip())
            elif line:
                items.append(line)
        return items
    
    def _generate_questions(self, response: str) -> List[str]:
        """Parse response into list of questions."""
        try:
            # Split response into sections
            sections = response.split('\n\n')
            questions = []
            
            for section in sections:
                if not section.strip():
                    continue
                
                # Look for question markers
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    # Check for question markers
                    if line.endswith('?') or line.startswith('Q:') or line.startswith('Question:'):
                        # Clean up the question
                        question = line
                        if question.startswith('Q:'):
                            question = question[2:].strip()
                        elif question.startswith('Question:'):
                            question = question[8:].strip()
                        questions.append(question)
            
            return questions
            
        except Exception as e:
            logging.error(f"Error generating questions: {e}")
            return []

if __name__ == "__main__":
    config = {
        "meeting_time": "07:30",
        "timezone": "UTC",
        # Add other configuration options as needed
    }
    
    system = MultiAgentSystem(config)
    try:
        asyncio.run(system.initialize())
    except KeyboardInterrupt:
        asyncio.run(system.cleanup())