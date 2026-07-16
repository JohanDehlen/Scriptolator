from PySide6.QtWidgets import (
    QLabel,
    QGroupBox,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from version import APP_NAME, APP_VERSION

from widgets.script_editor import ScriptEditor
from widgets.voice_panel import VoicePanel
from widgets.button_bar import ButtonBar
from widgets.output_panel import OutputPanel
from widgets.status_bar import StatusBar


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1280, 850)

        # -------------------------------------------------
        # Central Widget
        # -------------------------------------------------

        central = QWidget()
        self.setCentralWidget(central)

        mainLayout = QVBoxLayout(central)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Main Content
        # -------------------------------------------------

        contentLayout = QHBoxLayout()

        #
        # Left Column
        #

        leftLayout = QVBoxLayout()

        scriptGroup = QGroupBox("Script")

        scriptLayout = QVBoxLayout()

        self.scriptEditor = ScriptEditor()

        scriptLayout.addWidget(self.scriptEditor)

        scriptGroup.setLayout(scriptLayout)

        leftLayout.addWidget(scriptGroup)

        outputGroup = QGroupBox("Output")

        outputLayout = QVBoxLayout()

        self.outputPanel = OutputPanel()

        outputLayout.addWidget(self.outputPanel)

        outputGroup.setLayout(outputLayout)

        leftLayout.addWidget(outputGroup)

        #
        # Right Column
        #

        rightLayout = QVBoxLayout()

        voiceGroup = QGroupBox("Voice Settings")

        voiceLayout = QVBoxLayout()

        self.voicePanel = VoicePanel()

        voiceLayout.addWidget(self.voicePanel)

        voiceGroup.setLayout(voiceLayout)

        rightLayout.addWidget(voiceGroup)

        rightLayout.addStretch()

        contentLayout.addLayout(leftLayout, 3)
        contentLayout.addLayout(rightLayout, 1)

        mainLayout.addLayout(contentLayout)

        # -------------------------------------------------
        # Button Bar
        # -------------------------------------------------

        self.buttonBar = ButtonBar()

        mainLayout.addWidget(self.buttonBar)

        # -------------------------------------------------
        # Status Bar
        # -------------------------------------------------

        self.statusBarWidget = StatusBar()

        self.statusBarWidget.setStyleSheet("""
            padding: 8px;
            border-top: 1px solid gray;
        """)

        mainLayout.addWidget(self.statusBarWidget)