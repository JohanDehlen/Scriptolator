from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QHBoxLayout


class ButtonBar(QWidget):

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)

        self.generate = QPushButton("Generate MP3")

        self.play = QPushButton("Play")

        self.open = QPushButton("Open Folder")

        self.save = QPushButton("Save Project")

        self.load = QPushButton("Load Project")

        self.clear = QPushButton("Clear")

        layout.addWidget(self.generate)
        layout.addWidget(self.play)
        layout.addWidget(self.open)

        layout.addStretch()

        layout.addWidget(self.save)
        layout.addWidget(self.load)
        layout.addWidget(self.clear)