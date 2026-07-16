from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QSlider,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt

from services.edge_tts_service import EdgeTTSService


class VoicePanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ----------------------------
        # Voice
        # ----------------------------

        layout.addWidget(QLabel("Voice"))

        self.voiceCombo = QComboBox()
        self.voiceCombo.addItem("Loading voices...")
        layout.addWidget(self.voiceCombo)

        # ----------------------------
        # Speed
        # ----------------------------

        layout.addWidget(QLabel("Speed"))

        self.speedSlider = QSlider(Qt.Horizontal)
        self.speedSlider.setRange(-100, 100)
        self.speedSlider.setValue(0)

        layout.addWidget(self.speedSlider)

        # ----------------------------
        # Pitch
        # ----------------------------

        layout.addWidget(QLabel("Pitch"))

        self.pitchSlider = QSlider(Qt.Horizontal)
        self.pitchSlider.setRange(-100, 100)
        self.pitchSlider.setValue(0)

        layout.addWidget(self.pitchSlider)

        # ----------------------------
        # Volume
        # ----------------------------

        layout.addWidget(QLabel("Volume"))

        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(100)

        layout.addWidget(self.volumeSlider)

        # ----------------------------
        # Preview Button
        # ----------------------------

        self.previewButton = QPushButton("Preview Voice")
        layout.addWidget(self.previewButton)

        layout.addStretch()

        # Load Edge voices
        self.load_voices()

    def load_voices(self):
        """
        Load all available Microsoft Edge Neural voices.
        """

        self.voiceCombo.setEnabled(False)
        self.voiceCombo.clear()
        self.voiceCombo.addItem("Loading voices...")

        try:
            voices = EdgeTTSService.get_voices()

            self.voiceCombo.clear()

            if not voices:
                self.voiceCombo.addItem("No voices found")
                return

            self.voiceCombo.addItems(voices)
            self.voiceCombo.setEnabled(True)

        except Exception as ex:
            self.voiceCombo.clear()
            self.voiceCombo.addItem("Unable to load voices")

            QMessageBox.critical(
                self,
                "Voice Loading Error",
                f"Microsoft Edge voices could not be loaded.\n\n{ex}",
            )