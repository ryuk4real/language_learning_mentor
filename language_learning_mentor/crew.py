from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools.email_sender import EmailSender
from tools.calculator import QuizCalculator


@CrewBase
class LanguageMentor():
    """Language Learning Mentor Crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def level_detector(self) -> Agent:
        return Agent(
            config=self.agents_config['level_detector'],
            tools=[QuizCalculator()],
            verbose=True
        )

    @agent
    def tip_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['tip_agent'],
            tools=[EmailSender()],
            verbose=True
        )

    @agent
    def quiz_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['quiz_agent'],
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
