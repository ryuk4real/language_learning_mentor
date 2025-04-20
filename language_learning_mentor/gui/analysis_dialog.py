from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit

class AnalysisDialog(QDialog):
    def __init__(self, analysis_result, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Risultati Analisi")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Livello stimato: {analysis_result['estimated_level']}"))
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setText(analysis_result['feedback'])
        layout.addWidget(txt)
