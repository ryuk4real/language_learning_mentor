from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication # Needed to apply palette

class StyleManager:
    """Handles creating and applying color palettes for themes."""

    def __init__(self):
        self._light_palette = self._create_light_palette()
        self._dark_palette = self._create_dark_palette()

    def _create_light_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240)) # Background
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white) # TextEdit, LineEdit background
        palette.setColor(QPalette.Text, Qt.black) # TextEdit, LineEdit foreground
        palette.setColor(QPalette.Button, QColor(200, 200, 200)) # Button background
        palette.setColor(QPalette.ButtonText, Qt.black) # Button text
        palette.setColor(QPalette.Highlight, QColor(48, 140, 198)) # Selection color
        palette.setColor(QPalette.HighlightedText, Qt.white)
        # Add more roles as needed
        return palette

    def _create_dark_palette(self):
        palette = QPalette()
        dark_gray = QColor(53, 53, 53)
        light_gray = QColor(180, 180, 180)
        mid_gray = QColor(68, 68, 68)
        dark_blue = QColor(42, 130, 218) # Highlight color

        palette.setColor(QPalette.Window, dark_gray) # Background
        palette.setColor(QPalette.WindowText, light_gray)
        palette.setColor(QPalette.Base, mid_gray.darker(150)) # TextEdit, LineEdit background
        palette.setColor(QPalette.AlternateBase, mid_gray) # Alternate rows in lists/tables
        palette.setColor(QPalette.ToolTipBase, dark_gray)
        palette.setColor(QPalette.ToolTipText, light_gray)
        palette.setColor(QPalette.Text, light_gray) # TextEdit, LineEdit foreground
        palette.setColor(QPalette.Button, mid_gray) # Button background
        palette.setColor(QPalette.ButtonText, light_gray) # Button text
        palette.setColor(QPalette.BrightText, Qt.red) # Used for errors etc.
        palette.setColor(QPalette.Link, dark_blue.lighter()) # Link text color
        palette.setColor(QPalette.Highlight, dark_blue) # Selection color
        palette.setColor(QPalette.HighlightedText, Qt.black)

        # Disabled colors
        disabled_color = light_gray.darker(150)
        palette.setColor(QPalette.Disabled, QPalette.Text, disabled_color)
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_color)
        palette.setColor(QPalette.Disabled, QPalette.WindowText, disabled_color)
        # ... add other disabled roles if necessary

        return palette

    def apply_theme(self, theme_preference):
        # TODO: implement
        pass