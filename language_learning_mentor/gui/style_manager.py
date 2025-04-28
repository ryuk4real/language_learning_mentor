# gui/style_manager.py
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

class StyleManager:
    """Gestisce palette tema chiaro/scuro e un foglio di stile QSS globale."""

    def __init__(self):
        self._light_palette = self._create_light_palette()
        self._dark_palette  = self._create_dark_palette()
        self._common_qss    = self._build_common_qss()

    # ------------------------------------------------------------------ PALETTE
    def _create_light_palette(self):
        p = QPalette()
        p.setColor(QPalette.Window, QColor(248, 248, 248))
        p.setColor(QPalette.WindowText, Qt.black)
        p.setColor(QPalette.Base, Qt.white)
        p.setColor(QPalette.Text, Qt.black)
        p.setColor(QPalette.Button, QColor(220, 220, 220))
        p.setColor(QPalette.ButtonText, Qt.black)
        p.setColor(QPalette.Highlight, QColor(48, 140, 198))
        p.setColor(QPalette.HighlightedText, Qt.white)
        return p

    def _create_dark_palette(self):
        p = QPalette()
        dark  = QColor(45, 45, 45)
        mid   = QColor(70, 70, 70)
        light = QColor(200, 200, 200)
        p.setColor(QPalette.Window, dark)
        p.setColor(QPalette.WindowText, light)
        p.setColor(QPalette.Base, mid.darker(150))
        p.setColor(QPalette.AlternateBase, mid)
        p.setColor(QPalette.Text, light)
        p.setColor(QPalette.Button, mid)
        p.setColor(QPalette.ButtonText, dark)
        p.setColor(QPalette.Highlight, QColor(42, 130, 218))
        p.setColor(QPalette.HighlightedText, Qt.black)
        p.setColor(QPalette.Disabled, QPalette.Text, light.darker(140))
        p.setColor(QPalette.Disabled, QPalette.ButtonText, light.darker(140))
        return p

    # ------------------------------------------------------------------ QSS
    def _build_common_qss(self):
        """Restituisce un foglio di stile comune a entrambi i temi."""
        return """
        QWidget {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            font-size: 12px;
        }

        QPushButton {
            border-radius: 6px;
            padding: 6px 12px;
            border: 1px solid #8f8f8f;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                       stop:0 #f6f7fa, stop:1 #dadbde);
        }
        QPushButton:hover   { background-color: #e1ecf4; }
        QPushButton:pressed { background-color: #c6d4e1; }

        QLineEdit, QTextEdit {
            border: 1px solid #b0b0b0;
            border-radius: 4px;
            padding: 4px;
        }

        QGroupBox {
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            margin-top: 12px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        """

    # ------------------------------------------------------------------ APPLY
    def apply_theme(self, theme_preference: str):
        """Applica la palette e il foglio di stile."""
        app = QApplication.instance()
        if not app:
            print("Warning: QApplication instance not found.")
            return

        if theme_preference == 'dark':
            print("Applying dark theme.")
            app.setPalette(self._dark_palette)
        else:
            print("Applying light theme.")
            app.setPalette(self._light_palette)

        # Il QSS è identico per entrambi i temi
        app.setStyleSheet(self._common_qss)

    # ------------------------------------------------------------------ EXTRA
    def get_palette(self, theme_preference: str):
        """Ritorna la palette corrispondente al tema richiesto."""
        return self._dark_palette if theme_preference == 'dark' else self._light_palette

    def get_system_theme(self):
        """
        Prova a rilevare il tema di sistema; ritorna 'light' se non determinabile.
        Puoi specializzarla ulteriormente per il tuo OS.
        """
        from PySide6.QtCore import QSysInfo
        platform_name = QSysInfo.productType().lower()
        try:
            if 'windows' in platform_name:
                import winreg
                reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return 'light' if value == 1 else 'dark'
        except Exception:
            pass
        return 'light'
