from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QMessageBox, QButtonGroup,
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Signal

class LevelDetectionScreen(QWidget):
    back_requested = Signal()     # Signal to return to dashboard
    level_test_completed = Signal(int)  # Signal emitted when test is completed, with score
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.questions = []
        self.current = 0
        self.correct_answers = 0
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_layout = QHBoxLayout()
        self.title_label = QLabel("Language Level Test")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.back_button = QPushButton("Return to Dashboard")
        self.back_button.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_button)
        
        self.main_layout.addLayout(header_layout)
        
        # Question area (initially empty)
        self.question_layout = QVBoxLayout()
        self.main_layout.addLayout(self.question_layout)
        
        # Initial loading message
        self.loading_label = QLabel("Preparing level assessment test...")
        self.question_layout.addWidget(self.loading_label)
        
        # Final spacer
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    
    def start_test(self, test_data):
        """Initialize and start the test with the provided data"""
        self.questions = test_data
        self.current = 0
        self.correct_answers = 0
        
        # Clear any widgets from previous questions
        self._clear_question_area()
        
        # Show the first question
        if self.questions:
            self._show_current_question()
        else:
            self.question_layout.addWidget(QLabel("Error loading questions."))
    
    def _clear_question_area(self):
        """Clear the question area"""
        # Remove all widgets from the question layout
        while self.question_layout.count():
            item = self.question_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
    
    def _show_current_question(self):
        """Show the current question"""
        self._clear_question_area()
        
        # Add question number and text
        question_number = QLabel(f"Question {self.current + 1} of {len(self.questions)}")
        self.question_layout.addWidget(question_number)
        
        question_text = QLabel(self.questions[self.current]["question"])
        question_text.setStyleSheet("font-size: 16px; margin: 10px 0;")
        question_text.setWordWrap(True)
        self.question_layout.addWidget(question_text)
        
        # Group for option buttons
        self.option_group = QButtonGroup(self)
        
        # Add options
        for opt in self.questions[self.current]["options"]:
            btn = QPushButton(opt)
            btn.setCheckable(True)
            self.option_group.addButton(btn)
            self.question_layout.addWidget(btn)
        
        # Next button
        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self._on_next)
        self.question_layout.addWidget(next_btn)
    
    def _on_next(self):
        """Handle the click on the 'Next' button"""
        selected = [b for b in self.option_group.buttons() if b.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Select", "Choose an answer!")
            return
        
        # Check if answer is correct
        correct_answer = self.questions[self.current]["answer"]
        user_answer = selected[0].text()
        
        if user_answer == correct_answer:
            self.correct_answers += 1
        
        # Move to next question or end the test
        self.current += 1
        if self.current < len(self.questions):
            self._show_current_question()
        else:
            score = self.correct_answers
            QMessageBox.information(
                self, "Test Complete", 
                f"You've completed the level assessment test!\nScore: {score}/{len(self.questions)}"
            )
            self.level_test_completed.emit(score)  # Emit signal with score
            self.back_requested.emit()  # Return to dashboard
    
    def show_analysis_results(self, analysis_result):
        """Show analysis results"""
        self._clear_question_area()
        
        # Results header
        results_header = QLabel("Language Level Results")
        results_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px;")
        self.question_layout.addWidget(results_header)
        
        # Estimated level
        level_label = QLabel(f"Estimated level: {analysis_result['estimated_level']}")
        level_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.question_layout.addWidget(level_label)
        
        # Feedback
        feedback_label = QLabel("Feedback:")
        self.question_layout.addWidget(feedback_label)
        
        feedback_text = QLabel(analysis_result['feedback'])
        feedback_text.setWordWrap(True)
        feedback_text.setStyleSheet("margin: 5px 0 10px 0;")
        self.question_layout.addWidget(feedback_text)
        
        # Return to dashboard button
        back_btn = QPushButton("Return to Dashboard")
        back_btn.clicked.connect(self.back_requested.emit)
        self.question_layout.addWidget(back_btn)
    
    def reset_screen(self):
        """Reset screen state"""
        self.questions = []
        self.current = 0
        self.correct_answers = 0
        self._clear_question_area()
        
        # Show loading message
        self.loading_label = QLabel("Preparing level assessment test...")
        self.question_layout.addWidget(self.loading_label)