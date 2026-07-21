from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

from PySide6.QtCore import QThread, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QMouseEvent
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from services.edge_tts_service import EdgeTTSService


class ResettableSlider(QSlider):
    """Slider that resets to its default value when double-clicked."""

    def __init__(
        self,
        orientation: Qt.Orientation,
        default_value: int,
    ) -> None:
        super().__init__(orientation)

        self.default_value = default_value

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Reset the slider to its configured default value."""

        self.setValue(self.default_value)
        event.accept()


class VoicePreviewThread(QThread):
    """Generate a short voice preview without blocking the interface."""

    preview_generated = Signal(str)
    preview_failed = Signal(str)

    def __init__(
        self,
        voice: str,
        output_path: Path,
        rate: str,
        pitch: str,
        volume: str,
    ) -> None:
        super().__init__()

        self.voice = voice
        self.output_path = output_path
        self.rate = rate
        self.pitch = pitch
        self.volume = volume

    def run(self) -> None:
        """Generate the preview MP3 and report the result."""

        preview_text = (
            "In the beginning, God created the heavens and the earth. "
            "This is a preview of the selected Scriptalator narration voice."
        )

        try:
            generated_path = EdgeTTSService.generate_mp3(
                text=preview_text,
                voice=self.voice,
                output_path=self.output_path,
                rate=self.rate,
                pitch=self.pitch,
                volume=self.volume,
            )
        except Exception as error:
            self.preview_failed.emit(str(error))
        else:
            self.preview_generated.emit(str(generated_path))


class VoicePanel(QWidget):
    """Display, filter, and preview Microsoft Edge narration voices."""

    LANGUAGE_NAMES = {
        "af": "Afrikaans",
        "am": "Amharic",
        "ar": "Arabic",
        "az": "Azerbaijani",
        "bg": "Bulgarian",
        "bn": "Bengali",
        "bs": "Bosnian",
        "ca": "Catalan",
        "cs": "Czech",
        "cy": "Welsh",
        "da": "Danish",
        "de": "German",
        "el": "Greek",
        "en": "English",
        "es": "Spanish",
        "et": "Estonian",
        "eu": "Basque",
        "fa": "Persian",
        "fi": "Finnish",
        "fil": "Filipino",
        "fr": "French",
        "ga": "Irish",
        "gl": "Galician",
        "gu": "Gujarati",
        "he": "Hebrew",
        "hi": "Hindi",
        "hr": "Croatian",
        "hu": "Hungarian",
        "hy": "Armenian",
        "id": "Indonesian",
        "is": "Icelandic",
        "it": "Italian",
        "ja": "Japanese",
        "jv": "Javanese",
        "ka": "Georgian",
        "kk": "Kazakh",
        "km": "Khmer",
        "kn": "Kannada",
        "ko": "Korean",
        "lo": "Lao",
        "lt": "Lithuanian",
        "lv": "Latvian",
        "mk": "Macedonian",
        "ml": "Malayalam",
        "mn": "Mongolian",
        "mr": "Marathi",
        "ms": "Malay",
        "mt": "Maltese",
        "my": "Burmese",
        "nb": "Norwegian",
        "ne": "Nepali",
        "nl": "Dutch",
        "pl": "Polish",
        "ps": "Pashto",
        "pt": "Portuguese",
        "ro": "Romanian",
        "ru": "Russian",
        "si": "Sinhala",
        "sk": "Slovak",
        "sl": "Slovenian",
        "so": "Somali",
        "sq": "Albanian",
        "sr": "Serbian",
        "su": "Sundanese",
        "sv": "Swedish",
        "sw": "Swahili",
        "ta": "Tamil",
        "te": "Telugu",
        "th": "Thai",
        "tr": "Turkish",
        "uk": "Ukrainian",
        "ur": "Urdu",
        "uz": "Uzbek",
        "vi": "Vietnamese",
        "zh": "Chinese",
        "zu": "Zulu",
    }

    INVALID_VOICE_VALUES = {
        "Loading voices...",
        "No voices found",
        "Unable to load voices",
    }

    def __init__(self) -> None:
        super().__init__()

        self.all_voices: list[str] = []
        self.preview_thread: VoicePreviewThread | None = None
        self.last_preview_path: Path | None = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Select Language"))

        self.languageFilter = QComboBox()
        self.languageFilter.addItem("Loading languages...")
        self.languageFilter.setEnabled(False)

        layout.addWidget(self.languageFilter)

        layout.addWidget(QLabel("Voice"))

        self.voiceCombo = QComboBox()
        self.voiceCombo.addItem("Loading voices...")
        self.voiceCombo.setEnabled(False)

        layout.addWidget(self.voiceCombo)

        layout.addWidget(QLabel("Speed"))

        self.speedSlider = self._create_centered_slider()
        layout.addWidget(self.speedSlider)
        layout.addLayout(
            self._create_scale_labels("-100%", "0%", "+100%")
        )

        self.speedValueLabel = QLabel("Current speed: 0%")
        self.speedValueLabel.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(self.speedValueLabel)

        layout.addWidget(QLabel("Pitch"))

        self.pitchSlider = self._create_centered_slider()
        layout.addWidget(self.pitchSlider)
        layout.addLayout(
            self._create_scale_labels(
                "-100 Hz",
                "0 Hz",
                "+100 Hz",
            )
        )

        self.pitchValueLabel = QLabel("Current pitch: 0 Hz")
        self.pitchValueLabel.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(self.pitchValueLabel)

        layout.addWidget(QLabel("Volume"))

        self.volumeSlider = ResettableSlider(
            Qt.Orientation.Horizontal,
            default_value=100,
        )
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(100)
        self.volumeSlider.setTickPosition(
            QSlider.TickPosition.TicksBelow
        )
        self.volumeSlider.setTickInterval(50)

        layout.addWidget(self.volumeSlider)
        layout.addLayout(
            self._create_scale_labels("0%", "50%", "100%")
        )

        self.volumeValueLabel = QLabel("Current volume: 100%")
        self.volumeValueLabel.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(self.volumeValueLabel)

        reset_hint = QLabel(
            "Tip: Double-click a slider to reset it."
        )
        reset_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        reset_hint.setStyleSheet("font-style: italic;")

        layout.addWidget(reset_hint)

        self.previewButton = QPushButton("Preview Voice")
        layout.addWidget(self.previewButton)

        layout.addStretch()

        self.languageFilter.currentIndexChanged.connect(
            self._apply_language_filter
        )
        self.previewButton.clicked.connect(
            self._preview_voice
        )
        self.speedSlider.valueChanged.connect(
            self._update_speed_label
        )
        self.pitchSlider.valueChanged.connect(
            self._update_pitch_label
        )
        self.volumeSlider.valueChanged.connect(
            self._update_volume_label
        )

        self.load_voices()

    @staticmethod
    def _create_centered_slider() -> ResettableSlider:
        """Create a slider with minimum, centre, and maximum ticks."""

        slider = ResettableSlider(
            Qt.Orientation.Horizontal,
            default_value=0,
        )
        slider.setRange(-100, 100)
        slider.setValue(0)
        slider.setTickPosition(
            QSlider.TickPosition.TicksBelow
        )
        slider.setTickInterval(100)
        slider.setSingleStep(1)
        slider.setPageStep(10)

        return slider

    @staticmethod
    def _create_scale_labels(
        minimum_text: str,
        centre_text: str,
        maximum_text: str,
    ) -> QHBoxLayout:
        """Create labels aligned beneath a slider."""

        scale_layout = QHBoxLayout()

        minimum_label = QLabel(minimum_text)
        centre_label = QLabel(centre_text)
        maximum_label = QLabel(maximum_text)

        centre_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        maximum_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        centre_label.setStyleSheet("font-weight: bold;")

        scale_layout.addWidget(minimum_label)
        scale_layout.addStretch()
        scale_layout.addWidget(centre_label)
        scale_layout.addStretch()
        scale_layout.addWidget(maximum_label)

        return scale_layout

    def load_voices(self) -> None:
        """Load Microsoft Edge voices and populate language choices."""

        self.voiceCombo.setEnabled(False)
        self.voiceCombo.clear()
        self.voiceCombo.addItem("Loading voices...")

        try:
            self.all_voices = EdgeTTSService.get_voices()
        except Exception as error:
            self.all_voices = []

            self.languageFilter.clear()
            self.languageFilter.addItem("Languages unavailable")
            self.languageFilter.setEnabled(False)

            self.voiceCombo.clear()
            self.voiceCombo.addItem("Unable to load voices")

            QMessageBox.critical(
                self,
                "Voice Loading Error",
                (
                    "Microsoft Edge voices could not be loaded.\n\n"
                    f"{error}"
                ),
            )
            return

        self._populate_languages()
        self._apply_language_filter()

    def _populate_languages(self) -> None:
        """Populate the language dropdown from available voices."""

        language_codes = {
            self._get_voice_language_code(voice)
            for voice in self.all_voices
        }

        language_entries = sorted(
            (
                self.LANGUAGE_NAMES.get(
                    language_code,
                    language_code.upper(),
                ),
                language_code,
            )
            for language_code in language_codes
            if language_code
        )

        self.languageFilter.blockSignals(True)
        self.languageFilter.clear()
        self.languageFilter.addItem(
            "All Languages",
            "",
        )

        for language_name, language_code in language_entries:
            self.languageFilter.addItem(
                language_name,
                language_code,
            )

        self.languageFilter.setCurrentIndex(0)
        self.languageFilter.setEnabled(True)
        self.languageFilter.blockSignals(False)

    def _apply_language_filter(self, _: int = -1) -> None:
        """Show voices belonging to the selected language."""

        current_voice = self.voiceCombo.currentText().strip()
        selected_language = (
            self.languageFilter.currentData() or ""
        )

        if selected_language:
            matching_voices = [
                voice
                for voice in self.all_voices
                if self._get_voice_language_code(voice)
                == selected_language
            ]
        else:
            matching_voices = self.all_voices.copy()

        self.voiceCombo.blockSignals(True)
        self.voiceCombo.clear()

        if not matching_voices:
            self.voiceCombo.addItem("No voices found")
            self.voiceCombo.setEnabled(False)
            self.voiceCombo.blockSignals(False)
            return

        self.voiceCombo.addItems(matching_voices)
        self.voiceCombo.setEnabled(True)

        current_index = self.voiceCombo.findText(current_voice)

        if current_index >= 0:
            self.voiceCombo.setCurrentIndex(current_index)

        self.voiceCombo.blockSignals(False)

    @staticmethod
    def _get_voice_language_code(voice: str) -> str:
        """Return the language code at the start of a voice name."""

        return voice.split("-", 1)[0].lower()

    def _preview_voice(self) -> None:
        """Generate and play a preview of the selected voice."""

        if (
            self.preview_thread is not None
            and self.preview_thread.isRunning()
        ):
            QMessageBox.information(
                self,
                "Preview In Progress",
                "Scriptalator is already generating a voice preview.",
            )
            return

        voice = self.voiceCombo.currentText().strip()

        if not self._is_valid_voice(voice):
            QMessageBox.warning(
                self,
                "Voice Not Available",
                "Select a valid Microsoft Edge voice first.",
            )
            return

        preview_path = (
            Path(gettempdir())
            / f"scriptalator-preview-{uuid4().hex}.mp3"
        )

        self.preview_thread = VoicePreviewThread(
            voice=voice,
            output_path=preview_path,
            rate=self._format_percentage(
                self.speedSlider.value()
            ),
            pitch=self._format_pitch(
                self.pitchSlider.value()
            ),
            volume=self._format_percentage(
                self.volumeSlider.value() - 100
            ),
        )

        self.preview_thread.preview_generated.connect(
            self._preview_generated
        )
        self.preview_thread.preview_failed.connect(
            self._preview_failed
        )
        self.preview_thread.finished.connect(
            self._preview_finished
        )
        self.preview_thread.finished.connect(
            self.preview_thread.deleteLater
        )

        self._set_preview_controls_enabled(False)
        self.previewButton.setText("Generating Preview...")

        self.preview_thread.start()

    def _preview_generated(self, preview_path: str) -> None:
        """Open the generated preview in the default audio player."""

        self.last_preview_path = Path(preview_path)

        opened = QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(self.last_preview_path.resolve())
            )
        )

        if not opened:
            QMessageBox.critical(
                self,
                "Unable to Play Preview",
                (
                    "Windows could not open the preview MP3 in the "
                    "default audio player."
                ),
            )

    def _preview_failed(self, error_message: str) -> None:
        """Show an error when preview generation fails."""

        QMessageBox.critical(
            self,
            "Voice Preview Failed",
            (
                "Scriptalator could not generate the voice preview.\n\n"
                f"{error_message}"
            ),
        )

    def _preview_finished(self) -> None:
        """Restore the preview controls after generation."""

        self._set_preview_controls_enabled(True)
        self.previewButton.setText("Preview Voice")
        self.preview_thread = None

    def _set_preview_controls_enabled(
        self,
        enabled: bool,
    ) -> None:
        """Enable or disable controls used by voice preview."""

        self.languageFilter.setEnabled(enabled)
        self.voiceCombo.setEnabled(enabled)
        self.speedSlider.setEnabled(enabled)
        self.pitchSlider.setEnabled(enabled)
        self.volumeSlider.setEnabled(enabled)
        self.previewButton.setEnabled(enabled)

    def _update_speed_label(self, value: int) -> None:
        """Display the current speed adjustment."""

        self.speedValueLabel.setText(
            f"Current speed: {value:+d}%"
        )

    def _update_pitch_label(self, value: int) -> None:
        """Display the current pitch adjustment."""

        self.pitchValueLabel.setText(
            f"Current pitch: {value:+d} Hz"
        )

    def _update_volume_label(self, value: int) -> None:
        """Display the current volume level."""

        self.volumeValueLabel.setText(
            f"Current volume: {value}%"
        )

    @classmethod
    def _is_valid_voice(cls, voice: str) -> bool:
        """Return whether the selected value is a usable voice."""

        return bool(voice) and voice not in cls.INVALID_VOICE_VALUES

    @staticmethod
    def _format_percentage(value: int) -> str:
        """Format an integer as an Edge TTS percentage adjustment."""

        return f"{value:+d}%"

    @staticmethod
    def _format_pitch(value: int) -> str:
        """Format an integer as an Edge TTS pitch adjustment."""

        return f"{value:+d}Hz"