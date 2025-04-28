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

    def _make_groq_llm(
                self,
                cfg: dict,
                extra_system_message: str | None = None,
                with_action_structure: bool = True
        ) -> ChatGroq:
            """
            Crea l'istanza di ChatGroq.

            Args:
                cfg: configurazione da agents.yaml
                extra_system_message: istruzioni aggiuntive
                with_action_structure: se False omette il prompt
                                       Thought/Action/Observation/Final Answer
            """
            base_system_message = ""
            if with_action_structure:
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
                    """.strip()

            if extra_system_message:
                base_system_message += "\n" + extra_system_message.strip()

            return ChatGroq(
                model=f"groq/{cfg['model_name']}",
                temperature=cfg.get("temperature", 0.2),
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
            verbose=True
        )


    @agent
    def tip_agent(self) -> Agent:
        cfg = self.agents_config["tip_agent"]

        # ❶ Prompt di sistema ben guidato con UN esempio
        extra_prompt = """
            You are the “Daily Tip Agent”.
        
            TASK
            ----
            Write ONE short motivational tip (1–3 sentences, in English) that helps the
            user learn the target language {{ language }}.  Adapt vocabulary and grammar
            to the learner’s level {{ user_level }}.
        
            RULES
            -----
            * Mention something specific about {{ language }} (a new word to learn, a verb, sound, cultural
              fact, spelling trick, etc.).
            * Keep it friendly and upbeat; max three sentences.
            * Keep it short; be clear and concise, but still creative in the generation of new infos.
            * Be creative and use topics that are useful for the user in their daily life.
            * Do NOT add greetings, apologies, hashtags, lists or markdown.
            * Respond **only** in the form:
        
            Final Answer: <your tip here>
        
            EXAMPLE
            -------
            (language = Italian, user_level = Beginner)
        
            Final Answer: Italian vowels always keep the same sound; read simple words
            like *ciao* and *amico* aloud to lock those clear vowels into muscle memory!
            """.strip()

        llm = self._make_groq_llm(
                cfg,
                extra_system_message=extra_prompt,
                with_action_structure=False  # niente Thought/Action
            )

        return Agent(
                role=cfg["role"],
                goal=cfg["goal"],
                backstory=cfg["backstory"],
                llm=llm,
                tools=[],  # nessun tool: basta il testo
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
