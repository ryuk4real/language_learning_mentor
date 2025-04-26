import threading
import json
from crewai import Crew, Process
from crewai.project import CrewBase, agent, crew, task
from tools.calculator import QuizCalculator
from tools.email_sender import EmailSender
from crew import LanguageMentor

class LanguageProcessor:
    """
    Handles language-specific logic by delegating to CrewAI tasks and agents.
    Runs potentially blocking calls in background threads to keep the UI responsive.
    """
    def __init__(self):
        self.language_crew = LanguageMentor()

    def _run_single_task(self, task_obj, input_variables: dict) -> str:
        """
        Helper per creare una Crew temporanea e farla girare con input dinamico.
        """
        template = self.language_crew.task_templates.get(task_obj.description)

        if template:
            input_text = template
            for key, value in input_variables.items():
                input_text = input_text.replace(f"{{{{ {key} }}}}", str(value))
            input_variables["task"] = input_text
            print(f"[DEBUG] Generated input from template: {input_text}")

        temp_crew = Crew(
            agents=[task_obj.agent],
            tasks=[task_obj],
            process=Process.sequential,
            verbose=True
        )

        print(f"[DEBUG] Running task with input variables: {input_variables}")
        result = temp_crew.kickoff(inputs=input_variables)

        print(f"[DEBUG] Raw result from Crew: {result}")

        return result

    def generate_daily_tip(self, user_level: str, user_language: str) -> str:
        """
        Generate a daily language learning tip using the tip_agent inside a Crew.
        """
        tip_task = self.language_crew.tip_task()

        print("*"*50)
        print(f"Generating daily tip for level: {user_level}, language: {user_language}")
        print("*"*50)

        response = self._run_single_task(
            tip_task,
            input_variables={
                "user_level": user_level,
                "language": user_language,
                "task": "Generate a daily language learning tip"
            }
        )
        return str(response).strip()

    def prepare_quiz_data(self, user_level: str, user_language: str, num_questions: int = 5) -> list:
        """
        Create a language quiz using the quiz_agent inside a Crew.
        """
        quiz_task = self.language_crew.quiz_task()
        response = self._run_single_task(
            quiz_task,
            input_variables={
                "user_level": user_level,
                "language": user_language,
                "num_questions": num_questions,
                "task": "Create a language quiz"
            }
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{
                "question": "Error generating quiz",
                "options": ["Please try again later"],
                "correct_answer": 0
            }]

    def analyze_proficiency(self, user_input: str, user_level: str, user_language: str) -> dict:
        """
        Analyze language proficiency using the level_detector agent inside a Crew.
        """
        level_task = self.language_crew.level_task()
        response = self._run_single_task(
            level_task,
            input_variables={
                "text": user_input,
                "current_level": user_level,
                "language": user_language
            }
        )

        feedback = ""
        estimated_level = user_level

        if isinstance(response, dict):
            feedback = response.get('feedback', '')
            estimated_level = response.get('estimated_level', user_level)
        else:
            feedback = str(response)
            estimated_level = self._extract_level_from_response(feedback, user_level)

        return {
            'feedback': feedback,
            'estimated_level': estimated_level
        }

    def _extract_level_from_response(self, response, default_level):
        """Helper to try to extract the estimated level from the response text."""
        response_text = str(response).lower()
        if "beginner" in response_text:
            return "Beginner"
        elif "intermediate" in response_text:
            return "Intermediate"
        elif "advanced" in response_text:
            return "Advanced"
        elif "proficient" in response_text:
            return "Proficient"
        elif "master" in response_text:
            return "Master"
        return default_level
