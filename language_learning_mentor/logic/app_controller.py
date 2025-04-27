from PySide6.QtCore import QObject, Signal, QMetaObject, Q_ARG, Qt
import threading
import time

from logic.config_manager import load_user_config, save_user_config
from logic.language_processor import LanguageProcessor

class AppController(QObject):
    """
    Manages the application state and orchestrates interactions
    between UI components and backend logic.
    """
    user_loggedIn = Signal(str)
    user_state_updated = Signal(dict)
    show_language_selection = Signal()
    show_dashboard = Signal()
    status_message = Signal(str)
    tip_generated = Signal(str)
    theme_changed = Signal(str)
    quiz_data_ready = Signal(object)
    analysis_complete = Signal(object)
    level_test_data_ready = Signal(object)  # Manca nel tuo codice ma serve per level test

    def __init__(self, parent=None):
        super().__init__(parent)
        self._username = None
        self._language = None
        self._progress = 0
        self._level = "Beginner"
        self._theme = 'light'

        self.lang_processor = LanguageProcessor()

    @property
    def username(self): return self._username

    @property
    def language(self): return self._language

    @property
    def progress(self): return self._progress

    @property
    def level(self): return self._level

    @property
    def theme(self): return self._theme

    def set_theme(self, theme_preference):
        """Sets the theme preference and updates config."""
        if self._theme != theme_preference:
            self._theme = theme_preference
            self.save_user_state()
            self.theme_changed.emit(theme_preference)

    def toggle_theme(self):
        """Toggles between light and dark themes."""
        self.set_theme('dark' if self._theme == 'light' else 'light')

    def attempt_login(self, username):
        """Handles login attempt or new user registration."""
        sanitized_username = username.strip()
        if not sanitized_username:
            self.status_message.emit("Please enter a nickname.")
            return False

        config_data = load_user_config(sanitized_username)

        if config_data:
            self._username = sanitized_username
            self._language = config_data.get('language')
            self._progress = config_data.get('progress', 0)
            self._level = config_data.get('level', 'Beginner')
            self._theme = config_data.get('theme', 'light')

            self.theme_changed.emit(self._theme)
            self.user_loggedIn.emit(self._username)
            self.update_user_state_and_notify()

            if self._language:
                self.show_dashboard.emit()
                self.status_message.emit(f"Welcome back, {self._username}!")
            else:
                self.show_language_selection.emit()
                self.status_message.emit(f"Welcome back, {self._username}! Please select a language.")
        else:
            self._username = sanitized_username
            self._language = None
            self._progress = 0
            self._level = "Beginner"
            self._theme = 'light'

            self.save_user_state()
            self.user_loggedIn.emit(self._username)
            self.update_user_state_and_notify()
            self.show_language_selection.emit()
            self.status_message.emit(f"Welcome, {self._username}! Please select a language to begin.")

        return True

    def process_language_selection(self, selected_language):
        """Handles a new user selecting a language."""
        if not self._username:
            self.status_message.emit("Error: No user logged in to select language.")
            return False

        if selected_language not in ['Italian', 'Japanese', 'Spanish']:
            self.status_message.emit(f"Error: Invalid language selected: {selected_language}")
            return False

        self._language = selected_language
        self.save_user_state()
        self.update_user_state_and_notify()
        self.show_dashboard.emit()
        self.status_message.emit(f"You are now learning {self._language}!")
        return True

    def save_user_state(self):
        """Saves current user data to config file."""
        if not self._username:
            return
        save_user_config(self._username, {
            'language': self._language,
            'progress': self._progress,
            'level': self._level,
            'theme': self._theme,
        })

    def update_user_state_and_notify(self):
        """Emits signal with current user state for UI updates."""
        self.user_state_updated.emit({
            'username': self._username,
            'language': self._language,
            'progress': self._progress,
            'level': self._level,
            'theme': self._theme,
        })

    def logout(self):
        """Logs out the current user and resets state."""
        self.save_user_state()
        self._username = None
        self._language = None
        self._progress = 0
        self._level = "Beginner"

        self.user_state_updated.emit({
            'username': None, 'language': None, 'progress': 0, 'level': "Beginner", 'theme': 'light'
        })
        self.user_loggedIn.emit("")
        self.status_message.emit("Logged out.")

    def request_daily_tip(self):
        """Requests a daily tip from the language processor."""
        if not self._language:
            self.status_message.emit("Please select a language to get a tip.")
            self.tip_generated.emit("Please select a language first!")
            return

        self.status_message.emit("Generating tip...")
        self.tip_generated.emit("🧠 Generating tip...")
        threading.Thread(target=self._run_tip_generation_task, daemon=True).start()

    def _run_tip_generation_task(self):
        """Helper method to run tip generation in a thread."""
        try:
            tip = self.lang_processor.generate_daily_tip(self._level, self._language)
            self.tip_generated.emit(tip)
            self.status_message.emit("Tip generated.")
        except Exception as e:
            self.tip_generated.emit(f"Error: {e}")
            self.status_message.emit("Error generating tip.")

    def start_quiz(self):
        """Initiates the process of starting a quiz."""
        if not self._language:
            self.status_message.emit("Please select a language before starting a quiz.")
            return

        self.status_message.emit("Preparing quiz...")
        threading.Thread(target=self._run_prepare_quiz_task, daemon=True).start()

    def _run_prepare_quiz_task(self):
        """Helper method to prepare quiz data in a thread."""
        try:
            quiz = self.lang_processor.prepare_quiz_data(self._level, self._language)
            self.quiz_data_ready.emit(quiz)
            self.status_message.emit("Quiz ready.")
        except Exception as e:
            self.status_message.emit(f"Error preparing quiz: {e}")

    def detect_level(self, user_text: str):
        """Receives user text and sends it for background analysis."""
        if not self._language:
            self.status_message.emit("Select a language first.")
            return
        if not user_text.strip():
            self.status_message.emit("Insert a text first.")
            return

        self.status_message.emit("Analyzing proficiency…")
        threading.Thread(target=self._run_analyze_proficiency_task, args=(user_text,), daemon=True).start()

    def _run_analyze_proficiency_task(self, text_sample):
        """Helper method to analyze proficiency in a thread."""
        try:
            result = self.lang_processor.analyze_proficiency(text_sample, self._level, self._language)
            self.analysis_complete.emit(result)
            self.status_message.emit("Analysis complete.")
        except Exception as e:
            self.status_message.emit(f"Error analyzing proficiency: {e}")

    def add_exp(self, amount):
        """Adds experience points to the user's progress."""
        if not self._username or amount < 0:
            return

        self._progress += amount
        old_level = self._level
        self._level = self._calculate_level(self._progress)

        if self._level != old_level:
            self.status_message.emit(f"Congratulations! You reached {self._level} level!")

        self.save_user_state()
        self.update_user_state_and_notify()

    def _calculate_level(self, exp):
        """Calculates the user's level based on EXP."""
        if exp < 100:
            return "Beginner"
        elif exp < 500:
            return "Intermediate"
        elif exp < 1500:
            return "Advanced"
        elif exp < 3000:
            return "Proficient"
        else:
            return "Master"

    def setup_connections(self, main_window):
        """Configures the connections between controller and UI."""
        main_window.dashboard.quiz_requested.connect(self.start_quiz)
        main_window.dashboard.level_detection_requested.connect(self.start_level_detection)
        main_window.quiz_screen.quiz_completed.connect(self.process_quiz_results)
        main_window.level_detection_screen.analyze_requested.connect(self.detect_level)
        self.analysis_complete.connect(main_window.level_detection_screen.show_analysis_results)
        self.quiz_data_ready.connect(main_window.quiz_screen.start_quiz)

    def process_quiz_results(self, score):
        """Processes quiz results and awards EXP."""
        exp_earned = score * 10
        self.add_exp(exp_earned)
        self.status_message.emit(f"You earned {exp_earned} EXP from the quiz!")

    def start_level_detection(self):
        """Initiates the process of starting a level detection test."""
        if not self._language:
            self.status_message.emit("Please select a language before starting a level test.")
            return

        self.status_message.emit("Preparing level test...")
        threading.Thread(target=self._run_prepare_level_test_task, daemon=True).start()

    def _run_prepare_level_test_task(self):
        """Helper method to prepare level test data in a thread."""
        try:
            # Use language processor to prepare level test data, similar to quiz data
            test_data = self.lang_processor.prepare_level_test_data(self._level, self._language)
            self.level_test_data_ready.emit(test_data)
            self.status_message.emit("Level test ready.")
        except Exception as e:
            self.status_message.emit(f"Error preparing level test: {e}")

    def process_level_test_results(self, score):
        """Processes level test results and analyzes user level."""
        if not self._language:
            self.status_message.emit("Error: No language selected.")
            return

        self.status_message.emit("Analyzing level...")
        threading.Thread(target=self._run_analyze_level_task, args=(score,), daemon=True).start()

    def _run_analyze_level_task(self, score):
        """Helper method to analyze level test results."""
        try:
            result = self.lang_processor.analyze_level_test_result(score, self._level, self._language)
            self.analysis_complete.emit(result)
            
            # Update user level if the estimated level is different
            if result['estimated_level'] != self._level:
                self._level = result['estimated_level']
                self.save_user_state()
                self.update_user_state_and_notify()
                self.status_message.emit(f"Your language level has been updated to {self._level}!")
            else:
                self.status_message.emit("Level analysis complete. Your level remains the same.")
        except Exception as e:
            self.status_message.emit(f"Error analyzing level: {e}")