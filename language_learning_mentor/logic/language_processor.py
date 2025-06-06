import threading
import json
from crewai import Crew, Process
from crewai.project import CrewBase, agent, crew, task
from tools.calculator import QuizCalculator
from tools.email_sender import EmailSender
from crew import LanguageMentor
import os

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
            #print(f"[DEBUG] Generated input from template: {input_text}")
            task_obj.description = input_text

        # Crea una Crew temporanea con l'agente e il task specificato
        temp_crew = Crew(
            agents=[task_obj.agent],
            tasks=[task_obj],
            process=Process.sequential,
            verbose=True
        )

        #print(f"[DEBUG] Running task with input variables: {input_variables}")
        result = temp_crew.kickoff(inputs=input_variables)

        #print(f"[DEBUG] Raw result from Crew: {result}")

        return result

    def generate_daily_tip(self, user_level: str, user_language: str) -> str:
        """
        Generate a daily language learning tip using the tip_agent inside a Crew.
        """
        tip_task = self.language_crew.tip_task()

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
        If agent fails, return a basic fallback quiz.
        """
        quiz_task = self.language_crew.quiz_task()
        questions = []

        try:
            self._run_single_task(
                quiz_task,
                input_variables={
                    "user_level": user_level,
                    "language": user_language,
                    "num_questions": num_questions,
                    "task": f"Create a language quiz in the target language: {user_language}. Based on the user's level: {user_level}. The quiz should contain {num_questions} questions. Use the target language in the questions and answers."
                }
            )

            filepath = os.path.abspath("quizzes.json")
            with open(filepath, 'r', encoding='utf-8') as file:
                raw_quizzes = json.load(file)
            return raw_quizzes

        except Exception as e:
            print(f"Error calling quiz agent: {e}")
            return questions  


    def prepare_detect_quiz(self, user_level: str, user_language: str) -> list:
        """
        Analyze language proficiency using the level_detector agent inside a Crew.
        Returns a list of formatted quiz questions.
        """
        import json  # assicurati che ci sia

        level_task = self.language_crew.level_task()
        senteces = []

        try:
            response = self._run_single_task(
                level_task,
                input_variables={
                    "user_level": user_level,
                    "language": user_language,
                    "task": f"Create a language quiz to detect the user's level in the target language: {user_language}. You must use the target language in the questions and answers."
                }
            )

            filepath = os.path.abspath("level_assessment.json")
            with open(filepath, 'r', encoding='utf-8') as file:
                sentences = json.load(file)
                if isinstance(sentences, dict):
                    sentences = [sentences]
                return sentences
        except Exception as e:
            print(f"Error calling quiz agent: {e}")
            return senteces
        
             
