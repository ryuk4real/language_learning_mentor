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
from gui.quiz_screen import QuizScreen
from gui.level_detection_screen import LevelDetectionScreen

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
        self.quiz_screen = QuizScreen()  # Nuova schermata per il quiz
        self.level_detection_screen = LevelDetectionScreen()  # Nuova schermata per il rilevatore di livello

        self.stacked_widget.addWidget(self.login_screen)         # Index 0
        self.stacked_widget.addWidget(self.dashboard_screen)     # Index 1
        self.stacked_widget.addWidget(self.quiz_screen)          # Index 2
        self.stacked_widget.addWidget(self.level_detection_screen)  # Index 3

        # --- Connect Signals and Slots ---

        # Connect signals from LoginScreen to AppController
        self.login_screen.login_attempted.connect(self.controller.attempt_login)

        self.login_screen.register_requested.connect(self.controller.register_user)

        self.login_screen.language_selected.connect(self.controller.process_language_selection)

        # Connect signals from DashboardScreen to AppController
        self.dashboard_screen.logout_requested.connect(self.controller.logout)
        self.dashboard_screen.theme_toggled.connect(self.controller.toggle_theme) # Dashboard requests toggle
        self.dashboard_screen.quiz_requested.connect(self._show_quiz_screen)  # Modificato

        self.dashboard_screen.level_detection_requested.connect(self._show_level_detection_screen)  # Modificato

        # Connect signals dalle nuove schermate
        self.quiz_screen.back_requested.connect(self.show_dashboard_screen)  # Torna alla dashboard
        self.quiz_screen.quiz_completed.connect(self.controller.add_exp)  # Aggiungi esperienza al completamento
        
        self.level_detection_screen.back_requested.connect(self.show_dashboard_screen)  # Return to dashboard

        # Connect signals from AppController back to UI (MainWindow or Screens)
        self.controller.user_loggedIn.connect(self._handle_user_loggedIn) # MainWindow handles screen switch/reset
        self.controller.user_state_updated.connect(self.dashboard_screen.update_user_info) # Dashboard updates info
        self.controller.show_language_selection.connect(self.login_screen.show_language_selection_ui) # Login screen shows language options
        self.controller.show_dashboard.connect(self.show_dashboard_screen) # MainWindow switches to dashboard
        self.controller.status_message.connect(self._display_status_message) # Handle status (e.g., print or status bar)
        self.controller.tip_generated.connect(self.dashboard_screen.display_tip) # Dashboard displays tip
        self.controller.theme_changed.connect(self._apply_theme) # MainWindow applies themes

        self.controller.level_test_data_ready.connect(self.level_detection_screen.start_test)
        self.controller.analysis_complete.connect(self.level_detection_screen.show_analysis_results)
        self.controller.quiz_data_ready.connect(self.quiz_screen.start_quiz)
        self.controller.analysis_complete.connect(self.level_detection_screen.show_analysis_results)

        # --- Initial Setup ---
        # Show the login screen initially
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
    
    def _show_quiz_screen(self):
        """Passa alla schermata del quiz e avvia la preparazione."""
        print("MainWindow: Switching to quiz screen.")
        self.style_manager.apply_theme(self.controller.theme)
        self.stacked_widget.setCurrentWidget(self.quiz_screen)
        # Avvia la preparazione del quiz
        self.controller.start_quiz()
    
    def _show_level_detection_screen(self):
        """Passa alla schermata di rilevamento del livello."""
        print("MainWindow: Switching to level detection screen.")
        self.style_manager.apply_theme(self.controller.theme)
        self.stacked_widget.setCurrentWidget(self.level_detection_screen)
        # Resetta eventuali risultati precedenti
        self.level_detection_screen.reset_screen()


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

    def _apply_theme(self, theme):
        """Applies the theme when it changes."""
        print(f"MainWindow: Applying {theme} theme")
        self.style_manager.apply_theme(theme)

    def _show_level_detection_screen(self):
        """Switch to level detection screen and start preparation."""
        print("MainWindow: Switching to level detection screen.")
        self.style_manager.apply_theme(self.controller.theme)
        self.stacked_widget.setCurrentWidget(self.level_detection_screen)
        # Start level test preparation
        self.controller.start_level_detection()