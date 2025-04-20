from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QMessageBox, QTextEdit, QGroupBox,
    QSizePolicy, QSpacerItem, QStyleFactory, QMessageBox, QDialog # Import QStyleFactory
)
from PySide6.QtGui import QPixmap, QIcon, QFont, QAction, QColor, QPalette
from PySide6.QtCore import Qt, QTimer, QMetaObject, Q_ARG, QSize, QObject # QObject needed for signals/slots if inheriting QWidget

# Import other parts of your application
from logic.app_controller import AppController
from gui.login_screen import LoginScreen
from gui.dashboard_screen import DashboardScreen
from gui.style_manager import StyleManager
from gui.quiz_dialog import QuizDialog
from gui.analysis_dialog import AnalysisDialog
from gui.analysis_input_dialog import AnalysisInputDialog

class MainWindow(QWidget): # Or QMainWindow if you need menus, toolbars, status bar
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Language Learning Mentor")
        self.setGeometry(100, 100, 600, 450) # x, y, width, height

        # Initialize components
        self.style_manager = StyleManager()
        system_theme = self.style_manager.get_system_theme()
        self.style_manager.apply_theme(system_theme)
        
        self.controller = AppController()

        # Set up the main layout and stacked widget
        self.main_layout = QVBoxLayout(self) # Use self as parent
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Create UI screens and add them to the stacked widget
        self.login_screen = LoginScreen()
        self.dashboard_screen = DashboardScreen()

        self.stacked_widget.addWidget(self.login_screen)      # Index 0
        self.stacked_widget.addWidget(self.dashboard_screen)   # Index 1

        # --- Connect Signals and Slots ---

        # Connect signals from LoginScreen to AppController
        self.login_screen.login_attempted.connect(self.controller.attempt_login)
        self.login_screen.language_selected.connect(self.controller.process_language_selection)

        # Connect signals from DashboardScreen to AppController
        self.dashboard_screen.logout_requested.connect(self.controller.logout)
        self.dashboard_screen.theme_toggled.connect(self.controller.toggle_theme) # Dashboard requests toggle
        self.dashboard_screen.level_detection_requested.connect(self.controller.detect_level)
        self.dashboard_screen.quiz_requested.connect(self.controller.start_quiz)
        self.dashboard_screen.daily_tip_requested.connect(self.controller.request_daily_tip) # Dashboard requests tip
        self.dashboard_screen.level_detection_requested.connect(self._show_analysis_input)

        # Connect signals from AppController back to UI (MainWindow or Screens)
        self.controller.user_loggedIn.connect(self._handle_user_loggedIn) # MainWindow handles screen switch/reset
        self.controller.user_state_updated.connect(self.dashboard_screen.update_user_info) # Dashboard updates info
        self.controller.show_language_selection.connect(self.login_screen.show_language_selection_ui) # Login screen shows language options
        self.controller.show_dashboard.connect(self.show_dashboard_screen) # MainWindow switches to dashboard
        self.controller.status_message.connect(self._display_status_message) # Handle status (e.g., print or status bar)
        self.controller.tip_generated.connect(self.dashboard_screen.display_tip) # Dashboard displays tip
        self.controller.theme_changed.connect(self._apply_theme) # MainWindow applies themes
        # Add connections for quiz data, analysis results, etc. when implemented
        self.controller.quiz_data_ready.connect(self._handle_quiz_data_ready)
        self.controller.analysis_complete.connect(self._handle_analysis_complete)

        # --- Initial Setup ---
        # Apply the theme loaded by the controller (default or from config)
        # This needs the QApplication instance, so best done after QApplication is created in main.py
        # The initial attempt_login call will trigger state loading and theme preference
        # We'll handle applying the theme based on the state loaded *after* login attempt.

        # Show the login screen initially
        # We don't call attempt_login here, the user has to type and click
        self.show_login_screen()


    # --- Screen Management ---
    def show_login_screen(self):
        """Switches to the login screen and resets its state."""
        print("MainWindow: Switching to login screen.")
        # Reset the login screen UI state
        self.login_screen.reset_ui()
        # Apply the theme based on the *controller's current theme* (might be default or loaded)
        self.style_manager.apply_theme(self.controller.theme)
        self.stacked_widget.setCurrentWidget(self.login_screen) # Show the login widget

    def show_dashboard_screen(self):
        """Switches to the main dashboard screen."""
        print("MainWindow: Switching to dashboard screen.")
        # Apply the theme based on the controller's current theme
        self.style_manager.apply_theme(self.controller.theme)
        self.stacked_widget.setCurrentWidget(self.dashboard_screen) # Show the dashboard widget
        # Request the first daily tip when showing the dashboard
        self.controller.request_daily_tip()


    # --- Controller Signal Handlers ---

    def _handle_user_loggedIn(self, username):
        """
        Handles the signal from the controller indicating a user is logged in.
        Used here primarily for resetting the login screen on successful login
        before switching to dashboard or language select.
        """
        print(f"MainWindow: Received user_loggedIn signal for user: {username}")
        if username:
             # Reset the login screen state after successful login attempt
             self.login_screen.hide_language_selection_ui() # Also clears input, enables login btn state doesn't matter as we switch
             # Theme is applied when switching screens (show_dashboard_screen or show_login_screen)
        else: # Logout case
             self.show_login_screen() # Go back to login on logout

    def _display_status_message(self, message):
         """Handles status messages from the controller."""
         print(f"STATUS: {message}")
         # If using QMainWindow, you'd update a status bar here:
         # self.statusBar().showMessage(message)


    # --- Add handlers for other controller signals (quiz_data_ready, analysis_complete) ---
    # def _handle_quiz_data_ready(self, quiz_data):
    #    print("MainWindow: Received quiz_data_ready signal.")
    #    # Logic to display the quiz UI, e.g., open a new QuizDialog(quiz_data, self.controller)
    #    QMessageBox.information(self, "Quiz Data Ready", f"Received {len(quiz_data)} quiz questions. UI needs to show this.")

    # def _handle_analysis_complete(self, analysis_result):
    #    print("MainWindow: Received analysis_complete signal.")
    #    # Logic to display the analysis results, e.g., in a message box or dialog
    #    feedback = analysis_result.get("feedback", "No feedback.")
    #    level = analysis_result.get("estimated_level", "Unknown")
    #    QMessageBox.information(self, "Analysis Complete", f"Feedback:\n{feedback}\nEstimated Level: {level}")


    # --- Add handlers for UI signals that MainWindow needs to process directly (less common) ---
    # Example: If a button on MainWindow itself needed handling, but we've moved them to DashboardScreen

    def _apply_theme(self, theme):
        """Applies the theme when it changes."""
        print(f"MainWindow: Applying {theme} theme")
        self.style_manager.apply_theme(theme)
    
    def _handle_quiz_data_ready(self, quiz_data):
        """Apre il dialog del quiz quando i dati sono pronti."""
        dlg = QuizDialog(quiz_data, parent=self)
        dlg.exec()

    def _handle_analysis_complete(self, analysis_result):
        """Apre il dialog di analisi al termine."""
        dlg = AnalysisDialog(analysis_result, parent=self)
        dlg.exec()

    def _show_analysis_input(self):
        """Apri il dialog per l'input del testo da analizzare."""
        # qui c'era placeholder
        dlg = AnalysisInputDialog(self)
        if dlg.exec() == QDialog.Accepted:
            text = dlg.get_text()
            if text:
                self.controller.detect_level(text)
            else:
                QMessageBox.warning(self, "Testo mancante", "Devi inserire un testo da analizzare.")