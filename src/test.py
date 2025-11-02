import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QTextEdit,
)
from PyQt6.QtCore import Qt, QEvent


class TextViewer(QDialog):
    """Simple scrollable text viewer"""

    def __init__(self, text: str, title: str = "Document Viewer", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(600, 500)

        layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.text_edit.setPlainText(text)
        layout.addWidget(self.text_edit)

        # Optional: Close with Ctrl+W or Esc
        self.text_edit.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            mods = event.modifiers()
            if key == Qt.Key.Key_Escape or (
                key == Qt.Key.Key_W
                and mods & Qt.KeyboardModifier.ControlModifier
            ):
                self.close()
                return True
        return super().eventFilter(obj, event)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 200, 100)

        btn = QPushButton("Open Document", self)
        btn.clicked.connect(self.show_text)
        btn.setGeometry(25, 30, 150, 40)

    def show_text(self):
        # Internal path to your text file
        path = "/home/john/Projects/Work/Pyhton/pdf_generator_for_mom_2_1/data.json"

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            text = f"Could not read file:\n{e}"

        viewer = TextViewer(text, title=f"Viewing: {path}", parent=self)
        viewer.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
