from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QButtonGroup, QPushButton, QMessageBox

class QuizDialog(QDialog):
    def __init__(self, quiz_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quiz")
        layout = QVBoxLayout(self)
        self.questions = quiz_data
        self.current = 0
        self._build_question(layout)
    
    def _build_question(self, layout):
        layout.addWidget(QLabel(self.questions[self.current]["question"]))
        self.grp = QButtonGroup(self)
        for opt in self.questions[self.current]["options"]:
            btn = QPushButton(opt)
            btn.setCheckable(True)
            self.grp.addButton(btn)
            layout.addWidget(btn)
        next_btn = QPushButton("Avanti")
        next_btn.clicked.connect(self._on_next)
        layout.addWidget(next_btn)
    
    def _on_next(self):
        selected = [b for b in self.grp.buttons() if b.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Seleziona", "Scegli una risposta!")
            return
        corretto = self.questions[self.current]["answer"]
        if selected[0].text() == corretto:
            QMessageBox.information(self, "Corretto", "Risposta esatta!")
        else:
            QMessageBox.information(self, "Sbagliato", f"Risposta giusta: {corretto}")
        self.current += 1
        if self.current < len(self.questions):
            # ricostruisci la UI
            for w in self.children():
                if isinstance(w, (QLabel, QPushButton)) and w.text() != "Avanti":
                    w.deleteLater()
            self.layout().removeWidget(self.grp)
            self._build_question(self.layout())
        else:
            QMessageBox.information(self, "Fine Quiz", "Hai completato il quiz!")
            self.accept()
