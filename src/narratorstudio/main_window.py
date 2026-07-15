from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Narrator Studio v1.0")

        self.resize(900, 600)

        central = QWidget()

        self.setCentralWidget(central)

        layout = QVBoxLayout()

        central.setLayout(layout)

        title = QLabel("Narrator Studio")
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)

        subtitle = QLabel(
            "Professional AI Narration using Microsoft Edge Voices"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)