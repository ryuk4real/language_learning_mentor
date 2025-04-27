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
        If agent fails, return a basic fallback quiz.
        """
        quiz_task = self.language_crew.quiz_task()
        
        try:
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
                quiz_data = json.loads(response)
                # Validate quiz data structure
                if not self._validate_quiz_data(quiz_data):
                    raise ValueError("Invalid quiz data structure")
                return quiz_data
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error processing quiz data: {e}")
                return self._generate_fallback_quiz(user_level, user_language, num_questions)
        except Exception as e:
            print(f"Error calling quiz agent: {e}")
            return self._generate_fallback_quiz(user_level, user_language, num_questions)

    def _validate_quiz_data(self, quiz_data):
        """Validates that quiz data has the expected structure"""
        if not isinstance(quiz_data, list) or len(quiz_data) == 0:
            return False
        
        for question in quiz_data:
            # Check each question has required fields
            if not all(key in question for key in ["question", "options", "answer"]):
                return False
            if not isinstance(question["options"], list) or len(question["options"]) == 0:
                return False
        
        return True

    def _generate_fallback_quiz(self, user_level, user_language, num_questions=5):
        """
        Generates a basic fallback quiz when the agent fails.
        Uses basic language questions appropriate for the specified level and language.
        """
        fallback_quizzes = {
            "Italian": {
                "Beginner": [
                    {
                        "question": "What is 'hello' in Italian?",
                        "options": ["Ciao", "Arrivederci", "Grazie", "Scusa"],
                        "answer": "Ciao"
                    },
                    {
                        "question": "What is 'thank you' in Italian?",
                        "options": ["Per favore", "Grazie", "Scusa", "Prego"],
                        "answer": "Grazie"
                    },
                    {
                        "question": "Which is the correct translation for 'Good morning'?",
                        "options": ["Buona sera", "Buona notte", "Buon giorno", "Buon appetito"],
                        "answer": "Buon giorno"
                    },
                    {
                        "question": "How do you say 'yes' in Italian?",
                        "options": ["No", "Si", "Forse", "Bene"],
                        "answer": "Si"
                    },
                    {
                        "question": "What is 'please' in Italian?",
                        "options": ["Grazie", "Prego", "Per favore", "Scusa"],
                        "answer": "Per favore"
                    }
                ],
                "Intermediate": [
                    {
                        "question": "Choose the correct form: 'I eat' in Italian",
                        "options": ["Io mangio", "Tu mangi", "Lui mangia", "Noi mangiamo"],
                        "answer": "Io mangio"
                    },
                    {
                        "question": "What is the meaning of 'Che ore sono?'",
                        "options": ["How are you?", "What time is it?", "Where is it?", "What is your name?"],
                        "answer": "What time is it?"
                    },
                    {
                        "question": "Which preposition is used in 'Vado ___ Italia'?",
                        "options": ["a", "in", "da", "con"],
                        "answer": "in"
                    },
                    {
                        "question": "What is the Italian word for 'tomorrow'?",
                        "options": ["Ieri", "Oggi", "Domani", "Sempre"],
                        "answer": "Domani"
                    },
                    {
                        "question": "How do you say 'I would like' in Italian?",
                        "options": ["Io voglio", "Io vorrei", "Io posso", "Io devo"],
                        "answer": "Io vorrei"
                    }
                ]
            },
            "Spanish": {
                "Beginner": [
                    {
                        "question": "What is 'hello' in Spanish?",
                        "options": ["Hola", "Adiós", "Gracias", "Por favor"],
                        "answer": "Hola"
                    },
                    {
                        "question": "How do you say 'thank you' in Spanish?",
                        "options": ["Por favor", "Gracias", "Lo siento", "De nada"],
                        "answer": "Gracias"
                    },
                    {
                        "question": "What is 'Good morning' in Spanish?",
                        "options": ["Buenas tardes", "Buenas noches", "Buenos días", "Buen provecho"],
                        "answer": "Buenos días"
                    },
                    {
                        "question": "How do you say 'yes' in Spanish?",
                        "options": ["No", "Sí", "Tal vez", "Bien"],
                        "answer": "Sí"
                    },
                    {
                        "question": "What is 'please' in Spanish?",
                        "options": ["Gracias", "De nada", "Por favor", "Lo siento"],
                        "answer": "Por favor"
                    }
                ],
                "Intermediate": [
                    {
                        "question": "Choose the correct form: 'I eat' in Spanish",
                        "options": ["Yo como", "Tú comes", "Él come", "Nosotros comemos"],
                        "answer": "Yo como"
                    },
                    {
                        "question": "What is the meaning of '¿Qué hora es?'",
                        "options": ["How are you?", "What time is it?", "Where is it?", "What is your name?"],
                        "answer": "What time is it?"
                    },
                    {
                        "question": "Which preposition is used in 'Voy ___ España'?",
                        "options": ["a", "en", "de", "con"],
                        "answer": "a"
                    },
                    {
                        "question": "What is the Spanish word for 'tomorrow'?",
                        "options": ["Ayer", "Hoy", "Mañana", "Siempre"],
                        "answer": "Mañana"
                    },
                    {
                        "question": "How do you say 'I would like' in Spanish?",
                        "options": ["Yo quiero", "Yo quisiera", "Yo puedo", "Yo debo"],
                        "answer": "Yo quisiera"
                    }
                ]
            },
            "Japanese": {
                "Beginner": [
                    {
                        "question": "What is 'hello' in Japanese?",
                        "options": ["こんにちは (Konnichiwa)", "さようなら (Sayounara)", "ありがとう (Arigatou)", "お願いします (Onegaishimasu)"],
                        "answer": "こんにちは (Konnichiwa)"
                    },
                    {
                        "question": "How do you say 'thank you' in Japanese?",
                        "options": ["お願いします (Onegaishimasu)", "ありがとう (Arigatou)", "すみません (Sumimasen)", "どういたしまして (Douitashimashite)"],
                        "answer": "ありがとう (Arigatou)"
                    },
                    {
                        "question": "What is 'Good morning' in Japanese?",
                        "options": ["こんにちは (Konnichiwa)", "こんばんは (Konbanwa)", "おはようございます (Ohayou gozaimasu)", "おやすみなさい (Oyasuminasai)"],
                        "answer": "おはようございます (Ohayou gozaimasu)"
                    },
                    {
                        "question": "How do you say 'yes' in Japanese?",
                        "options": ["いいえ (Iie)", "はい (Hai)", "たぶん (Tabun)", "よくない (Yokunai)"],
                        "answer": "はい (Hai)"
                    },
                    {
                        "question": "What is 'please' in Japanese?",
                        "options": ["ありがとう (Arigatou)", "どういたしまして (Douitashimashite)", "お願いします (Onegaishimasu)", "すみません (Sumimasen)"],
                        "answer": "お願いします (Onegaishimasu)"
                    }
                ],
                "Intermediate": [
                    {
                        "question": "Choose the correct particle: わたしは日本語___ べんきょうします",
                        "options": ["を", "に", "が", "で"],
                        "answer": "を"
                    },
                    {
                        "question": "What is the meaning of '今何時ですか？'",
                        "options": ["How are you?", "What time is it?", "Where is it?", "What is your name?"],
                        "answer": "What time is it?"
                    },
                    {
                        "question": "Which is the correct way to say 'I went to Japan'?",
                        "options": ["日本に行きます", "日本に行きました", "日本で行きます", "日本で行きました"],
                        "answer": "日本に行きました"
                    },
                    {
                        "question": "What is the Japanese word for 'tomorrow'?",
                        "options": ["昨日 (Kinou)", "今日 (Kyou)", "明日 (Ashita)", "毎日 (Mainichi)"],
                        "answer": "明日 (Ashita)"
                    },
                    {
                        "question": "How do you say 'I would like' in polite Japanese?",
                        "options": ["ほしいです (Hoshii desu)", "～たいです (~tai desu)", "～ほうがいいです (~hou ga ii desu)", "～いただけませんか (~itadakemasen ka)"],
                        "answer": "～たいです (~tai desu)"
                    }
                ]
            }
        }
        
        # Default level if provided level not found
        if user_level not in ["Beginner", "Intermediate", "Advanced", "Proficient", "Master"]:
            user_level = "Beginner"
        
        # Fallback to Beginner for Advanced/Proficient/Master as they're not in our basic fallback
        if user_level not in ["Beginner", "Intermediate"]:
            user_level = "Intermediate"
        
        # Default language if provided language not found
        if user_language not in fallback_quizzes:
            user_language = "Italian"  # Default to Italian
        
        # Get the quiz for specified language and level
        quiz = fallback_quizzes[user_language][user_level]
        
        # Trim to requested number of questions
        return quiz[:num_questions]

    def analyze_proficiency(self, user_language: str) -> dict:
        """
        Analyze language proficiency using the level_detector agent inside a Crew.
        """
        pass