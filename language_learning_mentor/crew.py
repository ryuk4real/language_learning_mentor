from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools.email_sender import EmailSender
from tools.calculator import QuizCalculator
from pathlib import Path
from langchain_groq import ChatGroq
import yaml
from dotenv import load_dotenv
import os

@CrewBase
class LanguageMentor():
    """Language Learning Mentor Crew"""
    def __init__(self):
        load_dotenv()
        
        # Get the directory where this script is located
        script_dir = Path(__file__).resolve().parent
        
        # Define paths relative to the script's location
        agents_config_path = script_dir.parent / "language_learning_mentor" / "config" / "agents.yaml"
        tasks_config_path = script_dir.parent / "language_learning_mentor" / "config" / "tasks.yaml"
        
        # Load YAML files
        self.agents_config = yaml.safe_load(agents_config_path.read_text())
        self.tasks_config = yaml.safe_load(tasks_config_path.read_text())
        self.task_templates = {}

    def _make_groq_llm(self, cfg: dict) -> ChatGroq:
        print(f"[DEBUG] Creating Groq LLM with config: {cfg}") 
        return ChatGroq(
            model=f"groq/{cfg['model_name']}",
            temperature=cfg.get('temperature', 0.0),
            base_url="https://api.groq.com/openai/v1",
        )

    @agent
    def level_detector(self) -> Agent:
        cfg = self.agents_config['level_detector']
        llm = self._make_groq_llm(cfg)
        return Agent(
            role=cfg['role'],
            goal=cfg['goal'],
            backstory=cfg['backstory'],
            llm=llm,
            tools=[QuizCalculator()],
            verbose=True
        )

    @agent
    def tip_agent(self) -> Agent:
        cfg = self.agents_config['tip_agent']
        llm = self._make_groq_llm(cfg)
        return Agent(
            role=cfg['role'],
            goal=cfg['goal'],
            backstory=cfg['backstory'] + " Always reply exclusively in the target language specified by the user.", # Qui sto forzando la lingua, ma non lo prende
            llm=llm,
            tools=[EmailSender()],
            verbose=True
        )

    @agent
    def quiz_agent(self) -> Agent:
        cfg = self.agents_config['quiz_agent']
        llm = self._make_groq_llm(cfg)
        return Agent(
            role=cfg['role'],
            goal=cfg['goal'],
            backstory=cfg['backstory'],
            llm=llm,
            tools=[QuizCalculator(), EmailSender()],
            verbose=True
        )

    @task
    def level_task(self) -> Task:
        task_cfg = self.tasks_config['level_task']
        t = Task(
            description=task_cfg['description'],
            expected_output=task_cfg['expected_output'],
            agent=self.level_detector()
        )
        self.task_templates[t.description] = task_cfg.get('input_template')
        return t

    @task
    def tip_task(self) -> Task:
        task_cfg = self.tasks_config['tip_task']
        t = Task(
            description=task_cfg['description'],
            expected_output=task_cfg['expected_output'],
            agent=self.tip_agent()
        )
        self.task_templates[t.description] = task_cfg.get('input_template')
        return t

    @task
    def quiz_task(self) -> Task:
        task_cfg = self.tasks_config['quiz_task']
        t = Task(
            description=task_cfg['description'],
            expected_output=task_cfg['expected_output'],
            agent=self.quiz_agent(),
            output_file='quiz_score.md'
        )
        self.task_templates[t.description] = task_cfg.get('input_template')
        return t

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

    def get_crew_methods(self):
        """Debug method to check available methods on the Crew object"""
        crew = self.language_crew.crew()
        methods = [method for method in dir(crew) if not method.startswith('_')]
        print(f"Available Crew methods: {methods}")
        return methods
