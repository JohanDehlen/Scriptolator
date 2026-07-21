from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
)


class ScriptEditor(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ---------------------------------------
        # Toolbar
        # ---------------------------------------

        toolbar = QHBoxLayout()

        self.openButton = QPushButton("Open")

        self.saveButton = QPushButton("Save")

        self.clearButton = QPushButton("Clear")

        self.wordLabel = QLabel("Words: 0")

        self.timeLabel = QLabel("Time: 0 sec")

        toolbar.addWidget(self.openButton)
        toolbar.addWidget(self.saveButton)
        toolbar.addWidget(self.clearButton)

        toolbar.addStretch()

        toolbar.addWidget(self.wordLabel)
        toolbar.addWidget(self.timeLabel)

        layout.addLayout(toolbar)

        # ---------------------------------------
        # Text editor
        # ---------------------------------------

        self.editor = QTextEdit()

        self.editor.setPlaceholderText(
            "Paste or type your narration here..."
        )

        layout.addWidget(self.editor)

        self.editor.textChanged.connect(self.update_stats)

    def update_stats(self):

        text = self.editor.toPlainText()

        words = len(text.split())

        self.wordLabel.setText(f"Words: {words}")

        seconds = round(words / 2.5)

        self.timeLabel.setText(
            f"Time: {seconds} sec"
        )