from PySide6.QtWidgets import QLabel


class StatusBar(QLabel):

    def __init__(self):
        super().__init__()

        self.setText("Ready")