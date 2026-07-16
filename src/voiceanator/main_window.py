from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QGroupBox,
)

from version import APP_NAME, APP_VERSION

from widgets.script_editor import ScriptEditor
from widgets.voice_panel import VoicePanel


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1200, 800)

        # -----------------------------
        # Central Widget
        # -----------------------------

        central = QWidget()
        self.setCentralWidget(central)

        mainLayout = QVBoxLayout(central)

        # -----------------------------
        # Header
        # -----------------------------

        title = QLabel(APP_NAME)
        title.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
        """)

        subtitle = QLabel(
            "Professional AI Narration using Microsoft Edge Voices"
        )

        mainLayout.addWidget(title)
        mainLayout.addWidget(subtitle)

        # -----------------------------
        # Main Content
        # -----------------------------

        contentLayout = QHBoxLayout()

        # Script Panel

        scriptGroup = QGroupBox("Script")

        scriptLayout = QVBoxLayout()

        self.scriptEditor = ScriptEditor()

        scriptLayout.addWidget(self.scriptEditor)

        scriptGroup.setLayout(scriptLayout)

        # Voice Panel

        voiceGroup = QGroupBox("Voice Settings")

        voiceLayout = QVBoxLayout()

        self.voicePanel = VoicePanel()

        voiceLayout.addWidget(self.voicePanel)

        voiceGroup.setLayout(voiceLayout)

        contentLayout.addWidget(scriptGroup, 3)
        contentLayout.addWidget(voiceGroup, 1)

        mainLayout.addLayout(contentLayout)

        # -----------------------------
        # Status Bar
        # -----------------------------

        self.status = QLabel("Ready")

        self.status.setStyleSheet("""
            padding: 8px;
            border-top: 1px solid gray;
        """)

        mainLayout.addWidget(self.status)