# gui/quiz_screen.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QButtonGroup, 
    QPushButton, QMessageBox, QHBoxLayout, QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import Signal, Qt

class QuizScreen(QWidget):
    quiz_completed = Signal(int)  # Segnale emesso quando il quiz è completato, con punteggio
    back_requested = Signal()     # Segnale per tornare alla dashboard
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.questions = []
        self.current = 0
        self.correct_answers = 0
        
        # Layout principale
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Intestazione
        header_layout = QHBoxLayout()
        self.title_label = QLabel("Quiz")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.back_button = QPushButton("Torna alla Dashboard")
        self.back_button.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_button)
        
        self.main_layout.addLayout(header_layout)
        
        # Area per la domanda (inizialmente vuota)
        self.question_layout = QVBoxLayout()
        self.main_layout.addLayout(self.question_layout)
        
        # Messaggio di caricamento iniziale
        self.loading_label = QLabel("Preparazione quiz in corso...")
        self.question_layout.addWidget(self.loading_label)
        
        # Spaziatore finale
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    
    def start_quiz(self, quiz_data):
        """Inizializza e avvia il quiz con i dati forniti"""
        if not quiz_data or not isinstance(quiz_data, list) or len(quiz_data) == 0:
            self._show_error("Non è stato possibile caricare il quiz. Prova più tardi.")
            return
            
        self.questions = quiz_data
        self.current = 0
        self.correct_answers = 0
        
        # Pulisci eventuali widget dalla domanda precedente
        self._clear_question_area()
        
        # Validazione di base del formato dei dati
        try:
            self._validate_quiz_data()
            # Mostra la prima domanda
            self._show_current_question()
        except ValueError as e:
            self._show_error(f"Errore nel formato del quiz: {str(e)}")
    
    def _validate_quiz_data(self):
        """Verifica che i dati del quiz abbiano il formato corretto"""
        if not self.questions:
            raise ValueError("Nessuna domanda ricevuta")
            
        for i, q in enumerate(self.questions):
            if not isinstance(q, dict):
                raise ValueError(f"La domanda {i+1} non è nel formato corretto")
            
            # Verifica i campi obbligatori
            if "question" not in q:
                raise ValueError(f"Manca il testo nella domanda {i+1}")
            if "options" not in q or not isinstance(q["options"], list) or len(q["options"]) == 0:
                raise ValueError(f"Opzioni mancanti o non valide nella domanda {i+1}")
            if "answer" not in q:
                raise ValueError(f"Risposta mancante nella domanda {i+1}")
            
            # Verifica che la risposta corretta sia tra le opzioni
            if q["answer"] not in q["options"]:
                raise ValueError(f"La risposta corretta non è tra le opzioni nella domanda {i+1}")
    
    def _show_error(self, message):
        """Mostra un messaggio di errore nell'area domanda"""
        self._clear_question_area()
        
        error_label = QLabel(message)
        error_label.setStyleSheet("color: red;")
        error_label.setWordWrap(True)
        self.question_layout.addWidget(error_label)
        
        retry_button = QPushButton("Riprova")
        retry_button.clicked.connect(self.back_requested.emit)
        self.question_layout.addWidget(retry_button)
    
    def _clear_question_area(self):
        """Pulisce l'area della domanda"""
        # Rimuovi tutti i widget dal layout della domanda
        while self.question_layout.count():
            item = self.question_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
    
    def _show_current_question(self):
        """Mostra la domanda corrente"""
        self._clear_question_area()
        
        # Aggiungi numero domanda e testo
        question_number = QLabel(f"Domanda {self.current + 1} di {len(self.questions)}")
        self.question_layout.addWidget(question_number)
        
        question_text = QLabel(self.questions[self.current]["question"])
        question_text.setStyleSheet("font-size: 16px; margin: 10px 0;")
        question_text.setWordWrap(True)
        self.question_layout.addWidget(question_text)
        
        # Gruppo per i pulsanti delle opzioni
        self.option_group = QButtonGroup(self)
        
        # Aggiungi le opzioni
        for i, opt in enumerate(self.questions[self.current]["options"]):
            btn = QPushButton(opt)
            btn.setCheckable(True)
            self.option_group.addButton(btn, i)
            self.question_layout.addWidget(btn)
        
        # Pulsante avanti
        next_btn = QPushButton("Avanti")
        next_btn.clicked.connect(self._on_next)
        self.question_layout.addWidget(next_btn)
    
    def _on_next(self):
        """Gestisce il click sul pulsante 'Avanti'"""
        selected = [b for b in self.option_group.buttons() if b.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Seleziona", "Scegli una risposta!")
            return
        
        # Controlla se la risposta è corretta
        correct_answer = self.questions[self.current]["answer"]
        user_answer = selected[0].text()
        
        if user_answer == correct_answer:
            QMessageBox.information(self, "Corretto", "Risposta esatta!")
            self.correct_answers += 1
        else:
            QMessageBox.information(self, "Sbagliato", f"Risposta giusta: {correct_answer}")
        
        # Passa alla domanda successiva o termina il quiz
        self.current += 1
        if self.current < len(self.questions):
            self._show_current_question()
        else:
            score = self.correct_answers
            QMessageBox.information(
                self, "Fine Quiz", 
                f"Hai completato il quiz!\nPunteggio: {score}/{len(self.questions)}"
            )
            self.questions = []
            self.current = 0
            self.quiz_completed.emit(score * 10)  # Emetti segnale con punteggio (10 EXP per risposta corretta)
            self.back_requested.emit()  # Torna alla dashboard