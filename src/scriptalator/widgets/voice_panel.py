from pathlib import Path
from tempfile import gettempdir
from typing import Callable
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
from services.settings_service import SettingsService


class VoiceComboBox(QComboBox):
    """Display friendly voice labels while exposing Microsoft voice IDs."""

    def currentText(self) -> str:
        """Return the current Microsoft voice ID."""

        voice_id = self.currentData()

        if isinstance(voice_id, str) and voice_id:
            return voice_id

        return super().currentText()

    def findText(
        self,
        text: str,
        flags: Qt.MatchFlag = Qt.MatchFlag.MatchExactly
        | Qt.MatchFlag.MatchCaseSensitive,
    ) -> int:
        """Find either a Microsoft voice ID or a visible label."""

        for index in range(self.count()):
            if self.itemData(index) == text:
                return index

        return super().findText(text, flags)


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
        preview_text: str,
        voice: str,
        output_path: Path,
        rate: str,
        pitch: str,
        volume: str,
    ) -> None:
        super().__init__()

        self.preview_text = preview_text
        self.voice = voice
        self.output_path = output_path
        self.rate = rate
        self.pitch = pitch
        self.volume = volume

    def run(self) -> None:
        """Generate the preview MP3 and report the result."""

        try:
            generated_path = EdgeTTSService.generate_mp3(
                text=self.preview_text,
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

    REGION_NAMES = {
        "AE": "United Arab Emirates",
        "AR": "Argentina",
        "AT": "Austria",
        "AU": "Australia",
        "BE": "Belgium",
        "BO": "Bolivia",
        "BR": "Brazil",
        "CA": "Canada",
        "CH": "Switzerland",
        "CL": "Chile",
        "CN": "China",
        "CO": "Colombia",
        "CR": "Costa Rica",
        "CU": "Cuba",
        "CZ": "Czech Republic",
        "DE": "Germany",
        "DK": "Denmark",
        "DO": "Dominican Republic",
        "DZ": "Algeria",
        "EC": "Ecuador",
        "EG": "Egypt",
        "ES": "Spain",
        "FI": "Finland",
        "FR": "France",
        "GB": "United Kingdom",
        "GR": "Greece",
        "GT": "Guatemala",
        "HK": "Hong Kong",
        "HN": "Honduras",
        "IE": "Ireland",
        "IL": "Israel",
        "IN": "India",
        "IQ": "Iraq",
        "IT": "Italy",
        "JO": "Jordan",
        "JP": "Japan",
        "KE": "Kenya",
        "KR": "South Korea",
        "KW": "Kuwait",
        "LB": "Lebanon",
        "LY": "Libya",
        "MA": "Morocco",
        "MX": "Mexico",
        "MY": "Malaysia",
        "NG": "Nigeria",
        "NI": "Nicaragua",
        "NL": "Netherlands",
        "NO": "Norway",
        "NZ": "New Zealand",
        "OM": "Oman",
        "PA": "Panama",
        "PE": "Peru",
        "PH": "Philippines",
        "PK": "Pakistan",
        "PL": "Poland",
        "PR": "Puerto Rico",
        "PT": "Portugal",
        "PY": "Paraguay",
        "QA": "Qatar",
        "RO": "Romania",
        "RU": "Russia",
        "SA": "Saudi Arabia",
        "SE": "Sweden",
        "SG": "Singapore",
        "SY": "Syria",
        "TH": "Thailand",
        "TN": "Tunisia",
        "TR": "Turkey",
        "TW": "Taiwan",
        "TZ": "Tanzania",
        "UA": "Ukraine",
        "US": "United States",
        "UY": "Uruguay",
        "VE": "Venezuela",
        "VN": "Vietnam",
        "YE": "Yemen",
        "ZA": "South Africa",
    }

    ENGLISH_LOCALE_NAMES = {
        "en-US": "English (US)",
        "en-GB": "English (UK)",
        "en-AU": "English (Australia)",
        "en-CA": "English (Canada)",
        "en-IN": "English (India)",
        "en-IE": "English (Ireland)",
        "en-NZ": "English (New Zealand)",
        "en-ZA": "English (South Africa)",
        "en-SG": "English (Singapore)",
        "en-HK": "English (Hong Kong)",
        "en-KE": "English (Kenya)",
        "en-NG": "English (Nigeria)",
        "en-PH": "English (Philippines)",
        "en-TZ": "English (Tanzania)",
    }

    PREFERRED_ENGLISH_LOCALES = (
        "en-US",
        "en-GB",
        "en-AU",
        "en-CA",
        "en-IN",
        "en-IE",
        "en-NZ",
        "en-ZA",
        "en-SG",
        "en-HK",
        "en-KE",
        "en-NG",
        "en-PH",
        "en-TZ",
    )

    CHINESE_LOCALE_NAMES = {
        "zh-CN": "Chinese (Simplified)",
        "zh-HK": "Chinese (Hong Kong)",
        "zh-TW": "Chinese (Traditional)",
    }

    FAVORITES_FILTER_VALUE = "__favorites__"

    INVALID_VOICE_VALUES = {
        "Loading voices...",
        "No voices found",
        "Unable to load voices",
    }

    def __init__(self) -> None:
        super().__init__()

        self.all_voices: list[dict[str, str]] = []
        self.settings_service = SettingsService(
            Path(__file__).resolve().parents[3]
        )
        self.favorite_voices = set(
            self.settings_service.get_favorite_voices()
        )
        self.preview_text_provider: Callable[[], str] | None = None
        self.preview_thread: VoicePreviewThread | None = None
        self.last_preview_path: Path | None = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Narration Language"))

        self.languageFilter = QComboBox()
        self.languageFilter.addItem("Loading languages...")
        self.languageFilter.setEnabled(False)

        layout.addWidget(self.languageFilter)

        layout.addWidget(QLabel("Narration Voice"))

        voice_selection_layout = QHBoxLayout()

        self.favoriteButton = QPushButton("☆")
        self.favoriteButton.setToolTip(
            "Add the selected voice to Favorites"
        )
        self.favoriteButton.setFixedWidth(38)
        self.favoriteButton.setEnabled(False)

        self.voiceCombo = VoiceComboBox()
        self.voiceCombo.addItem("Loading voices...")
        self.voiceCombo.setEnabled(False)

        voice_selection_layout.addWidget(self.favoriteButton)
        voice_selection_layout.addWidget(self.voiceCombo, 1)

        layout.addLayout(voice_selection_layout)

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

        self.previewButton = QPushButton("Preview")
        layout.addWidget(self.previewButton)

        layout.addStretch()

        self.languageFilter.currentIndexChanged.connect(
            self._apply_language_filter
        )
        self.voiceCombo.currentIndexChanged.connect(
            self._update_favorite_button
        )
        self.favoriteButton.clicked.connect(
            self._toggle_current_favorite
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

    def set_preview_text_provider(
        self,
        provider: Callable[[], str],
    ) -> None:
        """Set the function used to obtain narration preview text."""

        self.preview_text_provider = provider

    def _get_preview_text(self) -> str:
        """Return script-based preview text or a safe fallback."""

        default_text = (
            "In the beginning, God created the heavens and the earth."
        )

        if self.preview_text_provider is None:
            return default_text

        provided_text = self.preview_text_provider().strip()

        if not provided_text:
            return default_text

        words = provided_text.split()

        return " ".join(words[:25])

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
            self.all_voices = EdgeTTSService.get_voice_details()
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
        """Populate the dropdown with friendly locale names."""

        locales = {
            voice["locale"]
            for voice in self.all_voices
            if voice["locale"]
        }

        language_entries = sorted(
            (
                self._language_sort_key(locale),
                self._friendly_locale_name(locale),
                locale,
            )
            for locale in locales
        )

        self.languageFilter.blockSignals(True)
        self.languageFilter.clear()
        self.languageFilter.addItem(
            "All Languages",
            "",
        )
        self.languageFilter.addItem(
            "★ Favorites",
            self.FAVORITES_FILTER_VALUE,
        )

        for _, language_name, locale in language_entries:
            self.languageFilter.addItem(
                language_name,
                locale,
            )

        self.languageFilter.setCurrentIndex(0)
        self.languageFilter.setEnabled(True)
        self.languageFilter.blockSignals(False)

    def _apply_language_filter(self, _: int = -1) -> None:
        """Show voices belonging to the selected locale."""

        current_voice_id = self.voiceCombo.currentText().strip()
        selected_locale = (
            self.languageFilter.currentData() or ""
        )

        if selected_locale == self.FAVORITES_FILTER_VALUE:
            matching_voices = [
                voice
                for voice in self.all_voices
                if voice["short_name"] in self.favorite_voices
            ]
        elif selected_locale:
            matching_voices = [
                voice
                for voice in self.all_voices
                if voice["locale"] == selected_locale
            ]
        else:
            matching_voices = self.all_voices.copy()

        matching_voices.sort(
            key=lambda voice: (
                self._voice_display_name(voice).lower(),
                voice["short_name"].lower(),
            )
        )

        self.voiceCombo.blockSignals(True)
        self.voiceCombo.clear()

        if not matching_voices:
            self.voiceCombo.addItem("No voices found")
            self.voiceCombo.setEnabled(False)
            self.favoriteButton.setEnabled(False)
            self.voiceCombo.blockSignals(False)
            self._update_favorite_button()
            return

        for voice in matching_voices:
            display_name = self._voice_display_name(voice)

            if voice["short_name"] in self.favorite_voices:
                display_name = f"★ {display_name}"

            self.voiceCombo.addItem(
                display_name,
                voice["short_name"],
            )

        self.voiceCombo.setEnabled(True)
        self.favoriteButton.setEnabled(True)

        current_index = self.voiceCombo.findText(current_voice_id)

        if current_index >= 0:
            self.voiceCombo.setCurrentIndex(current_index)

        self.voiceCombo.blockSignals(False)
        self._update_favorite_button()

    def _toggle_current_favorite(self) -> None:
        """Add or remove the selected voice from Favorites."""

        voice_id = self.voiceCombo.currentText().strip()

        if not self._is_valid_voice(voice_id):
            return

        is_favorite = self.settings_service.toggle_favorite_voice(
            voice_id
        )

        if is_favorite:
            self.favorite_voices.add(voice_id)
        else:
            self.favorite_voices.discard(voice_id)

        self._apply_language_filter()
        restored_index = self.voiceCombo.findText(voice_id)

        if restored_index >= 0:
            self.voiceCombo.setCurrentIndex(restored_index)

        self._update_favorite_button()

    def _update_favorite_button(self, _: int = -1) -> None:
        """Reflect the selected voice's favorite state."""

        voice_id = self.voiceCombo.currentText().strip()
        is_valid = self._is_valid_voice(voice_id)

        self.favoriteButton.setEnabled(is_valid)

        if is_valid and voice_id in self.favorite_voices:
            self.favoriteButton.setText("★")
            self.favoriteButton.setToolTip(
                "Remove the selected voice from Favorites"
            )
            return

        self.favoriteButton.setText("☆")
        self.favoriteButton.setToolTip(
            "Add the selected voice to Favorites"
        )

    @classmethod
    def _language_sort_key(
        cls,
        locale: str,
    ) -> tuple[int, int, str]:
        """Place English variants first, then other languages alphabetically."""

        if locale in cls.PREFERRED_ENGLISH_LOCALES:
            return (
                0,
                cls.PREFERRED_ENGLISH_LOCALES.index(locale),
                "",
            )

        return (
            1,
            0,
            cls._friendly_locale_name(locale).lower(),
        )

    @classmethod
    def _friendly_locale_name(cls, locale: str) -> str:
        """Convert a Microsoft locale code into a readable name."""

        if locale in cls.ENGLISH_LOCALE_NAMES:
            return cls.ENGLISH_LOCALE_NAMES[locale]

        if locale in cls.CHINESE_LOCALE_NAMES:
            return cls.CHINESE_LOCALE_NAMES[locale]

        language_code, separator, region_code = locale.partition("-")

        language_name = cls.LANGUAGE_NAMES.get(
            language_code.lower(),
            language_code.upper(),
        )

        if not separator:
            return language_name

        region_name = cls.REGION_NAMES.get(
            region_code.upper(),
            region_code.upper(),
        )

        return f"{language_name} ({region_name})"

    @staticmethod
    def _simple_voice_name(short_name: str) -> str:
        """Extract the speaker name from a Microsoft voice ID."""

        name = short_name.rsplit("-", 1)[-1]

        if name.lower().endswith("neural"):
            name = name[:-6]

        return name or short_name

    @classmethod
    def _voice_display_name(
        cls,
        voice: dict[str, str],
    ) -> str:
        """Return the friendly label shown in the voice dropdown."""

        speaker_name = cls._simple_voice_name(
            voice["short_name"]
        )
        gender = voice["gender"].strip() or "Unknown"

        return f"{speaker_name} — {gender}"

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
            preview_text=self._get_preview_text(),
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
        self.previewButton.setText("Generating...")

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
        self.previewButton.setText("Preview")
        self.preview_thread = None

    def _set_preview_controls_enabled(
        self,
        enabled: bool,
    ) -> None:
        """Enable or disable controls used by voice preview."""

        self.languageFilter.setEnabled(enabled)
        self.voiceCombo.setEnabled(enabled)
        self.favoriteButton.setEnabled(
            enabled and self._is_valid_voice(
                self.voiceCombo.currentText().strip()
            )
        )
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