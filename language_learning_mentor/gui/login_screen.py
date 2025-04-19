import sys
import re
# No longer need Path for flags, so remove pathlib import
# from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QMessageBox # Keep QMessageBox for input errors
)
# No longer need QPixmap for flag images, so remove QPixmap import
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal, QSize # QObject is implicitly inherited by QWidget


# --- Language and Emoji Definitions ---
LANGUAGES = ['Italian', 'Japanese', 'Spanish'] # Use capitalized names for display
LANGUAGE_EMOJIS = {
    'Italian': '🇮🇹',
    'Japanese': '🇯🇵',
    'Spanish': '🇪🇸',
    # Add other languages/emojis here if needed, but keep LANGUAGES list updated
}

# --- OS-Independent Flag Paths ---
# Remove FLAGS_DIR and FLAGS definitions as they are no longer used


class LoginScreen(QWidget):
    """
    UI widget for the login and language selection screen.
    Emits signals for user actions.
    """
    # Define signals that the UI will emit for the controller to handle
    login_attempted = Signal(str)
    language_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui() # Build the UI elements

        # Remove _flag_pixmaps as we no longer use QPixmaps for flags

    def _setup_ui(self):
        """Builds the widgets and layout for the login screen."""
        layout = QVBoxLayout(self) # Use self as parent for the layout
        layout.setAlignment(Qt.AlignCenter) # Center content vertically

        header_label = QLabel("Language Learning Mentor")
        header_font = QFont("Arial", 16, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        layout.addSpacing(30)

        layout.addWidget(QLabel("Enter your Nickname:"), alignment=Qt.AlignCenter)

        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Nickname")
        self.username_entry.setMinimumWidth(250)
        # Connect Enter key press to the login handler
        self.username_entry.returnPressed.connect(self._handle_login_button_click)
        layout.addWidget(self.username_entry, alignment=Qt.AlignCenter)

        self.login_button = QPushButton("Login / Register")
        self.login_button.setMinimumWidth(150)
        # Connect button click to the internal handler
        self.login_button.clicked.connect(self._handle_login_button_click)
        layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        layout.addSpacing(20)

        # --- Language Selection Section ---
        self.lang_selection_widget = QWidget() # Container widget
        lang_layout = QVBoxLayout(self.lang_selection_widget)
        lang_layout.setAlignment(Qt.AlignCenter)
        lang_layout.setContentsMargins(0,0,0,0)

        lang_layout.addWidget(QLabel("Choose a language to learn:"), alignment=Qt.AlignCenter)

        flags_h_layout = QHBoxLayout() # Keep name, but now holds emoji buttons
        flags_h_layout.setAlignment(Qt.AlignCenter)

        # Loop through the list of languages to create emoji buttons
        for lang in LANGUAGES:
            emoji = LANGUAGE_EMOJIS.get(lang, '❓') # Get emoji or a question mark if not found
            button_text = f"{emoji} {lang}"

            btn = QPushButton(button_text)
            btn.setFixedSize(120, 50) # Set a fixed size for button consistency

            # Connect button click to emit language_selected signal
            # Use lambda to capture the language
            btn.clicked.connect(lambda checked=False, l=lang: self.language_selected.emit(l))
            flags_h_layout.addWidget(btn)


        lang_layout.addLayout(flags_h_layout)
        layout.addWidget(self.lang_selection_widget, alignment=Qt.AlignCenter)
        self.lang_selection_widget.setVisible(False) # Initially hide language selection

        # Add vertical spacer to push content to the top slightly
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _handle_login_button_click(self):
        """Internal handler for login button/Enter key."""
        username = self.username_entry.text().strip()
        if not username:
            QMessageBox.warning(self, "Input Required", "Please enter your nickname.")
            return
        # Emit the signal for the controller to handle the login logic
        self.login_attempted.emit(username)

    def show_language_selection_ui(self):
        """Makes the language selection part visible."""
        self.login_button.setEnabled(False) # Disable login button
        self.username_entry.setEnabled(False) # Disable username input
        self.lang_selection_widget.setVisible(True)

    def hide_language_selection_ui(self):
        """Hides the language selection part and re-enables login."""
        self.lang_selection_widget.setVisible(False)
        self.login_button.setEnabled(True)
        self.username_entry.setEnabled(True)
        self.username_entry.clear() # Clear username field on successful login/selection

    def reset_ui(self):
        """Resets the login screen to its initial state."""
        self.username_entry.clear()
        self.login_button.setEnabled(True)
        self.username_entry.setEnabled(True)
        self.lang_selection_widget.setVisible(False)
        self.username_entry.setFocus()