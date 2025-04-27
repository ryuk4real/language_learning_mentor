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

    def _make_groq_llm(self, cfg: dict, extra_system_message: str = None) -> ChatGroq:
        print(f"[DEBUG] Creating Groq LLM with config: {cfg}")
        base_system_message = """
        You must always follow this exact structure:

            Thought: [Think about what you need to do]
            Action: [Exact name of the tool to use, e.g., "Email Sender"]
            Action Input: {"recipient": "email", "subject": "subject", "body": "text"}
            Observation: [Result of the action]

            After each Observation you MUST immediately write:

            Thought: I now know the final answer
            Final Answer: [Final response to send to the user]

        Rules:
        - Never write anything outside this structure.
        - Never skip any step.
        - Never leave the Final Answer empty.
        - Always reason and respond in English internally.
        """

        if extra_system_message:
            base_system_message += f"\n{extra_system_message}"

        return ChatGroq(
            model=f"groq/{cfg['model_name']}",
            temperature=cfg.get('temperature', 0.2),
            base_url="https://api.groq.com/openai/v1",
            system_message=base_system_message
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
            max_iter=7,  # Limits reasoning steps
            max_retry_limit=1,  # Reduce retries
            verbose=True
        )

    def tip_agent(self) -> Agent:
        cfg = self.agents_config['tip_agent']
        llm = self._make_groq_llm(cfg,
            extra_system_message= """
                                    You must write the message exclusively in English.
                                    Provide a short motivational tip about learning the language {{ language }},
                                    and a cultural fact related to {{ language }}.
                                    Keep the text short, positive, and adapted to a {{ user_level }} user.
                                    Do not write in {{ language }}, only in English.
                                    Do not add any extra explanations or unrelated content.
                            """
                                  )

        return Agent(
            role=cfg['role'],
            goal=cfg['goal'],
            backstory=cfg['backstory'],
            llm=llm,
            tools=[EmailSender()],
            verbose=True
        )

    @agent
    def quiz_agent(self) -> Agent:
        cfg = self.agents_config['quiz_agent']
        llm = self._make_groq_llm(cfg)  # <- adesso va bene
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
            agent=self.level_detector(),
            output_file='level_assessment.json'
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
