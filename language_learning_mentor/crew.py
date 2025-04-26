from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools.email_sender import EmailSender
from tools.calculator import QuizCalculator
from pathlib import Path
from langchain_groq import ChatGroq
import yaml
from dotenv import load_dotenv

@CrewBase
class LanguageMentor():
    """Language Learning Mentor Crew"""
    def __init__(self):
        load_dotenv()
        self.agents_config = yaml.safe_load(Path('config/agents.yaml').read_text())
        self.tasks_config = yaml.safe_load(Path('config/tasks.yaml').read_text())
        self.task_templates = {}

    def _make_groq_llm(self, cfg: dict, extra_system_message: str = None) -> ChatGroq:
        print(f"[DEBUG] Creating Groq LLM with config: {cfg}")
        base_system_message =  """ 
        SEMPRE rispondi seguendo questo formato:

            Thought: [Pensa a cosa devi fare]
            Action: [Nome esatto del tool da usare, ad esempio "Email Sender"]
            Action Input: {"recipient": "email", "subject": "oggetto", "body": "testo"}
            Observation: [Risultato dell'azione]
            
            DOPO ogni Observation devi SEMPRE scrivere:
            
            Thought: I now know the final answer
            Final Answer: [Risposta finale da inviare all'utente]
            
            NON scrivere nulla fuori da questo schema. NON saltare nessuna parte. NON lasciare il Final Answer vuoto.
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
        llm = self._make_groq_llm(cfg)  # <- adesso va bene, extra_system_message è opzionale
        return Agent(
            role=cfg['role'],
            goal=cfg['goal'],
            backstory=cfg['backstory'],
            llm=llm,
            tools=[QuizCalculator()],
            verbose=True
        )

    def tip_agent(self) -> Agent:
        cfg = self.agents_config['tip_agent']
        llm = self._make_groq_llm(cfg,
                                  extra_system_message="Quando l'utente specifica una lingua, devi SEMPRE rispondere esclusivamente in quella lingua.")
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
