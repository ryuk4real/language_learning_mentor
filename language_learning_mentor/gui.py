import sys
import json
import re
import os
import threading
from pathlib import Path

# Import PySide6 modules
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QMessageBox, QTextEdit, QGroupBox,
    QSizePolicy, QSpacerItem, QStyleFactory # Import QStyleFactory
)
from PySide6.QtGui import QPixmap, QIcon, QFont, QAction, QColor, QPalette
from PySide6.QtCore import Qt, QTimer, QMetaObject, Q_ARG, QSize

# Assuming CrewAI related imports are functional, keep them (commented out for now)
# from crewai import Task
# from crew import LanguageMentor
# from crewai import Process, Task
# from tools.calculator import QuizCalculator

# --- Configuration ---

CONFIG_DIR = Path("config") # Directory to store user config files
CONFIG_DIR.mkdir(exist_ok=True) # Create config directory if it doesn't exist

# --- OS-Independent Flag Paths ---
BASE_DIR = Path(__file__).resolve().parent
FLAGS_DIR = BASE_DIR / "flags"

FLAGS = {
    'English': FLAGS_DIR / 'uk.png',
    'Japanese': FLAGS_DIR / 'japan.png',
    'Spanish': FLAGS_DIR / 'spain.png',
}

# --- Helper Functions ---

def get_config_path(username):
    """Generates the path for a user's config file."""
    # Sanitize username slightly for filename (replace spaces, common unsafe chars)
    safe_filename = re.sub(r'[\\/*?:"<>| ]', '_', username.lower())
    if not safe_filename:
        safe_filename = "default_user" # Fallback for empty/unsafe names
    return CONFIG_DIR / f"{safe_filename}.json"

def load_user_config(username):
    """Loads user configuration from JSON file."""
    config_path = get_config_path(username)
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None # User does not exist
    except json.JSONDecodeError:
        print(f"Warning: Corrupted config file for {username}. Using defaults.")
        return None # Treat as new user if file is corrupt
    except IOError as e:
         print(f"Error loading config for {username}: {e}")
         return None

def save_user_config(username, data):
    """Saves user configuration to JSON file."""
    config_path = get_config_path(username)
    try:
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Saved config for {username}")
    except IOError as e:
        QMessageBox.critical(None, "Save Error", f"Could not save configuration for {username}:\n{e}")
    except Exception as e:
        QMessageBox.critical(None, "Save Error", f"An unexpected error occurred while saving:\n{e}")


# --- Main Application Window ---
class MainWindow(QWidget): # Using QWidget as the main window
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Language Mentor")
        self.setGeometry(100, 100, 600, 450) # x, y, width, height

        # Set the application style (e.g., 'Fusion')
        # print("Available styles:", QStyleFactory.keys()) # Uncomment to see available styles
        QApplication.setStyle('Fusion') # 'Fusion' is a good cross-platform style

        # User Data - initialized empty or loaded from config
        self.username = None
        self.language = None
        self.progress = 0 # Experience points (EXP)
        self.level = "Beginner" # Default level for new users
        # Load theme preference first, default to 'light'
        # This is needed *before* building UI if UI colors depended heavily on it,
        # but with palette/Fusion, applying palette *after* UI is built is fine.
        self.current_theme = 'light' # Default theme preference ('light' or 'dark')
        # Config loading will update self.current_theme if saved

        # Define color palettes for light and dark themes
        self._light_palette = self._create_light_palette()
        self._dark_palette = self._create_dark_palette()


        # Layout for the main window - will hold the stacked widget
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Stacked widget to manage different screens (login, language select, dashboard)
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Create screen widgets (initially empty)
        self.login_widget = QWidget()
        self.language_select_widget = QWidget() # This widget is logically part of login flow but distinct
        self.dashboard_widget = QWidget()

        # Build the UI for each screen
        self._build_login_ui()
        self._build_dashboard_ui() # Build dashboard UI

        # Add screens to the stacked widget
        self.stacked_widget.addWidget(self.login_widget)          # Index 0
        self.stacked_widget.addWidget(self.dashboard_widget)      # Index 1
        # Language selection UI is integrated *within* the login widget visually,
        # controlled by showing/hiding a section, not a separate stacked widget page.

        # Apply the default/loaded theme
        # We do this after building UI so widgets exist to receive the palette
        self.set_theme(self.current_theme)

        # Show the login screen initially
        self.show_login_screen()


    # --- Palette Creation ---
    def _create_light_palette(self):
        palette = QPalette()
        # Default colors from the 'Fusion' style in light mode are usually good
        # Explicitly setting some common ones ensures consistency
        palette.setColor(QPalette.Window, QColor(240, 240, 240)) # Background
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white) # TextEdit, LineEdit background
        palette.setColor(QPalette.Text, Qt.black) # TextEdit, LineEdit foreground
        palette.setColor(QPalette.Button, QColor(200, 200, 200)) # Button background
        palette.setColor(QPalette.ButtonText, Qt.black) # Button text
        palette.setColor(QPalette.Highlight, QColor(48, 140, 198)) # Selection color
        palette.setColor(QPalette.HighlightedText, Qt.white)
        # Add more roles as needed for specific widgets
        return palette

    def _create_dark_palette(self):
        palette = QPalette()
        dark_gray = QColor(53, 53, 53)
        light_gray = QColor(180, 180, 180)
        mid_gray = QColor(68, 68, 68)
        dark_blue = QColor(42, 130, 218) # Highlight color

        palette.setColor(QPalette.Window, dark_gray) # Background
        palette.setColor(QPalette.WindowText, light_gray)
        palette.setColor(QPalette.Base, mid_gray.darker(150)) # TextEdit, LineEdit background
        palette.setColor(QPalette.AlternateBase, mid_gray) # Alternate rows in lists/tables
        palette.setColor(QPalette.ToolTipBase, dark_gray)
        palette.setColor(QPalette.ToolTipText, light_gray)
        palette.setColor(QPalette.Text, light_gray) # TextEdit, LineEdit foreground
        palette.setColor(QPalette.Button, mid_gray) # Button background
        palette.setColor(QPalette.ButtonText, light_gray) # Button text
        palette.setColor(QPalette.BrightText, Qt.red) # Used for errors etc.
        palette.setColor(QPalette.Link, dark_blue.lighter()) # Link text color
        palette.setColor(QPalette.Highlight, dark_blue) # Selection color
        palette.setColor(QPalette.HighlightedText, Qt.black)

        # Disabled colors
        disabled_color = light_gray.darker(150)
        palette.setColor(QPalette.Disabled, QPalette.Text, disabled_color)
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_color)
        palette.setColor(QPalette.Disabled, QPalette.WindowText, disabled_color)
        # ... add other disabled roles if necessary

        return palette


    # --- Config and Theme Handling ---
    def load_config(self, username):
        """Loads user data from config file and sets instance variables."""
        config_data = load_user_config(username)
        if config_data:
            self.username = username
            self.language = config_data.get('language', None)
            self.progress = config_data.get('progress', 0)
            self.level = config_data.get('level', 'Beginner')
            # Load theme preference, default to 'light' if not found
            self.current_theme = config_data.get('theme', 'light')
            print(f"Loaded config for {username}: Lang={self.language}, Theme={self.current_theme}, Level={self.level}")
            # Theme is applied in show_login_screen or show_main_dashboard after loading
            return True
        return False

    def save_config(self):
        """Saves current user data to their config file."""
        if not self.username:
            print("Warning: Cannot save config, no username set.")
            return
        data = {
            'language': self.language,
            'progress': self.progress,
            'level': self.level,
            'theme': self.current_theme, # Save theme preference name ('light' or 'dark')
        }
        save_user_config(self.username, data)

    def set_theme(self, theme_preference):
        """Sets the application theme using QPalette based on 'light' or 'dark' preference."""
        self.current_theme = theme_preference # Store the preference ('light' or 'dark')

        if theme_preference == 'dark':
            QApplication.setPalette(self._dark_palette)
        else: # Default to light
            QApplication.setPalette(self._light_palette)

        print(f"Applied theme: {theme_preference}")

        # Note: QPalette applies colors based on the current QStyle ('Fusion').
        # No need for manual updates.


    def toggle_theme(self):
        """Switches between light and dark themes."""
        new_theme_preference = 'dark' if self.current_theme == 'light' else 'light'
        self.set_theme(new_theme_preference)
        self.save_config() # Save theme preference immediately


    # --- Screen Building ---
    def _build_login_ui(self):
        """Builds the widgets and layout for the login screen."""
        layout = QVBoxLayout(self.login_widget)
        layout.setAlignment(Qt.AlignCenter) # Center content vertically

        header_label = QLabel("Language Mentor")
        # No need for objectName("HeaderLabel") with QSS
        # Set font directly
        header_font = QFont("Arial", 16, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        layout.addSpacing(30) # Add vertical space

        layout.addWidget(QLabel("Enter your Nickname:"), alignment=Qt.AlignCenter)

        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Nickname")
        self.username_entry.setMinimumWidth(250)
        self.username_entry.returnPressed.connect(self.handle_login_attempt) # Bind Enter key
        layout.addWidget(self.username_entry, alignment=Qt.AlignCenter)

        self.login_button = QPushButton("Login / Register")
        self.login_button.setMinimumWidth(150)
        self.login_button.clicked.connect(self.handle_login_attempt)
        layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        layout.addSpacing(20) # Add space before language options appear

        # --- Language Selection Section (part of login UI) ---
        self.lang_selection_widget = QWidget() # Container widget for language selection
        lang_layout = QVBoxLayout(self.lang_selection_widget)
        lang_layout.setAlignment(Qt.AlignCenter)
        lang_layout.setContentsMargins(0,0,0,0) # Remove default margins

        lang_layout.addWidget(QLabel("Choose a language to learn:"), alignment=Qt.AlignCenter)

        flags_h_layout = QHBoxLayout() # Horizontal layout for flags
        flags_h_layout.setAlignment(Qt.AlignCenter)

        # Store QIcons/QPixmaps to prevent garbage collection
        self._flag_icons = {}
        self._flag_pixmaps = {} # Store pixmaps for QLabel

        for lang, path in FLAGS.items():
            try:
                pixmap = QPixmap(str(path)) # Use str() for Path compatibility
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self._flag_pixmaps[lang] = scaled_pixmap # Store reference to pixmap

                    # Use QLabels within a QVBoxLayout for icon + text below
                    flag_v_layout = QVBoxLayout()
                    flag_v_layout.setSpacing(2)
                    flag_v_layout.setAlignment(Qt.AlignCenter)
                    flag_v_layout.setContentsMargins(5,5,5,5) # Padding around flag

                    icon_label = QLabel()
                    icon_label.setPixmap(scaled_pixmap)
                    icon_label.setAlignment(Qt.AlignCenter)
                    flag_v_layout.addWidget(icon_label)

                    text_label = QLabel(lang)
                    text_label.setAlignment(Qt.AlignCenter)
                    flag_v_layout.addWidget(text_label)

                    flag_container = QWidget() # Container for icon and text labels
                    flag_container.setLayout(flag_v_layout)
                    flag_container.setCursor(Qt.PointingHandCursor) # Indicate it's clickable
                    flag_container.setStyleSheet("QWidget { border: 1px solid transparent; } QWidget:hover { border: 1px solid #AAAAAA; }") # Simple hover effect

                    # Make the container clickable
                    # Use a lambda to capture the language and call confirm_language
                    flag_container.mousePressEvent = lambda event, l=lang: self.confirm_language(l)

                    flags_h_layout.addWidget(flag_container)

                else:
                    print(f"Warning: Could not load flag image from {path}. Using text button.")
                    btn = QPushButton(lang)
                    btn.setFixedSize(80, 80)
                    btn.clicked.connect(lambda checked=False, l=lang: self.confirm_language(l)) # checked=False needed for lambda with signal
                    flags_h_layout.addWidget(btn)

            except Exception as e:
                print(f"Error loading image or creating button for {lang}: {e}")
                btn = QPushButton(lang)
                btn.setFixedSize(80, 80)
                btn.clicked.connect(lambda checked=False, l=lang: self.confirm_language(l))
                flags_h_layout.addWidget(btn)

        lang_layout.addLayout(flags_h_layout) # Add the horizontal layout of flags to the lang_layout

        layout.addWidget(self.lang_selection_widget, alignment=Qt.AlignCenter) # Add container to main login layout
        self.lang_selection_widget.setVisible(False) # Initially hide it

        # Add a vertical spacer to push content to the top slightly
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))


    def _build_dashboard_ui(self):
        """Builds the widgets and layout for the main dashboard."""
        layout = QVBoxLayout(self.dashboard_widget)
        layout.setContentsMargins(10, 10, 10, 10) # Add padding

        # --- Top Bar ---
        top_bar_layout = QHBoxLayout()

        self.welcome_label = QLabel("Welcome, User!")
        header_font = QFont("Arial", 16, QFont.Bold) # Set font directly
        self.welcome_label.setFont(header_font)
        top_bar_layout.addWidget(self.welcome_label)

        top_bar_layout.addStretch() # Push items to the ends

        self.theme_button = QPushButton("Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setFixedWidth(80) # Fixed width for theme button
        top_bar_layout.addWidget(self.theme_button)

        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.show_login_screen)
        self.logout_button.setFixedWidth(80) # Fixed width for logout button
        top_bar_layout.addWidget(self.logout_button)

        layout.addLayout(top_bar_layout)

        # --- Info Bar ---
        info_bar_layout = QHBoxLayout()

        self.exp_label = QLabel("EXP: 0")
        info_bar_layout.addWidget(self.exp_label)

        self.level_label = QLabel("Level: Beginner")
        info_bar_layout.addWidget(self.level_label)

        self.language_label = QLabel("Learning: ")
        info_bar_layout.addWidget(self.language_label)

        info_bar_layout.addStretch() # Push items to the left

        layout.addLayout(info_bar_layout)

        # --- Daily Tip Area ---
        tip_groupbox = QGroupBox("Daily Tip")
        tip_layout = QVBoxLayout(tip_groupbox)

        # QTextEdit widget - can be made read-only
        self.tip_textbox = QTextEdit()
        self.tip_textbox.setReadOnly(True)
        self.tip_textbox.setFixedHeight(80) # Fixed height for the tip box
        tip_layout.addWidget(self.tip_textbox)

        layout.addWidget(tip_groupbox)

        # --- Center Buttons ---
        center_buttons_layout = QVBoxLayout()
        center_buttons_layout.setAlignment(Qt.AlignCenter)

        self.level_button = QPushButton("Level Proficiency Detector")
        self.level_button.setMinimumWidth(250)
        self.level_button.clicked.connect(self.detect_level)
        center_buttons_layout.addWidget(self.level_button, alignment=Qt.AlignCenter)

        self.quiz_button = QPushButton("Quiz")
        self.quiz_button.setMinimumWidth(250)
        self.quiz_button.clicked.connect(self.start_quiz)
        center_buttons_layout.addWidget(self.quiz_button, alignment=Qt.AlignCenter)

        layout.addLayout(center_buttons_layout)

        # Add vertical spacer to push elements towards the top
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Update dashboard info placeholders (will be called again when shown)
        self.update_dashboard_info()
        self._display_tip(f"A helpful tip will appear here once a language is selected!") # Initial placeholder


    # --- Screen Management ---
    def show_login_screen(self):
        """Switches to the login screen."""
        # Apply the current theme preference (will reload palette)
        # This ensures the login screen gets the correct initial theme on app start or logout
        self.set_theme(self.current_theme)

        self.username = None # Reset user data when going back to login
        self.language = None
        self.progress = 0
        self.level = "Beginner"

        self.lang_selection_widget.setVisible(False) # Hide the language section
        self.username_entry.clear()
        self.login_button.setEnabled(True)
        self.username_entry.setFocus()
        self.stacked_widget.setCurrentIndex(0) # Show the login widget (index 0)


    def handle_login_attempt(self):
        entered_username = self.username_entry.text().strip()
        if not entered_username:
            QMessageBox.warning(self, "Input Required", "Please enter your nickname.")
            return

        if self.load_config(entered_username):
            # User exists, config loaded and theme applied
            print(f"Welcome back, {self.username}!")
            self.show_main_dashboard()
        else:
            # New user
            print(f"Creating profile for new user: {entered_username}")
            self.username = entered_username
            # Set defaults for new user before showing language selection
            self.language = None # Language must be selected
            self.progress = 0
            self.level = "Beginner"
            # Default theme is already set in __init__ or loaded if config existed
            # No need to call set_theme here, it's done on show_login_screen

            self.save_config() # Save initial config (includes default theme)
            self.show_language_selection() # Proceed to language selection

    def show_language_selection(self):
        """Shows language selection buttons for a new user within the login screen."""
        self.login_button.setEnabled(False) # Disable login button

        # The language selection UI is already built within _build_login_ui
        # We just need to make its container widget visible
        self.lang_selection_widget.setVisible(True)

        # Ensure we are on the login stacked widget page
        self.stacked_widget.setCurrentIndex(0)


    def confirm_language(self, selected_language):
        """Called when a new user clicks a language flag/container."""
        self.language = selected_language
        print(f"User '{self.username}' selected language: {self.language}")
        # Save the initial configuration for the new user (includes theme)
        self.save_config()
        QMessageBox.information(self, "Language Set", f"Great! You've chosen to learn {self.language}.")
        self.show_main_dashboard()


    def show_main_dashboard(self):
        """Switches to the main dashboard screen."""
        # Apply the current theme preference (will reload palette)
        self.set_theme(self.current_theme)

        # Update dashboard labels with current user info
        self.update_dashboard_info()
        # Update tip box placeholder
        self._display_tip(f"A helpful tip about learning {self.language} will appear here soon!")

        self.stacked_widget.setCurrentIndex(1) # Show the dashboard widget (index 1)


    def update_dashboard_info(self):
         """Updates the labels on the dashboard with current user data."""
         if self.username:
              self.welcome_label.setText(f"Welcome, {self.username}!")
              self.exp_label.setText(f"EXP: {self.progress}")
              self.level_label.setText(f"Level: {self.level}")
              self.language_label.setText(f"Learning: {self.language if self.language else 'N/A'}")
         else:
             # Handle case where info is called before login (shouldn't happen with current flow)
             self.welcome_label.setText("Welcome!")
             self.exp_label.setText("EXP: ---")
             self.level_label.setText("Level: ---")
             self.language_label.setText("Learning: ---")


    # --- Placeholder/Core Logic Functions ---

    def update_status(self, text):
         # You might want a dedicated status bar at the bottom if needed
         print(f"Status: {text}") # Simple print for now
         # Example: self.statusBar().showMessage(text) if using QMainWindow

    # Use QMetaObject.invokeMethod for cross-thread UI updates
    def _display_tip(self, tip_text):
        """Safely updates the tip textbox from any thread."""
        # Use QueuedConnection to ensure this is called on the main thread
        QMetaObject.invokeMethod(self.tip_textbox, "setText", Qt.QueuedConnection, Q_ARG(str, tip_text))


    # --- Tip Generation ---
    def generate_tip(self):
        self.update_status("Generating tip...")
        self._display_tip("🧠 Generating a tip...") # Update tip box immediately

        # Start the background task in a separate thread
        # threading.Thread(target=self._run_tip_task, daemon=True).start()
        # Placeholder for now
        # Simulate async work with QTimer for demonstration without actual threading
        QTimer.singleShot(2000, lambda: self._run_tip_task_finished(f"Placeholder Tip: Learn 5 new words in {self.language if self.language else 'your chosen language'} today!"))


    def _run_tip_task(self):
        # Ensure CrewAI/API logic is handled here
        try:
            # --- Replace with your actual CrewAI/API call ---
            #import time
            #time.sleep(2) # Simulate work
            result = f"Here's a tip for {self.language}: Practice speaking even if it's just to yourself!"
            # --- End Replace ---

            # Call a method on the main thread to update UI
            QMetaObject.invokeMethod(self, "_run_tip_task_finished", Qt.QueuedConnection, Q_ARG(str, result))
            QMetaObject.invokeMethod(self, "update_status", Qt.QueuedConnection, Q_ARG(str, "Tip generated."))

        except Exception as e:
            error_msg = f"Error generating tip: {e}"
            QMetaObject.invokeMethod(self, "_run_tip_task_finished", Qt.QueuedConnection, Q_ARG(str, error_msg))
            QMetaObject.invokeMethod(self, "update_status", Qt.QueuedConnection, Q_ARG(str, "Error"))
            print(f"Tip generation error: {e}")
            # import traceback
            # print(traceback.format_exc())

    def _run_tip_task_finished(self, tip_text):
         """Called on the main thread after tip generation finishes."""
         self._display_tip(tip_text)


    # --- Quiz ---
    def start_quiz(self):
        # Placeholder - use your existing quiz logic, adapting UI updates
        self.update_status("Starting quiz...")
        QMessageBox.information(self, "Quiz", "Quiz functionality needs to be implemented.")
        # Example: threading.Thread(target=self._prepare_quiz).start()

    # --- Level Detection ---
    def detect_level(self):
        self.update_status("Detecting level...")
        # Show feedback in a popup for now
        QMessageBox.information(self, "Proficiency Level Detection", "🔍Proficiency detection functionality needs to be implemented.")


# --- Main Execution ---
if __name__ == "__main__":

    # Ensure the flags directory exists or provide a clear warning
    if not FLAGS_DIR.is_dir():
        print(f"WARNING: Flags directory not found at '{FLAGS_DIR}'. Please create it and add flag images (e.g., uk.png, japan.png, spain.png). Using text buttons for languages.")
        # Optionally exit or continue without flags
        # sys.exit("Flags directory not found.")


    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())