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
        """Applies the specified theme palette to the application."""
        app = QApplication.instance()
        if not app:
            print("Warning: QApplication instance not found. Cannot apply theme.")
            return

        if theme_preference == 'dark':
            print("Applying dark theme.")
            app.setPalette(self._dark_palette)
        else: # Default to light
            print("Applying light theme.")
            app.setPalette(self._light_palette)

    def get_palette(self, theme_preference):
         """Returns the palette object for a given theme preference."""
         if theme_preference == 'dark':
             return self._dark_palette
         else:
             return self._light_palette
         
    def get_system_theme(self):
        """Detects whether the system is using a dark or light theme in a cross-platform way."""
        from PySide6.QtCore import QOperatingSystemVersion, QSysInfo
        
        # Default to light theme if detection fails
        default_theme = 'light'
        
        try:
            # Method 1: Check for specific platform indicators
            platform_name = QSysInfo.productType().lower()
            
            if 'windows' in platform_name:
                # Windows-specific theme detection
                try:
                    import winreg
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                    key = winreg.OpenKey(registry, key_path)
                    # AppsUseLightTheme = 0 means dark theme
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    return 'light' if value == 1 else 'dark'
                except Exception as e:
                    print(f"Windows theme detection error: {e}")
                    
            elif any(x in platform_name for x in ['linux', 'unix']):
                # Linux theme detection via environment variables or gsettings
                try:
                    # Try gsettings for GNOME/GTK-based desktops
                    import subprocess
                    try:
                        result = subprocess.run(
                            ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                            capture_output=True, text=True, timeout=1
                        )
                        output = result.stdout.strip().lower()
                        if 'dark' in output:
                            return 'dark'
                        elif 'light' in output or 'default' in output:
                            return 'light'
                    except (subprocess.SubprocessError, FileNotFoundError):
                        pass  # gsettings not available or command failed
                    
                    # Fallback check for common environment variables
                    import os
                    desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
                    if desktop_env:
                        if 'kde' in desktop_env:
                            # Try KDE specific method
                            try:
                                result = subprocess.run(
                                    ['kreadconfig5', '--group', 'General', '--key', 'ColorScheme', '--file', 'kdeglobals'],
                                    capture_output=True, text=True, timeout=1
                                )
                                output = result.stdout.strip().lower()
                                return 'dark' if 'dark' in output else 'light'
                            except (subprocess.SubprocessError, FileNotFoundError):
                                pass  # kreadconfig5 not available
                except Exception as e:
                    print(f"Linux theme detection error: {e}")
            
            # Method 2: Fallback using application palette comparison
            from PySide6.QtGui import QGuiApplication
            palette = QGuiApplication.palette()
            window_color = palette.color(palette.Window)
            text_color = palette.color(palette.WindowText)
            
            # If text is lighter than background, likely dark mode
            return 'dark' if text_color.lightness() > window_color.lightness() else 'light'
            
        except Exception as e:
            print(f"Theme detection error: {e}")
            return default_theme