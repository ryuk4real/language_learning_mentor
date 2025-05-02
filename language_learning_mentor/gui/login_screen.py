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
LANGUAGES = ['Italian', 'French', 'Spanish'] # Use capitalized names for display
LANGUAGE_EMOJIS = {
    'Italian': '🇮🇹',
    'French': '🇫🇷',
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

    register_requested = Signal(str, str)  # nickname, email

    login_attempted = Signal(str)
    language_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui() # Build the UI elements

        # Remove _flag_pixmaps as we no longer use QPixmaps for flags

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # — Header —
        header = QLabel("Language Learning Mentor")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # — Instruction for unregistered users —
        self.info_label = QLabel("Please login or register to continue.")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: gray; margin-bottom: 10px;")
        layout.addWidget(self.info_label)

        layout.addSpacing(15)

        # — Nickname —
        layout.addWidget(QLabel("Nickname:"), alignment=Qt.AlignCenter)
        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Enter your nickname")
        self.username_entry.setMinimumWidth(250)
        layout.addWidget(self.username_entry, alignment=Qt.AlignCenter)

        layout.addSpacing(10)

        # — Email (hidden until registration) —
        email_row = QHBoxLayout()  # ➜ CHANGED
        self.email_label = QLabel("Email:")
        self.email_label.setVisible(False)
        email_row.addWidget(self.email_label)


        self.email_entry = QLineEdit()
        self.email_entry.setPlaceholderText("Enter your email")
        self.email_entry.setMinimumWidth(300)
        self.email_entry.setVisible(False)
        layout.addWidget(self.email_entry, alignment=Qt.AlignCenter)

        layout.addLayout(email_row)
        layout.addSpacing(20)

        # — Buttons —
        btn_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")
        btn_layout.addWidget(self.login_button)
        btn_layout.addWidget(self.register_button)
        layout.addLayout(btn_layout)

        # — Connections —
        self.login_button.clicked.connect(self._handle_login_button_click)
        self.register_button.clicked.connect(self._start_registration_flow)

        layout.addSpacing(30)

        # — Language selection (hidden until after login/register) —
        self.lang_widget = QWidget()
        lang_layout = QVBoxLayout(self.lang_widget)
        lang_layout.setAlignment(Qt.AlignCenter)
        lang_layout.addWidget(QLabel("Choose a language:"))
        row = QHBoxLayout()
        for lang in LANGUAGES:
            btn = QPushButton(f"{LANGUAGE_EMOJIS[lang]}  {lang}")
            btn.setFixedSize(120, 50)
            btn.clicked.connect(lambda _, l=lang: self.language_selected.emit(l))
            row.addWidget(btn)
        lang_layout.addLayout(row)
        self.lang_widget.setVisible(False)
        layout.addWidget(self.lang_widget, alignment=Qt.AlignCenter)

    def _handle_login_button_click(self):
        """Internal handler for login button/Enter key."""
        username = self.username_entry.text().strip()
        if not username:
            QMessageBox.warning(self, "Input Required", "Please enter your nickname.")
            return
        # Emit the signal for the controller to handle the login logic
        self.login_attempted.emit(username)

    def _start_registration_flow(self):
        """Switch UI into ‘registration’ mode."""
        self.info_label.setText("Please fill in your email to register.")
        self.email_label.setVisible(True)
        self.email_entry.setVisible(True)

        self.login_button.setEnabled(False)
        self.register_button.setText("Submit")
        try:
            self.register_button.clicked.disconnect()
        except TypeError:
            pass
        self.register_button.clicked.connect(self._handle_register_button_click)

    def _handle_register_button_click(self):
        """Validate and emit nickname+email for registration."""
        nick = self.username_entry.text().strip()
        mail = self.email_entry.text().strip()
        if not nick or not mail:
            QMessageBox.warning(self, "Input Required", "Please enter both nickname and email.")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", mail):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
            return
        self.register_requested.emit(nick, mail)


    def _start_registration_flow(self):
        """Show the email field and switch to registration mode."""
        self.email_entry.setVisible(True)
        # optionally disable login to avoid confusion
        self.login_button.setEnabled(False)
        self.register_button.setText("Submit")
        # reconnect the button to the real register handler
        self.register_button.clicked.disconnect()
        self.register_button.clicked.connect(self._handle_register_button_click)


    def _handle_register_button_click(self):
        """Called when the user submits nickname + email to register."""
        nickname = self.username_entry.text().strip()
        email = self.email_entry.text().strip()
        if not nickname or not email:
            QMessageBox.warning(self, "Input Required", "Please enter both nickname and email.")
            return
        # basic email format check
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
            return
        # emit registration signal
        self.register_requested.emit(nickname, email)

    def show_language_selection_ui(self):
        """Show the language‐buttons and disable login/register inputs."""
        self.login_button.setEnabled(False)
        self.register_button.setEnabled(False)
        self.username_entry.setEnabled(False)
        self.email_entry.setEnabled(False)
        self.lang_widget.setVisible(True)

    def hide_language_selection_ui(self):
        """Hide the language‐buttons and re‐enable login/register inputs."""
        self.lang_widget.setVisible(False)
        self.email_label.setVisible(False)
        self.email_entry.setVisible(False)

        # Reset buttons back to initial state
        self.login_button.setEnabled(True)
        self.register_button.setEnabled(True)

        # Restore entries
        self.username_entry.setEnabled(True)
        self.email_entry.setEnabled(False)

        # Clear any text
        self.username_entry.clear()
        self.email_entry.clear()

        # In case you had switched the register button text
        self.register_button.setText("Register")
        # And reconnect it to the registration flow
        try:
            self.register_button.clicked.disconnect()
        except TypeError:
            pass
        self.register_button.clicked.connect(self._start_registration_flow)

    def reset_ui(self):
        """Reset the entire login screen to its fresh start state."""
        self.username_entry.clear()
        self.email_entry.clear()
        self.email_label.setVisible(False)
        self.email_entry.setVisible(False)

        # Hide email + language panels
        self.email_entry.setVisible(False)
        self.lang_widget.setVisible(False)

        # Re-enable everything
        self.login_button.setEnabled(True)
        self.register_button.setEnabled(True)
        self.username_entry.setEnabled(True)

        # Restore register button text & connection
        self.register_button.setText("Register")
        try:
            self.register_button.clicked.disconnect()
        except TypeError:
            pass
        self.register_button.clicked.connect(self._start_registration_flow)

        # Focus back on nickname
        self.username_entry.setFocus()
