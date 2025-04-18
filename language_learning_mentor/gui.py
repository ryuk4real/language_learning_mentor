import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
from crew import LanguageMentor
from crewai import Process  # Aggiungiamo questo import mancante
import threading
import json
import re

# Percorsi bandiere
FLAGS = {
    'English': 'flags/uk.png',
    'Japanese': 'flags/japan.png',
    'Spanish': 'flags/spain.png',
    'Klingon': 'flags/klingon.png'
}

class LanguageMentorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Mentor")
        self.root.geometry("500x700")
        self.username = None
        self.language = None
        self.progress = 0
        self.level = "Non rilevato"
        
        # Risultati del quiz
        self.quiz_results = []
        
        self.show_login_screen()

    # ───────────────────────────────────────────────────────────── #
    # LOGIN / SELEZIONE LINGUA
    def show_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Benvenuto!", font=("Arial", 18)).pack(pady=20)
        tk.Label(self.root, text="Inserisci il tuo nome:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Scegli una lingua:").pack(pady=10)
        self.lang_frame = tk.Frame(self.root)
        self.lang_frame.pack(pady=5)

        for idx, (lang, path) in enumerate(FLAGS.items()):
            try:
                img = Image.open(path).resize((50, 30))
                photo = ImageTk.PhotoImage(img)
                btn = tk.Button(self.lang_frame, image=photo, command=lambda l=lang: self.set_language(l))
                btn.image = photo
                btn.grid(row=0, column=idx, padx=5)
            except Exception as e:
                print(f"Errore nel caricamento dell'immagine {path}: {e}")
                # Fallback button senza immagine
                btn = tk.Button(self.lang_frame, text=lang, command=lambda l=lang: self.set_language(l))
                btn.grid(row=0, column=idx, padx=5)

        self.start_button = tk.Button(self.root, text="Inizia", command=self.start_session, width=20, bg="#4CAF50", fg="white")
        self.start_button.pack(pady=30)

    def set_language(self, lang):
        self.language = lang
        messagebox.showinfo("Lingua selezionata", f"Hai scelto: {lang}")

    def start_session(self):
        self.username = self.username_entry.get()
        if not self.username or not self.language:
            messagebox.showwarning("Dati mancanti", "Inserisci nome e scegli una lingua.")
            return
        self.show_main_dashboard()

    # ───────────────────────────────────────────────────────────── #
    # DASHBOARD PRINCIPALE
    def show_main_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Header
        header_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text=f"{self.username} - {self.language}", font=("Arial", 16), bg="#f0f0f0").pack(side=tk.LEFT, padx=10)
        
        # Contenuto principale
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.content_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=40, height=15)
        self.content_area.pack(fill=tk.BOTH, expand=True, pady=10)
        self.content_area.insert(tk.END, f"Benvenuto {self.username}!\nSei pronto per imparare {self.language}?\n\nLivello attuale: {self.level}")
        self.content_area.config(state=tk.DISABLED)
        
        # Bottoni
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        buttons = [
            ("TIP", self.generate_tip),
            ("LEARN", self.start_quiz),
            ("PROGRESS", self.show_progress),
            ("DETECT LEVEL", self.detect_level)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, font=("Arial", 14), command=command, width=10, height=2)
            btn.grid(row=0, column=i, padx=5, pady=5)
            
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)
        
        # Status Bar
        status_frame = tk.Frame(self.root, bg="#f0f0f0", pady=5)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(status_frame, text="Pronto", bg="#f0f0f0")
        self.status_label.pack(side=tk.LEFT, padx=10)

    def update_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()
        
    def update_content(self, text, clear=True):
        self.content_area.config(state=tk.NORMAL)
        if clear:
            self.content_area.delete(1.0, tk.END)
        self.content_area.insert(tk.END, text)
        self.content_area.config(state=tk.DISABLED)
        self.content_area.see(tk.END)

    # ───────────────────────────────────────────────────────────── #
    # CALLBACK FUNZIONALI

    def generate_tip(self):
        self.update_status("Generazione tip in corso...")
        self.update_content("🧠 Sto generando un tip per te...\nAttendi qualche secondo...")
        threading.Thread(target=self._run_tip_task).start()

    def _run_tip_task(self):
        try:
            # Creazione di un nuovo mentor
            mentor = LanguageMentor()
            
            # Utilizziamo direttamente l'agente tip con il suo task
            tip_agent = mentor.tip_agent()
            tip_task = mentor.tip_task()
            
            # Creazione del task specifico per il tip
            tip_task.description = tip_task.description.replace("{{user_name}}", self.username).replace("{{language}}", self.language)
            
            # Esecuzione
            result = tip_agent.execute_task(tip_task)
            
            self.root.after(0, lambda: self.update_content(f"📌 Tip per oggi:\n\n{result}"))
            self.root.after(0, lambda: self.update_status("Tip generato con successo"))
        except Exception as e:
            self.root.after(0, lambda: self.update_content(f"Si è verificato un errore: {str(e)}"))
            self.root.after(0, lambda: self.update_status("Errore"))
            import traceback
            print(traceback.format_exc())

    def start_quiz(self):
        self.update_status("Preparazione quiz...")
        self.update_content("🧩 Sto preparando il quiz...\nAttendi qualche secondo...")
        self.current_quiz_question = 0
        self.quiz_correct = 0
        self.quiz_wrong = 0
        self.quiz_questions = []
        threading.Thread(target=self._prepare_quiz).start()
        
    def _prepare_quiz(self):
        try:
            # Utilizziamo direttamente l'agente quiz
            mentor = LanguageMentor()
            quiz_agent = mentor.quiz_agent()
            
            # Ask the agent to generate quiz questions
            prompt = f"Genera un quiz di 5 domande a scelta multipla per testare la conoscenza di {self.language} per {self.username}. " \
                     f"Ogni domanda deve avere 4 opzioni. Formatta il risultato come JSON."
            
            result = quiz_agent.execute_task(
                task=Task(
                    description=prompt,
                    expected_output="Un quiz in formato JSON con domande e opzioni"
                )
            )
            
            # Try to parse quiz questions from the result
            try:
                # Look for JSON pattern
                json_pattern = r'\[\s*{.*}\s*\]'
                json_match = re.search(json_pattern, result, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(0)
                    questions = json.loads(json_str)
                    self.quiz_questions = questions
                else:
                    # Fallback: Parse the text output manually
                    questions = []
                    lines = result.split('\n')
                    
                    current_q = None
                    options = []
                    correct_idx = None
                    
                    for line in lines:
                        if line.strip().startswith("Domanda") or line.strip().startswith("Q"):
                            # Save previous question if exists
                            if current_q and options and correct_idx is not None:
                                questions.append({
                                    "question": current_q,
                                    "options": options,
                                    "correct": correct_idx
                                })
                            
                            # Start new question
                            q_parts = line.split(":", 1)
                            if len(q_parts) > 1:
                                current_q = q_parts[1].strip()
                            else:
                                current_q = "Domanda generica"
                            options = []
                            correct_idx = None
                            
                        elif line.strip().startswith(("A)", "A.", "1)", "1.")):
                            options = []  # Reset options
                            options.append(line.split(")", 1)[1].strip() if ")" in line else line.split(".", 1)[1].strip())
                        elif line.strip().startswith(("B)", "B.", "2)", "2.")):
                            options.append(line.split(")", 1)[1].strip() if ")" in line else line.split(".", 1)[1].strip())
                        elif line.strip().startswith(("C)", "C.", "3)", "3.")):
                            options.append(line.split(")", 1)[1].strip() if ")" in line else line.split(".", 1)[1].strip())
                        elif line.strip().startswith(("D)", "D.", "4)", "4.")):
                            options.append(line.split(")", 1)[1].strip() if ")" in line else line.split(".", 1)[1].strip())
                        elif "risposta corretta" in line.lower() or "correct answer" in line.lower():
                            if "A" in line or "1" in line:
                                correct_idx = 0
                            elif "B" in line or "2" in line:
                                correct_idx = 1
                            elif "C" in line or "3" in line:
                                correct_idx = 2
                            elif "D" in line or "4" in line:
                                correct_idx = 3
                    
                    # Add the last question
                    if current_q and options and correct_idx is not None:
                        questions.append({
                            "question": current_q,
                            "options": options,
                            "correct": correct_idx
                        })
                    
                    if questions:
                        self.quiz_questions = questions
                    else:
                        raise Exception("Impossibile parsare le domande del quiz")
            except Exception as parsing_error:
                # Fallback con domande predefinite
                print(f"Errore nel parsing: {parsing_error}")
                self.quiz_questions = [
                    {"question": f"Come si dice 'ciao' in {self.language}?", "options": ["Hello", "Goodbye", "Thank you", "Sorry"], "correct": 0},
                    {"question": f"Come si dice 'grazie' in {self.language}?", "options": ["Sorry", "Please", "Thank you", "Welcome"], "correct": 2},
                    {"question": f"Quale di queste è una frase corretta in {self.language}?", "options": ["Option 1", "Option 2", "Option 3", "Option 4"], "correct": 1},
                    {"question": f"Quale parola significa 'casa' in {self.language}?", "options": ["Car", "House", "Food", "Water"], "correct": 1},
                    {"question": f"Come si dice 'buongiorno' in {self.language}?", "options": ["Good morning", "Good night", "Good evening", "Good afternoon"], "correct": 0},
                ]
                
            self.root.after(0, self._show_quiz_question)
        except Exception as e:
            self.root.after(0, lambda: self.update_content(f"Si è verificato un errore nella preparazione del quiz: {str(e)}"))
            self.root.after(0, lambda: self.update_status("Errore"))
            import traceback
            print(traceback.format_exc())
    
    def _show_quiz_question(self):
        if self.current_quiz_question < len(self.quiz_questions):
            question = self.quiz_questions[self.current_quiz_question]
            
            # Pulisci la schermata
            for widget in self.root.winfo_children():
                widget.destroy()
                
            # Mostra la domanda
            tk.Label(self.root, text=f"Domanda {self.current_quiz_question + 1}/{len(self.quiz_questions)}", 
                     font=("Arial", 14)).pack(pady=10)
            tk.Label(self.root, text=question["question"], font=("Arial", 12), wraplength=450).pack(pady=10)
            
            # Mostra le opzioni
            for i, option in enumerate(question["options"]):
                btn = tk.Button(
                    self.root, 
                    text=option, 
                    font=("Arial", 12),
                    width=30,
                    wraplength=300,
                    command=lambda idx=i: self._check_answer(idx, question["correct"])
                )
                btn.pack(pady=5)
                
            # Pulsante per tornare indietro
            tk.Button(self.root, text="Annulla quiz", command=self.show_main_dashboard).pack(pady=20)
        else:
            self._calculate_quiz_result()
            
    def _check_answer(self, selected_idx, correct_idx):
        if selected_idx == correct_idx:
            self.quiz_correct += 1
            messagebox.showinfo("Risposta", "Corretto! 👍")
        else:
            self.quiz_wrong += 1
            messagebox.showinfo("Risposta", f"Sbagliato! La risposta corretta era l'opzione {correct_idx + 1} 👎")
            
        self.current_quiz_question += 1
        self._show_quiz_question()
            
    def _calculate_quiz_result(self):
        try:
            # Utilizziamo direttamente l'agente quiz
            mentor = LanguageMentor()
            quiz_agent = mentor.quiz_agent()
            calculator = QuizCalculator()
            
            # Utilizziamo lo strumento calculator
            score_result = calculator._run(correct=self.quiz_correct, wrong=self.quiz_wrong)
            
            # Aggiorna il progresso
            score = self.quiz_correct - self.quiz_wrong
            if score > 0:
                self.progress += score
                
            # Salva il risultato
            self.quiz_results.append({
                "correct": self.quiz_correct,
                "wrong": self.quiz_wrong,
                "score": score
            })
            
            # Esecuzione task di analisi del quiz
            result = quiz_agent.execute_task(
                task=Task(
                    description=f"Analizza i risultati del quiz per {self.username} che sta imparando {self.language}. " \
                              f"Risposte corrette: {self.quiz_correct}, Risposte errate: {self.quiz_wrong}. " \
                              f"Fornisci un feedback motivazionale.",
                    expected_output="Un'analisi dei risultati con suggerimenti di miglioramento"
                )
            )
            
            # Mostra risultato
            self.show_main_dashboard()
            self.update_content(f"Quiz completato!\n\nRisposte corrette: {self.quiz_correct}\nRisposte errate: {self.quiz_wrong}\n\n{result}")
            self.update_status("Quiz completato")
        except Exception as e:
            self.show_main_dashboard()
            self.update_content(f"Si è verificato un errore nel calcolo del risultato: {str(e)}")
            self.update_status("Errore")
            import traceback
            print(traceback.format_exc())

    def show_progress(self):
        self.update_status("Visualizzazione progressi...")
        
        progress_text = f"Riepilogo progressi per {self.username}\n"
        progress_text += f"Lingua: {self.language}\n"
        progress_text += f"Livello: {self.level}\n"
        progress_text += f"Punteggio totale: {self.progress}\n\n"
        
        if self.quiz_results:
            progress_text += "Quiz completati:\n"
            for i, quiz in enumerate(self.quiz_results):
                progress_text += f"Quiz {i+1}: Corrette {quiz['correct']}, Errate {quiz['wrong']}, Punteggio {quiz['score']}\n"
        else:
            progress_text += "Non hai ancora completato nessun quiz.\n"
            
        progress_text += "\nContinua così per migliorare il tuo livello!"
        
        self.update_content(progress_text)
        self.update_status("Progressi visualizzati")

    def detect_level(self):
        self.update_status("Rilevamento livello in corso...")
        self.update_content("🔍 Sto valutando il tuo livello di conoscenza della lingua...\nAttendi qualche secondo...")
        threading.Thread(target=self._run_level_task).start()
        
    def _run_level_task(self):
        try:
            # Utilizziamo direttamente l'agente di rilevamento livello
            mentor = LanguageMentor()
            level_agent = mentor.level_detector()
            level_task = mentor.level_task()
            
            # Sostituiamo i placeholder nelle descrizioni del task
            level_task.description = level_task.description.replace("{{user_name}}", self.username).replace("{{language}}", self.language)
            
            # Esecuzione
            result = level_agent.execute_task(level_task)
            
            # Estrai il livello dal risultato
            if "principiante" in result.lower():
                self.level = "Principiante" 
            elif "intermedio" in result.lower():
                self.level = "Intermedio"
            elif "avanzato" in result.lower():
                self.level = "Avanzato"
            else:
                self.level = "Non classificato"
                
            self.root.after(0, lambda: self.update_content(f"🎓 Valutazione del livello completata:\n\n{result}"))
            self.root.after(0, lambda: self.update_status(f"Livello rilevato: {self.level}"))
        except Exception as e:
            self.root.after(0, lambda: self.update_content(f"Si è verificato un errore: {str(e)}"))
            self.root.after(0, lambda: self.update_status("Errore"))
            import traceback
            print(traceback.format_exc())

# ───────────────────────────────────────────────────────────── #
# MAIN
if __name__ == "__main__":
    # Import aggiuntivo per l'esecuzione diretta
    from crewai import Task
    from tools.calculator import QuizCalculator
    
    root = tk.Tk()
    app = LanguageMentorApp(root)
    root.mainloop()