from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSizePolicy, QSpacerItem, QTextEdit,
)
from PySide6.QtGui import QFont
# QObject import is not strictly necessary here as QWidget inherits it
from PySide6.QtCore import Qt, Signal # , QObject


class DashboardScreen(QWidget):
    """
    UI widget for the main application dashboard.
    Displays user info and provides buttons for features.
    Emits signals for user actions.
    """
    # Signals that the UI will emit for the controller to handle
    logout_requested = Signal()
    theme_toggled = Signal()
    level_detection_requested = Signal()
    quiz_requested = Signal()
    daily_tip_requested = Signal()
    quiz_results_updated = Signal(int) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui() # Build the UI elements
        # Initial placeholder state - will be updated by controller signal shortly after
        # We can leave these placeholders as they will be overwritten
        # self.update_user_info(username="User", language="N/A", progress=0, level="Beginner")
        self.display_tip("A helpful tip will appear here!") # Initial tip placeholder

    def _setup_ui(self):
        """Builds the widgets and layout for the main dashboard."""
        layout = QVBoxLayout(self) # Use self as parent for the layout
        layout.setContentsMargins(10, 10, 10, 10)

        # --- Top Bar ---
        top_bar_layout = QHBoxLayout()

        self.welcome_label = QLabel("Welcome, User!")
        header_font = QFont("Arial", 16, QFont.Bold)
        self.welcome_label.setFont(header_font)
        top_bar_layout.addWidget(self.welcome_label)

        top_bar_layout.addStretch()

        self.theme_button = QPushButton("Theme")
        self.theme_button.setFixedWidth(80)
        self.theme_button.clicked.connect(self.theme_toggled.emit) # Emit signal
        top_bar_layout.addWidget(self.theme_button)

        self.logout_button = QPushButton("Logout")
        self.logout_button.setFixedWidth(80)
        self.logout_button.clicked.connect(self.logout_requested.emit) # Emit signal
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

        info_bar_layout.addStretch()

        layout.addLayout(info_bar_layout)

        # --- Daily Tip Area ---
        tip_groupbox = QGroupBox("Daily Tip")
        tip_layout = QVBoxLayout(tip_groupbox)

        self.tip_textbox = QTextEdit()
        self.tip_textbox.setReadOnly(True)
        self.tip_textbox.setFixedHeight(80)
        tip_layout.addWidget(self.tip_textbox)

        # Add a button to get a new tip
        get_tip_button = QPushButton("Get New Tip")
        get_tip_button.clicked.connect(self.daily_tip_requested.emit)
        tip_layout.addWidget(get_tip_button, alignment=Qt.AlignRight)

        layout.addWidget(tip_groupbox)

        # --- Center Buttons ---
        center_buttons_layout = QVBoxLayout()
        center_buttons_layout.setAlignment(Qt.AlignCenter)

        self.level_button = QPushButton("Level Proficiency Detector")
        self.level_button.setMinimumWidth(250)
        self.level_button.clicked.connect(self.level_detection_requested.emit) # Emit signal
        center_buttons_layout.addWidget(self.level_button, alignment=Qt.AlignCenter)

        self.quiz_button = QPushButton("Quiz")
        self.quiz_button.setMinimumWidth(250)
        self.quiz_button.clicked.connect(self.quiz_requested.emit) # Emit signal
        center_buttons_layout.addWidget(self.quiz_button, alignment=Qt.AlignCenter)

        layout.addLayout(center_buttons_layout)

        # Add vertical spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    # --- MODIFIED METHOD SIGNATURE AND CONTENT ---
    def update_user_info(self, state_dict):
        """
        Updates the labels on the dashboard using data from the state dictionary.
        This method is a slot connected to AppController.user_state_updated.
        """
        print(f"DashboardScreen: Received state_dict to update UI: {state_dict}")
        # Extract data from the dictionary, providing defaults for safety
        username = state_dict.get('username', 'User')
        language = state_dict.get('language', 'N/A')
        progress = state_dict.get('progress', 0)
        level = state_dict.get('level', 'Beginner')
        # theme = state_dict.get('theme', 'light') # Can access theme here if needed for specific dashboard styling

        self.welcome_label.setText(f"Welcome, {username}!")
        self.exp_label.setText(f"EXP: {progress}")
        self.level_label.setText(f"Level: {level}")
        self.language_label.setText(f"Learning: {language}")
        # Optionally enable/disable feature buttons if language is None
        # is_language_set = language != 'N/A' and language is not None
        # self.level_button.setEnabled(is_language_set)
        # self.quiz_button.setEnabled(is_language_set)


    def display_tip(self, tip_text):
        """Sets the text of the daily tip textbox."""
        # This method's signature remains unchanged as it's connected to Signal(str)
        self.tip_textbox.setText(tip_text)

    # Add methods for other UI updates (quiz display, analysis results, etc.)