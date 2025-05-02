from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QMessageBox, QButtonGroup,
    QSizePolicy, QSpacerItem, QProgressBar
)
from PySide6.QtCore import Signal
from logic.app_controller import AppController
import threading

class LevelDetectionScreen(QWidget):
    back_requested = Signal()     # Signal to return to dashboard
    level_test_completed = Signal(int)  # Signal emitted when test is completed, with score
    analyze_requested = Signal(str)  # Signal to request analysis of user's text
    
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)

        self.controller = controller          # ← usa sempre questo
        self.controller.level_test_data_ready.connect(self.start_test)

        self.questions        = []
        self.current          = 0
        self.correct_answers  = 0
        self.levels = ["Beginner", "Pre-Intermediate",
                       "Intermediate", "Pre-Advanced",
                       "Advanced", "Master"]

        # --- UI ---------------------------------------------------------
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)

        header_layout = QHBoxLayout()
        self.title_label = QLabel("Language Level Test")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        self.back_button = QPushButton("Return to Dashboard")
        self.back_button.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_button)

        self.main_layout.addLayout(header_layout)

        self.question_layout = QVBoxLayout()
        self.main_layout.addLayout(self.question_layout)

        # Barra livello
        self.level_label = QLabel("Current Level: Beginner")
        self.level_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; margin: 10px 0;")
        self.level_progress_bar = QProgressBar()
        self.level_progress_bar.setRange(0, 100)
        self.level_progress_bar.setValue(0)

        lvl_box = QVBoxLayout()
        lvl_box.addWidget(self.level_label)
        lvl_box.addWidget(self.level_progress_bar)
        self.main_layout.addLayout(lvl_box)

        self.main_layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))


    def start_test(self, question_data):
        """Start with the first received question"""
        if self.current == 0:
            self.questions = []
            self.correct_answers = 0
            self.level_progress_bar.setValue(0)
            self.level_label.setText("Current Level: Beginner")

        if isinstance(question_data, list):
            question_data = question_data[0]

        self.questions.clear()
        self.questions.append(question_data)
        self._clear_question_area()
        self._show_current_question()

    
    def _clear_question_area(self):
        """Clear the question area"""
        while self.question_layout.count():
            item = self.question_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
    
    def _show_current_question(self):
        """Show the current question"""
        self._clear_question_area()
        
        # Add question number and text
        question_number = QLabel(f"Question {self.current + 1} of {5}")
        self.question_layout.addWidget(question_number)

        question_text = QLabel(self.questions[0]["question"])
        question_text.setStyleSheet("font-size: 16px; margin: 10px 0;")
        question_text.setWordWrap(True)
        self.question_layout.addWidget(question_text)
        
        self.option_group = QButtonGroup(self)
        
        for opt in self.questions[0]["options"]:
            btn = QPushButton(opt)
            btn.setCheckable(True)
            self.option_group.addButton(btn)
            self.question_layout.addWidget(btn)
        
        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self._on_next)
        self.question_layout.addWidget(next_btn)
    
    def _on_next(self):
        """Handle the click on the 'Next' button"""
        self.current += 1
        selected = [b for b in self.option_group.buttons() if b.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Select", "Choose an answer!")
            return

        correct_answer = self.questions[0]["answer"]
        user_answer = selected[0].text()


        ##if user_answer == correct_answer:
        ##    self.correct_answers += 1


        correct_idx = self.questions[0]["answer"]  # int
        correct_text = self.questions[0]["options"][correct_idx]

        if user_answer == correct_text:
            self.correct_answers += 1

        self._update_level()
        
        if self.current < 5:  # Totale 5 domande
            threading.Thread(target=self.controller._run_level_test_task, daemon=True).start()
            self._clear_question_area()
            self.questions = []
        else:
            score = self.correct_answers
            QMessageBox.information(
                self, "Test Complete", 
                f"You've completed the level assessment test!\nScore: {score}/5"
            )
            self.questions = []
            self.current = 0
            self.level_test_completed.emit(score) 
            self.back_requested.emit() 

    
    def _update_level(self):
        """Update the level based on current performance"""
        if not self.questions:
            return
        
        percentage = (self.correct_answers / 5) * 100
        self.level_progress_bar.setValue(int(percentage))
        if percentage < 20:
            level = self.levels[0]  # Beginner
        elif percentage < 40:
            level = self.levels[1]  # Pre-Intermediate
        elif percentage < 60:
            level = self.levels[2]  # Intermediate
        elif percentage < 80:
            level = self.levels[3]  # Pre-Advanced
        elif percentage < 95:
            level = self.levels[4]  # Advanced
        else:
            level = self.levels[5]  # Master
        
        self.level_label.setText(f"Current Level: {level}")
    
    def show_analysis_results(self, analysis_result):
        """Show analysis results"""
        self._clear_question_area()

        results_header = QLabel("Language Level Results")
        results_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px;")
        self.question_layout.addWidget(results_header)
        
        level_label = QLabel(f"Estimated level: {analysis_result['estimated_level']}")
        level_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.question_layout.addWidget(level_label)
        
        feedback_label = QLabel("Feedback:")
        self.question_layout.addWidget(feedback_label)
        
        feedback_text = QLabel(analysis_result['feedback'])
        feedback_text.setWordWrap(True)
        feedback_text.setStyleSheet("margin: 5px 0 10px 0;")
        self.question_layout.addWidget(feedback_text)
        
        back_btn = QPushButton("Return to Dashboard")
        back_btn.clicked.connect(self.back_requested.emit)
        self.question_layout.addWidget(back_btn)
    
    def reset_screen(self):
        """Reset screen state"""
        self.questions = []
        self.current = 0
        self.correct_answers = 0
        self._clear_question_area()
        
        self.level_progress_bar.setValue(0)
        self.level_label.setText("Current Level: Beginner")
        
        self.loading_label = QLabel("Preparing level assessment test...")
        self.question_layout.addWidget(self.loading_label)