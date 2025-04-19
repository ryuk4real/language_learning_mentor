from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools.email_sender import EmailSender
from tools.calculator import QuizCalculator
from pathlib import Path
from groq import Groq
from langchain_groq import ChatGroq
import os, yaml
from dotenv import load_dotenv


@CrewBase
class LanguageMentor():
    """Language Learning Mentor Crew"""
    load_dotenv() 
    agents_config = yaml.safe_load(Path('config/agents.yaml').read_text())
    tasks_config = yaml.safe_load(Path('config/tasks.yaml').read_text())

    def _make_groq_llm(self, cfg: dict) -> ChatGroq:
        return ChatGroq(
            model=cfg['model_name'],
            temperature=cfg.get('temperature', 0.0),
            api_key=os.getenv("GROQ_KEY")
        )

    @agent
    def level_detector(self) -> Agent:
        cfg = self.agents_config['level_detector']
        llm = self._make_groq_llm(cfg)
        return Agent(
            llm=llm,
            tools=[QuizCalculator()],
            verbose=True
        )

    @agent
    def tip_agent(self) -> Agent:
        cfg = self.agents_config['tip_agent']
        llm = self._make_groq_llm(cfg)
        return Agent(
            llm=llm,
            tools=[EmailSender()],
            verbose=True
        )

    @agent
    def quiz_agent(self) -> Agent:
        cfg = self.agents_config['quiz_agent']
        llm = self._make_groq_llm(cfg)
        return Agent(
            llm=llm,
            tools=[QuizCalculator(), EmailSender()],
            verbose=True
        )

    @task
    def level_task(self) -> Task:
        return Task(
            config=self.tasks_config['level_task']
        )

    @task
    def tip_task(self) -> Task:
        return Task(
            config=self.tasks_config['tip_task']
        )

    @task
    def quiz_task(self) -> Task:
        return Task(
            config=self.tasks_config['quiz_task'],
            output_file='quiz_score.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
