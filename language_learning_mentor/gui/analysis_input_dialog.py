from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt

class AnalysisInputDialog(QDialog):
    """Dialog in cui l'utente inserisce un testo da analizzare."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analisi competenza")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10,10,10,10)

        layout.addWidget(QLabel("Inserisci qui il testo da analizzare:"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Scrivi o incolla il tuo testo…")
        self.text_edit.setFixedHeight(120)
        layout.addWidget(self.text_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.analyze_btn = QPushButton("Analizza")
        self.analyze_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.analyze_btn)

        self.cancel_btn = QPushButton("Annulla")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def get_text(self) -> str:
        return self.text_edit.toPlainText().strip()
