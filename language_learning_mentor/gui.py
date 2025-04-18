import tkinter as tk
from tkinter import messagebox, scrolledtext, font as tkFont
from PIL import Image, ImageTk
from crewai import Task
from crew import LanguageMentor 
from crewai import Process, Task
from tools.calculator import QuizCalculator
import threading
import json
import re
import os
from pathlib import Path

# --- Configuration ---

CONFIG_DIR = Path("config") # Directory to store user config files
CONFIG_DIR.mkdir(exist_ok=True) # Create config directory if it doesn't exist

# Define theme colors
LIGHT_THEME = {
    "bg": "#F0F0F0",
    "fg": "#000000",
    "button_bg": "#D0D0D0",
    "button_fg": "#000000",
    "entry_bg": "#FFFFFF",
    "entry_fg": "#000000",
    "text_bg": "#FFFFFF",
    "text_fg": "#000000",
    "accent": "#4CAF50", # Example accent color
    "accent_fg": "#FFFFFF"
}

DARK_THEME = {
    "bg": "#2E2E2E",
    "fg": "#FFFFFF",
    "button_bg": "#505050",
    "button_fg": "#FFFFFF",
    "entry_bg": "#3E3E3E",
    "entry_fg": "#FFFFFF",
    "text_bg": "#3E3E3E",
    "text_fg": "#FFFFFF",
    "accent": "#81C784", # Lighter accent for dark theme
    "accent_fg": "#000000"
}

# --- OS-Independent Flag Paths ---
BASE_DIR = Path(__file__).resolve().parent
FLAGS_DIR = BASE_DIR / "flags"

FLAGS = {
    'English': FLAGS_DIR / 'uk.png',
    'Japanese': FLAGS_DIR / 'japan.png',
    'Spanish': FLAGS_DIR / 'spain.png',
}

# --- Helper Functions ---

def get_config_path(username):
    """Generates the path for a user's config file."""
    # Sanitize username slightly for filename (replace spaces, common unsafe chars)
    safe_filename = re.sub(r'[\\/*?:"<>| ]', '_', username.lower())
    if not safe_filename:
        safe_filename = "default_user" # Fallback for empty/unsafe names
    return CONFIG_DIR / f"{safe_filename}.json"

def load_user_config(username):
    """Loads user configuration from JSON file."""
    config_path = get_config_path(username)
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None # User does not exist
    except json.JSONDecodeError:
        print(f"Warning: Corrupted config file for {username}. Using defaults.")
        return None # Treat as new user if file is corrupt

def save_user_config(username, data):
    """Saves user configuration to JSON file."""
    config_path = get_config_path(username)
    try:
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        messagebox.showerror("Save Error", f"Could not save configuration for {username}:\n{e}")

def apply_theme(widget, theme):
    """Recursively applies theme colors to a widget and its children."""
    try:
        widget.config(bg=theme["bg"])
    except tk.TclError: pass # Ignore widgets that don't support 'bg'

    # Apply specific colors based on widget type
    widget_type = widget.winfo_class()

    if widget_type in ('Label', 'TLabel', 'Message'):
        try: widget.config(fg=theme["fg"], bg=theme["bg"])
        except tk.TclError: pass
    elif widget_type in ('Button', 'TButton'):
        try: widget.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["accent"], activeforeground=theme["accent_fg"])
        except tk.TclError: pass
    elif widget_type in ('Entry', 'TEntry'):
        try: widget.config(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
        except tk.TclError: pass
    elif widget_type in ('Text', 'ScrolledText'):
         try: widget.config(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["fg"])
         except tk.TclError: pass
    elif widget_type in ('Frame', 'TFrame', 'Labelframe', 'TLabelframe'):
         try: widget.config(bg=theme["bg"])
         except tk.TclError: pass

    # Recursively apply to children
    for child in widget.winfo_children():
        apply_theme(child, theme)

# --- Main Application Class ---
class LanguageMentorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Mentor")
        self.root.geometry("600x400") # Slightly larger for more content

        # User Data - initialized empty or loaded from config
        self.username = None
        self.language = None
        self.progress = 0 # Experience points (EXP)
        self.level = "Beginner" # Default level for new users
        self.current_theme = 'light' # Default theme
        self.theme_colors = LIGHT_THEME

        # Font setup
        self.default_font = tkFont.nametofont("TkDefaultFont")
        self.default_font.configure(size=10)
        self.header_font = tkFont.Font(family="Arial", size=16, weight="bold")
        self.label_font = tkFont.Font(family="Arial", size=11)
        self.button_font = tkFont.Font(family="Arial", size=10, weight="bold")

        self.show_login_screen()

    # --- Config and Theme Handling ---
    def load_config(self, username):
        """Loads user data from config file and sets instance variables."""
        config_data = load_user_config(username)
        if config_data:
            self.username = username
            self.language = config_data.get('language', None)
            self.progress = config_data.get('progress', 0)
            self.level = config_data.get('level', 'Beginner')
            self.current_theme = config_data.get('theme', 'light')
            print(f"Loaded config for {username}: Lang={self.language}, Theme={self.current_theme}, Level={self.level}")
            return True
        return False

    def save_config(self):
        """Saves current user data to their config file."""
        if not self.username:
            print("Warning: Cannot save config, no username set.")
            return
        data = {
            'language': self.language,
            'progress': self.progress,
            'level': self.level,
            'theme': self.current_theme,
        }
        save_user_config(self.username, data)
        print(f"Saved config for {self.username}")

    def set_theme(self, theme_name):
        """Sets the application theme."""
        self.current_theme = theme_name
        self.theme_colors = DARK_THEME if theme_name == 'dark' else LIGHT_THEME
        apply_theme(self.root, self.theme_colors)
        # Special case for root window background
        self.root.config(bg=self.theme_colors["bg"])

    def toggle_theme(self):
        """Switches between light and dark themes."""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.set_theme(new_theme)
        self.save_config() # Save theme preference immediately

    # --- Screen Management ---
    def clear_screen(self):
        """Removes all widgets from the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- Login / Language Selection ---
    def show_login_screen(self):
        self.clear_screen()
        self.username = None # Reset user data when going back to login
        self.language = None
        self.progress = 0
        self.level = "Beginner"
        self.set_theme(self.current_theme) # Re-apply theme in case it was changed

        login_frame = tk.Frame(self.root, padx=20, pady=40)
        login_frame.pack(expand=True)
        apply_theme(login_frame, self.theme_colors) # Apply theme to the frame

        tk.Label(login_frame, text="Language Mentor", font=self.header_font).pack(pady=(0, 30))
        tk.Label(login_frame, text="Enter your Nickname:", font=self.label_font).pack(pady=5)

        self.username_entry = tk.Entry(login_frame, width=30, font=self.label_font)
        self.username_entry.pack(pady=5)
        self.username_entry.focus_set() # Set focus to username entry

        # Frame for language buttons (initially hidden)
        self.lang_frame = tk.Frame(login_frame)
        # Pack it later when needed
        apply_theme(self.lang_frame, self.theme_colors)

        self.login_button = tk.Button(login_frame, text="Login / Register", command=self.handle_login_attempt, font=self.button_font, width=20)
        self.login_button.pack(pady=20)

        # Bind Enter key to login button
        self.root.bind('<Return>', lambda event=None: self.login_button.invoke())

        # Apply theme to newly created widgets within login_frame
        apply_theme(login_frame, self.theme_colors)

    def handle_login_attempt(self):
        # Unbind Enter key once button is clicked or Enter is pressed
        self.root.unbind('<Return>')

        entered_username = self.username_entry.get().strip()
        if not entered_username:
            messagebox.showwarning("Input Required", "Please enter your nickname.")
            # Re-bind Enter key if input was invalid
            self.root.bind('<Return>', lambda event=None: self.login_button.invoke())
            return

        if self.load_config(entered_username):
            # User exists, config loaded
            print(f"Welcome back, {self.username}!")
            self.show_main_dashboard()
        else:
            # New user
            print(f"Creating profile for new user: {entered_username}")
            self.username = entered_username
            # Set defaults for new user before showing language selection
            self.language = None
            self.progress = 0
            self.level = "Beginner"
            self.current_theme = 'light' # Default to light
            self.show_language_selection() # Proceed to language selection

    def show_language_selection(self):
        """Shows language selection buttons for a new user."""
        self.login_button.config(state=tk.DISABLED) # Disable login button now

        tk.Label(self.lang_frame, text="Choose a language to learn:", font=self.label_font).pack(pady=(15, 10))

        flags_subframe = tk.Frame(self.lang_frame)
        flags_subframe.pack(pady=5)
        apply_theme(flags_subframe, self.theme_colors)

        flag_images = {} # Keep references to images

        for lang, path in FLAGS.items():
            try:
                img = Image.open(path)
                # Resize more reasonably if needed, maintaining aspect ratio
                img.thumbnail((60, 60)) # Resize keeping aspect ratio, max 60x60
                photo = ImageTk.PhotoImage(img)
                flag_images[lang] = photo # Store reference

                btn = tk.Button(flags_subframe, image=photo, text=lang, compound=tk.TOP,
                                font=self.label_font, command=lambda l=lang: self.confirm_language(l),
                                width=80, height=80) # Adjust size as needed
                btn.image = photo # Keep a reference!
                btn.pack(side=tk.LEFT, padx=10, pady=5)

            except FileNotFoundError:
                print(f"Warning: Flag image not found at {path}. Using text button.")
                btn = tk.Button(flags_subframe, text=lang, font=self.label_font,
                                command=lambda l=lang: self.confirm_language(l), width=10)
                btn.pack(side=tk.LEFT, padx=10, pady=5)
            except Exception as e:
                print(f"Error loading image {path}: {e}")
                btn = tk.Button(flags_subframe, text=lang, font=self.label_font,
                                command=lambda l=lang: self.confirm_language(l), width=10)
                btn.pack(side=tk.LEFT, padx=10, pady=5)

        # Pack the language frame now that it's populated
        self.lang_frame.pack(pady=10)
        apply_theme(self.lang_frame, self.theme_colors) # Apply theme to the frame and its new children

    def confirm_language(self, selected_language):
        """Called when a new user clicks a language flag."""
        self.language = selected_language
        print(f"User '{self.username}' selected language: {self.language}")
        # Save the initial configuration for the new user
        self.save_config()
        messagebox.showinfo("Language Set", f"Great! You've chosen to learn {self.language}.")
        self.show_main_dashboard()


    # --- Main Dashboard ---
    def show_main_dashboard(self):
        self.clear_screen()
        self.set_theme(self.current_theme)

        # --- Top Bar ---
        top_frame = tk.Frame(self.root, pady=5, padx=10)
        top_frame.pack(fill=tk.X)
        apply_theme(top_frame, self.theme_colors)

        welcome_label = tk.Label(top_frame, text=f"Welcome, {self.username}!", font=self.header_font)
        welcome_label.pack(side=tk.LEFT)

        exit_button = tk.Button(top_frame, text="Logout", command=self.show_login_screen, font=self.button_font, width=8)
        exit_button.pack(side=tk.RIGHT, padx=(0, 5))

        theme_button = tk.Button(top_frame, text="Theme", command=self.toggle_theme, font=self.button_font, width=8)
        theme_button.pack(side=tk.RIGHT, padx=(0, 10))

        # --- Info Bar ---
        info_frame = tk.Frame(self.root, pady=5, padx=10)
        info_frame.pack(fill=tk.X)
        apply_theme(info_frame, self.theme_colors)

        self.exp_label = tk.Label(info_frame, text=f"EXP: {self.progress}", font=self.label_font)
        self.exp_label.pack(side=tk.LEFT, padx=(0, 15))

        self.level_label = tk.Label(info_frame, text=f"Level: {self.level}", font=self.label_font)
        self.level_label.pack(side=tk.LEFT, padx=(0, 15))

        self.language_label = tk.Label(info_frame, text=f"Learning: {self.language}", font=self.label_font)
        self.language_label.pack(side=tk.LEFT)

        # --- Daily Tip Area ---
        tip_frame = tk.LabelFrame(self.root, text="Daily Tip", padx=10, pady=10, font=self.label_font)
        tip_frame.pack(fill=tk.X, padx=10, pady=10)
        apply_theme(tip_frame, self.theme_colors)
        tip_frame.config(fg=self.theme_colors["fg"]) # Set label frame text color

        self.tip_textbox = scrolledtext.ScrolledText(tip_frame, height=5, wrap=tk.WORD, state=tk.DISABLED, font=self.label_font)
        self.tip_textbox.pack(fill=tk.X, expand=True)
        # Placeholder text
        self.tip_textbox.config(state=tk.NORMAL)
        self.tip_textbox.insert(tk.END, f"A helpful tip about learning {self.language} will appear here soon!")
        self.tip_textbox.config(state=tk.DISABLED)
        apply_theme(self.tip_textbox, self.theme_colors) # Apply theme specifically to text box

        # --- Center Buttons ---
        center_frame = tk.Frame(self.root, pady=5)
        center_frame.pack(expand=False)
        apply_theme(center_frame, self.theme_colors)

        level_button = tk.Button(center_frame, text="Level Proficiency Detector", command=self.detect_level, font=self.button_font, width=25, height=2)
        level_button.pack(pady=10)

        quiz_button = tk.Button(center_frame, text="Quiz", command=self.start_quiz, font=self.button_font, width=25, height=2)
        quiz_button.pack(pady=10)

        # Apply theme to all widgets on dashboard
        apply_theme(self.root, self.theme_colors)
        self.root.config(bg=self.theme_colors["bg"]) # Ensure root bg is set

        # Load initial tip (or other initial actions)
        # self.generate_tip() # Maybe call this here or leave it manual

    # --- Placeholder/Core Logic Functions (Keep your CrewAI/threading logic here) ---

    def update_status(self, text):
         # You might want a dedicated status bar at the bottom if needed
         print(f"Status: {text}") # Simple print for now
         # Example: self.status_label.config(text=text) if you add a status bar

    def update_main_content(self, text, title="Info"):
        """Updates the Daily Tip box or shows a message box."""
        # Option 1: Update the tip box (if appropriate)
        # self.tip_textbox.config(state=tk.NORMAL)
        # self.tip_textbox.delete(1.0, tk.END)
        # self.tip_textbox.insert(tk.END, text)
        # self.tip_textbox.config(state=tk.DISABLED)

        # Option 2: Show a popup (better for results/feedback)
        messagebox.showinfo(title, text)
        self.root.update_idletasks()

    def _update_ui_safe(self, func, *args):
        """Helper to schedule UI updates from threads."""
        self.root.after(0, func, *args)

    # --- Tip Generation ---
    def generate_tip(self):
        # This would ideally update the self.tip_textbox
        self.update_status("Generating tip...")
        # Make the tip box writable, add placeholder, disable again
        self.tip_textbox.config(state=tk.NORMAL)
        self.tip_textbox.delete(1.0, tk.END)
        self.tip_textbox.insert(tk.END, "🧠 Generating a tip...")
        self.tip_textbox.see(tk.END)
        self.tip_textbox.config(state=tk.DISABLED)
        apply_theme(self.tip_textbox, self.theme_colors) # Reapply theme
        threading.Thread(target=self._run_tip_task, daemon=True).start()

    def _run_tip_task(self):
        try:
            # --- Replace with your actual CrewAI/API call ---
            import time
            time.sleep(2) # Simulate work
            result = f"Here's a tip for {self.language}: Practice speaking even if it's just to yourself!"
            # --- End Replace ---

            self._update_ui_safe(self._display_tip, result)
            self._update_ui_safe(self.update_status, "Tip generated.")
        except Exception as e:
            self._update_ui_safe(self._display_tip, f"Error generating tip: {e}")
            self._update_ui_safe(self.update_status, "Error")
            print(f"Tip generation error: {e}")
            # import traceback
            # print(traceback.format_exc())

    def _display_tip(self, tip_text):
        """Safely updates the tip textbox from any thread."""
        self.tip_textbox.config(state=tk.NORMAL)
        self.tip_textbox.delete(1.0, tk.END)
        self.tip_textbox.insert(tk.END, tip_text)
        self.tip_textbox.config(state=tk.DISABLED)
        apply_theme(self.tip_textbox, self.theme_colors) # Reapply theme

    # --- Quiz ---
    def start_quiz(self):
        # Placeholder - use your existing quiz logic, adapting UI updates
        self.update_status("Starting quiz...")
        messagebox.showinfo("Quiz", "Quiz functionality needs to be implemented.")
        # Example: threading.Thread(target=self._prepare_quiz).start()

    # --- Level Detection ---
    def detect_level(self):
        self.update_status("Detecting level...")
        # Show feedback in a popup for now
        self.update_main_content("🔍Proficiency detection functionality needs to be implemented.", title="Proficiency Level Detection")

# --- Main Execution ---
if __name__ == "__main__":

    # Ensure the flags directory exists or provide a clear error
    if not FLAGS_DIR.is_dir():
        print(f"ERROR: Flags directory not found at '{FLAGS_DIR}'. Please create it and add flag images (e.g., uk.png, japan.png, spain.png).")
        # Optionally exit or continue without flags
        # exit()

    root = tk.Tk()
    app = LanguageMentorApp(root)
    root.mainloop()