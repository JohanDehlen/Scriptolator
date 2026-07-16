from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QHBoxLayout


class OutputPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QFormLayout(self)

        folderLayout = QHBoxLayout()

        self.folder = QLineEdit()

        self.browse = QPushButton("Browse...")

        folderLayout.addWidget(self.folder)
        folderLayout.addWidget(self.browse)

        self.filename = QLineEdit()

        layout.addRow("Output Folder", folderLayout)
        layout.addRow("Output File", self.filename)