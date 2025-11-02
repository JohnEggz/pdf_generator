# src/main.py
import sys
import signal
from PyQt6.QtWidgets import QApplication

# Import the MainWindow class from your GUI application file
from src.gui.app import MainWindow

def main():
    """
    Main entry point for the application.
    Initializes the PyQt application and shows the main window.
    """
    # Create the application instance
    app = QApplication(sys.argv)

    # Allow Ctrl+C to exit the application from the console
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Create an instance of your main window and show it
    window = MainWindow()
    window.show()

    # Start the application's event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
