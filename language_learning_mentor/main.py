import sys
from PySide6.QtWidgets import QApplication

# Assuming ui.main_window exists and contains the main application window class
from gui.main_window import MainWindow

# Set the application style (optional, but good practice)
# print("Available styles:", QApplication.setStyle('Fusion')) # Uncomment to see available styles
QApplication.setStyle('Fusion')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # The MainWindow class will now handle creating/connecting the controller and other UI parts
    window = MainWindow()
    window.show()
    sys.exit(app.exec())