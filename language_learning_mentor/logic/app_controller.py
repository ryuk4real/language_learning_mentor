from PySide6.QtCore import QObject, Signal 
import threading
import time

from logic.config_manager import load_user_config, save_user_config
from logic.language_processor import LanguageProcessor

class AppController(QObject):
    """
    Manages the application state and orchestrates interactions
    between UI components and backend logic.
    """
    # Signals to notify the UI about state changes
    user_loggedIn = Signal(str)         # Emitted with username after successful login/registration
    user_state_updated = Signal(dict)   # Emitted when exp, level, language changes
    show_language_selection = Signal()  # Emitted for new users after login
    show_dashboard = Signal()           # Emitted after language selected or returning user logs in
    status_message = Signal(str)        # Emitted for messages to a status bar or print
    tip_generated = Signal(str)         # Emitted when a tip is ready
    theme_changed = Signal(str)        # Emitted when theme changes
    quiz_data_ready    = Signal(object)   # Emesso con la lista delle domande
    analysis_complete  = Signal(object)   # Emesso con {"feedback":…, "estimated_level":…}
    # Add signals for quiz data, analysis results, etc. as needed

    def __init__(self, parent=None):
        super().__init__(parent)
        # --- Application State ---
        self._username = None
        self._language = None
        self._progress = 0  # Experience points (EXP)
        self._level = "Beginner"
        self._theme = 'light' # Default theme

        # Initialize backend logic components
        # You might pass API keys or configurations here if needed
        self.lang_processor = LanguageProcessor()

        # --- Initial Actions ---
        # Nothing happens until the UI (MainWindow) calls a method like attempt_login

    # --- Properties for state ---
    @property
    def username(self):
        return self._username

    @property
    def language(self):
        return self._language

    @property
    def progress(self):
        return self._progress

    @property
    def level(self):
        return self._level

    @property
    def theme(self):
        return self._theme

    def set_theme(self, theme_preference):
        """Sets the theme preference and updates config."""
        print(f"Controller: Setting theme to {theme_preference}")
        if self._theme != theme_preference:
            self._theme = theme_preference
            # Save preference immediately - config manager handles file writing
            self.save_user_state()
            # Emit theme changed signal
            self.theme_changed.emit(theme_preference)

    def toggle_theme(self):
        """Toggles between light and dark themes."""
        new_theme = 'dark' if self._theme == 'light' else 'light'
        self.set_theme(new_theme)  # This will emit the signal too


    # --- User Authentication and State Management ---
    def attempt_login(self, username):
        """Handles login attempt or new user registration."""
        sanitized_username = username.strip()
        if not sanitized_username:
            self.status_message.emit("Please enter a nickname.")
            return False

        config_data = load_user_config(sanitized_username)

        if config_data:
            # Returning user
            print(f"Controller: Loading config for {sanitized_username}")
            self._username = sanitized_username
            self._language = config_data.get('language', None)
            self._progress = config_data.get('progress', 0)
            self._level = config_data.get('level', 'Beginner')
            self._theme = config_data.get('theme', 'light') # Load theme
            print(f"Loaded: Lang={self._language}, Theme={self._theme}, Level={self._level}")
            
            # Emit theme change to apply the user's saved theme preference
            self.theme_changed.emit(self._theme)

            self.user_loggedIn.emit(self._username)

            # --- ADDED: Always update UI state after loading config ---
            self.update_user_state_and_notify()

            if self._language:
                # User has a language, go to dashboard
                self.show_dashboard.emit()
                self.status_message.emit(f"Welcome back, {self._username}!")
            else:
                # User exists but needs to select language
                self.show_language_selection.emit()
                self.status_message.emit(f"Welcome back, {self._username}! Please select a language.")
            return True # Indicate login handled

        else:
            # New user registration
            print(f"Controller: Registering new user: {sanitized_username}")
            self._username = sanitized_username
            self._language = None # Must select language
            self._progress = 0
            self._level = "Beginner"
            self._theme = 'light' # Default theme for new users

            self.save_user_state() # Save initial state with default theme
            self.user_loggedIn.emit(self._username)

            # --- ADDED: Update UI state for the new user immediately ---
            self.update_user_state_and_notify()

            self.show_language_selection.emit()
            self.status_message.emit(f"Welcome, {self._username}! Please select a language to begin.")
            return True # Indicate registration started

    def process_language_selection(self, selected_language):
        """Handles a new user selecting a language."""
        if not self._username:
            self.status_message.emit("Error: No user logged in to select language.")
            return False

        if selected_language not in ['Italian', 'Japanese', 'Spanish']: # Validate language
             self.status_message.emit(f"Error: Invalid language selected: {selected_language}")
             return False

        self._language = selected_language
        print(f"Controller: User '{self._username}' selected language: {self._language}")
        self.save_user_state() # Save the selected language

        self.update_user_state_and_notify() # Notify UI of language change
        self.show_dashboard.emit() # Go to dashboard
        self.status_message.emit(f"You are now learning {self._language}!")
        return True

    def save_user_state(self):
        """Saves current user data to config file."""
        if not self._username:
            print("Controller Warning: Cannot save state, no username set.")
            return
        data = {
            'language': self._language,
            'progress': self._progress,
            'level': self._level,
            'theme': self._theme, # Save theme preference
        }
        # config_manager functions should print errors, no need for popup here
        save_user_config(self._username, data)

    def update_user_state_and_notify(self):
        """Emits signal with current user state for UI updates."""
        state = {
            'username': self._username,
            'language': self._language,
            'progress': self._progress,
            'level': self._level,
            'theme': self._theme # Include theme in state
        }
        print(f"Controller: Emitting user_state_updated with: {state}")
        self.user_state_updated.emit(state)


    def logout(self):
        """Logs out the current user and resets state."""
        print(f"Controller: Logging out user {self._username}")
        # Save current state before logging out might be desired, depending on flow
        self.save_user_state()

        # Reset state in controller
        self._username = None
        self._language = None
        self._progress = 0
        self._level = "Beginner"
        # Decide if theme should reset to default on logout or persist per system
        # self._theme = 'light' # Option 1: Reset theme on logout
        # self._theme = 'light' # Option 2: Load default theme for the 'no user' state

        # Notify UI to reset and show login screen
        # Send a dictionary with default/empty values for the UI to display
        self.user_state_updated.emit({
            'username': None, 'language': None, 'progress': 0, 'level': "Beginner", 'theme': 'light' # Send default theme
        })
        self.user_loggedIn.emit("") # Indicate no user logged in (MainWindow listens to this)
        self.status_message.emit("Logged out.")


    # --- Application Features Logic (Interactions with LanguageProcessor) ---

    def request_daily_tip(self):
        """Requests a daily tip from the language processor."""
        if not self._language:
            self.status_message.emit("Please select a language to get a tip.")
            self.tip_generated.emit("Please select a language first!") # Update tip box directly
            return

        self.status_message.emit("Generating tip...")
        self.tip_generated.emit("🧠 Generating tip...") # Immediate UI feedback

        # Run the potentially blocking task in a background thread
        thread = threading.Thread(
            target=self._run_tip_generation_task,
            args=(self._level, self._language),
            daemon=True
        )
        thread.start()

    def _run_tip_generation_task(self, level, language):
        """Helper method to run tip generation in a thread."""
        #try:
        #    tip = self.lang_processor.generate_daily_tip(level, language)
        #    QMetaObject.invokeMethod(self, 'tip_generated', Qt.QueuedConnection, Q_ARG(str, tip))
        #    QMetaObject.invokeMethod(self, 'status_message', Qt.QueuedConnection, Q_ARG(str, "Tip generated."))
        #except Exception as e:
        #    QMetaObject.invokeMethod(self, 'tip_generated', Qt.QueuedConnection, Q_ARG(str, f"Error generating tip: {e}"))
        #    QMetaObject.invokeMethod(self, 'status_message', Qt.QueuedConnection, Q_ARG(str, "Error generating tip."))
        #    print(f"Error in _run_tip_generation_task: {e}")
        pass

    def start_quiz(self):
        """Initiates the process of starting a quiz."""
        if not self._language:
            self.status_message.emit("Please select a language before starting a quiz.")
            return

        self.status_message.emit("Preparing quiz...")
        # Run quiz data preparation in a thread
        threading.Thread(target=self._run_prepare_quiz_task, args=(self._level, self._language), daemon=True).start()
 

    def _run_prepare_quiz_task(self, level, language):
        """Helper method to prepare quiz data in a thread."""
        #try:
        #    quiz_data = self.lang_processor.prepare_quiz_data(level, language)
        #    # Emit signal with quiz data for UI to handle (e.g., show a dialog)
        #    # self.quiz_data_ready.emit(quiz_data) # Uncomment if you add this signal
        #    QMetaObject.invokeMethod(self, 'status_message', Qt.QueuedConnection, Q_ARG(str, "Quiz data prepared."))
        #    # Example showing temporary message box from logic thread (for demo)
        #    from PySide6.QtWidgets import QMessageBox, QWidget # Import locally to avoid circular dependency if not needed elsewhere
        #    QMetaObject.invokeMethod(None, 'information', Qt.QueuedConnection,
        #                             Q_ARG(QWidget, None),
        #                             Q_ARG(str, "Quiz Data Ready!"),
        #                             Q_ARG(str, f"Quiz data prepared for {language} ({level}).\n{len(quiz_data)} questions.\n(UI needs to implement showing the quiz)"))
#
        #except Exception as e:
        #    QMetaObject.invokeMethod(self, 'status_message', Qt.QueuedConnection, Q_ARG(str, "Error preparing quiz."))
        #    from PySide6.QtWidgets import QMessageBox, QWidget
        #    QMetaObject.invokeMethod(None, 'critical', Qt.QueuedConnection,
        #                             Q_ARG(QWidget, None),
        #                             Q_ARG(str, "Quiz Error"),
        #                             Q_ARG(str, f"Error preparing quiz:\n{e}"))
        #    print(f"Error in _run_prepare_quiz_task: {e}")
        quiz = self.lang_processor.prepare_quiz_data(level, language)
        # Emissione diretta: PySide6 farà la queue-to-GUI thread automaticamente
        self.quiz_data_ready.emit(quiz)
        self.status_message.emit("Quiz pronto!")
 

    def detect_level(self, user_text: str):
        """Riceve il testo dalla UI e lo invia in background per analisi."""
        if not self._language:
            self.status_message.emit("Seleziona una lingua prima dell’analisi.")
            return
        if not user_text.strip():
            self.status_message.emit("Inserisci un testo prima di analizzare.")
            return

        self.status_message.emit("Analizzando competenza…")
        # Passiamo il testo reale inserito dall’utente
        threading.Thread(
            target=self._run_analyze_proficiency_task,
            args=(user_text, self._level, self._language),
            daemon=True
        ).start()

    def _run_analyze_proficiency_task(self, text_sample, current_level, language):
        result = self.lang_processor.analyze_proficiency(text_sample, current_level, language)
        self.analysis_complete.emit(result)
        self.status_message.emit("Analisi terminata.")


    # --- Add methods for other features (e.g., completing quiz, earning EXP, leveling up) ---
    def add_exp(self, amount):
        """Adds experience points to the user's progress."""
        if not self._username:
            print("Controller Warning: Cannot add exp, no user logged in.")
            return # Cannot add exp without a user

        if amount < 0:
             print("Controller Warning: Cannot add negative exp.")
             return

        print(f"Controller: Adding {amount} EXP to {self._username}")
        self._progress += amount

        old_level = self._level
        self._level = self._calculate_level(self._progress) # Recalculate level

        if self._level != old_level:
            print(f"Controller: {self._username} leveled up from {old_level} to {self._level}!")
            self.status_message.emit(f"Congratulations! You reached {self._level} level!")
            # You might want another signal specifically for level up animation/celebration

        self.save_user_state() # Save updated progress/level
        self.update_user_state_and_notify() # Notify UI of state change


    def _calculate_level(self, exp):
        """Calculates the user's level based on EXP (simple example)."""
        # Define EXP thresholds for levels
        if exp < 100:
            return "Beginner"
        elif exp < 500:
            return "Intermediate"
        elif exp < 1500:
            return "Advanced"
        elif exp < 3000:
            return "Proficient" # Added a level
        else:
            return "Master" # Or some higher level