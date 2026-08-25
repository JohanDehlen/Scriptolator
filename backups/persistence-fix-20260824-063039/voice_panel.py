from __future__ import annotations

from pathlib import Path
from tempfile import gettempdir
from typing import Any, Callable
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

from services.application_paths import ApplicationPaths
from services.azure_settings_service import AzureSettingsService
from services.settings_service import SettingsService
from services.speech_engine_manager import SpeechEngineManager
from widgets.azure_settings_dialog import AzureSettingsDialog
from widgets.profile_controls import ProfileControls
from widgets.speech_engine_selector import SpeechEngineSelector


class VoiceComboBox(QComboBox):
    """Display friendly labels while exposing Microsoft voice IDs."""

    def currentText(self) -> str:
        """Return the current Microsoft voice ID."""

        voice_id = self.currentData()

        if isinstance(voice_id, str) and voice_id:
            return voice_id

        return super().currentText()

    def findText(
        self,
        text: str,
        flags: Qt.MatchFlag = (
            Qt.MatchFlag.MatchExactly
            | Qt.MatchFlag.MatchCaseSensitive
        ),
    ) -> int:
        """Find either a Microsoft voice ID or visible label."""

        for index in range(self.count()):
            if self.itemData(index) == text:
                return index

        return super().findText(text, flags)


class ResettableSlider(QSlider):
    """Slider that resets to its default when double-clicked."""

    def __init__(
        self,
        orientation: Qt.Orientation,
        default_value: int,
    ) -> None:
        super().__init__(orientation)
        self.default_value = default_value

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Reset the slider to its configured default."""

        self.setValue(self.default_value)
        event.accept()


class VoiceLoadingThread(QThread):
    """Load voices from the active engine without blocking Qt."""

    voices_loaded = Signal(object)
    loading_failed = Signal(str)

    def __init__(
        self,
        engine: Any,
        engine_id: str,
    ) -> None:
        super().__init__()
        self.engine = engine
        self.engine_id = engine_id

    def run(self) -> None:
        """Retrieve normalized voice metadata."""

        try:
            voices = self.engine.get_voice_details()
        except Exception as error:
            self.loading_failed.emit(str(error))
        else:
            self.voices_loaded.emit(
                {
                    "engine_id": self.engine_id,
                    "voices": voices,
                }
            )


class VoicePreviewThread(QThread):
    """Generate a voice preview without blocking Qt."""

    preview_generated = Signal(str)
    preview_failed = Signal(str)

    def __init__(
        self,
        engine: Any,
        preview_text: str,
        voice: str,
        output_path: Path,
        rate: str,
        pitch: str,
        volume: str,
    ) -> None:
        super().__init__()

        self.engine = engine
        self.preview_text = preview_text
        self.voice = voice
        self.output_path = output_path
        self.rate = rate
        self.pitch = pitch
        self.volume = volume

    def run(self) -> None:
        """Generate the preview MP3 and report the result."""

        try:
            generated_path = self.engine.generate_mp3(
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
    """Select, filter, favourite, and preview narration voices."""

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

    PREFERRED_ENGLISH_LOCALES = tuple(
        ENGLISH_LOCALE_NAMES
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

        self.application_paths = ApplicationPaths.create()
        self.settings_service = SettingsService(
            self.application_paths
        )
        self.azure_settings_service = AzureSettingsService(
            self.application_paths
        )
        self.engine_manager = SpeechEngineManager()

        self.all_voices: list[dict[str, str]] = []
        self.favorite_voices = set(
            self.settings_service.get_favorite_voices()
        )
        self.preview_text_provider: Callable[[], str] | None = None
        self._pending_profile_selection: (
            tuple[str, str] | None
        ) = None
        self.voice_loading_thread: VoiceLoadingThread | None = None
        self.preview_thread: VoicePreviewThread | None = None
        self.last_preview_path: Path | None = None

        layout = QVBoxLayout(self)

        self.profileControls = ProfileControls()
        layout.addWidget(self.profileControls)

        self.engineSelector = SpeechEngineSelector(
            engine_manager=self.engine_manager,
            settings_service=self.azure_settings_service,
        )
        layout.addWidget(self.engineSelector)

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

        self.engineSelector.engine_changed.connect(
            self._engine_changed
        )
        self.engineSelector.azure_settings_requested.connect(
            self._show_azure_settings_dialog
        )
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

    @property
    def current_engine_id(self) -> str:
        """Return the active speech-engine identifier."""

        return self.engine_manager.current_engine_id

    def set_preview_text_provider(
        self,
        provider: Callable[[], str],
    ) -> None:
        """Set the function used to obtain preview text."""

        self.preview_text_provider = provider

    def apply_profile_selection(
        self,
        engine_id: str,
        language: str,
        voice: str,
    ) -> None:
        """Switch engine and restore a profile voice when ready."""

        self._pending_profile_selection = (
            language,
            voice,
        )

        if engine_id != self.current_engine_id:
            selected = self.engineSelector.set_engine(engine_id)

            if not selected:
                self._pending_profile_selection = None
                raise ValueError(
                    "The profile speech engine could not be selected."
                )

            return

        if self.all_voices:
            self._apply_pending_profile_selection()
            return

        self.load_voices()

    def _apply_pending_profile_selection(self) -> None:
        """Apply a deferred profile language and voice."""

        if self._pending_profile_selection is None:
            return

        language, voice = self._pending_profile_selection
        self._pending_profile_selection = None

        language_index = self.languageFilter.findData(language)

        if language_index < 0:
            language_index = 0

        self.languageFilter.setCurrentIndex(language_index)

        voice_index = self.voiceCombo.findText(voice)

        if voice_index < 0:
            raise ValueError(
                "The profile voice is not available for its "
                "saved speech engine."
            )

        self.voiceCombo.setCurrentIndex(voice_index)

    def _show_azure_settings_dialog(self) -> None:
        """Open Azure settings and refresh the selector."""

        dialog = AzureSettingsDialog(
            settings_service=self.azure_settings_service,
            parent=self,
        )
        dialog.exec()
        self.engineSelector.refresh_after_azure_settings()

    def _engine_changed(self, _: str) -> None:
        """Reload voices after the speech engine changes."""

        self.load_voices()

    def load_voices(self) -> None:
        """Load voices from the active speech engine."""

        if (
            self.voice_loading_thread is not None
            and self.voice_loading_thread.isRunning()
        ):
            return

        self.all_voices = []
        self._set_voice_loading_state(True)

        engine_id = self.engine_manager.current_engine_id
        engine = self.engine_manager.current_engine

        self.voice_loading_thread = VoiceLoadingThread(
            engine=engine,
            engine_id=engine_id,
        )
        self.voice_loading_thread.voices_loaded.connect(
            self._voices_loaded
        )
        self.voice_loading_thread.loading_failed.connect(
            self._voice_loading_failed
        )
        self.voice_loading_thread.finished.connect(
            self._voice_loading_finished
        )
        self.voice_loading_thread.start()

    def _voices_loaded(self, payload: object) -> None:
        """Populate controls after successful voice retrieval."""

        if not isinstance(payload, dict):
            self._voice_loading_failed(
                "The speech engine returned invalid voice data."
            )
            return

        engine_id = str(payload.get("engine_id", ""))
        voices = payload.get("voices")

        if engine_id != self.engine_manager.current_engine_id:
            return

        if not isinstance(voices, list):
            self._voice_loading_failed(
                "The speech engine returned invalid voice data."
            )
            return

        self.all_voices = [
            voice
            for voice in voices
            if isinstance(voice, dict)
            and str(voice.get("short_name", "")).strip()
        ]

        if not self.all_voices:
            self._voice_loading_failed(
                "The selected speech engine returned no voices."
            )
            return

        self._populate_languages()
        self._apply_language_filter()

        if self._pending_profile_selection is not None:
            try:
                self._apply_pending_profile_selection()
            except ValueError as error:
                QMessageBox.warning(
                    self,
                    "Unable to Restore Profile Voice",
                    str(error),
                )
        else:
            self._restore_saved_voice_selection()

    def _restore_saved_voice_selection(self) -> None:
        """Restore the saved language and voice after loading."""

        saved_language = self.settings_service.get_language()
        saved_voice = self.settings_service.get_voice()

        language_index = self.languageFilter.findData(
            saved_language
        )

        if language_index < 0:
            language_index = 0

        self.languageFilter.setCurrentIndex(language_index)

        voice_index = self.voiceCombo.findText(saved_voice)

        if voice_index >= 0:
            self.voiceCombo.setCurrentIndex(voice_index)

    def _voice_loading_failed(self, error_text: str) -> None:
        """Display a voice-loading error."""

        self.all_voices = []
        self._pending_profile_selection = None

        self.languageFilter.clear()
        self.languageFilter.addItem("Languages unavailable")
        self.languageFilter.setEnabled(False)

        self.voiceCombo.clear()
        self.voiceCombo.addItem("Unable to load voices")
        self.voiceCombo.setEnabled(False)

        self.favoriteButton.setEnabled(False)
        self.previewButton.setEnabled(False)

        QMessageBox.critical(
            self,
            "Voice Loading Error",
            (
                f"{self.engine_manager.current_engine_name} voices "
                "could not be loaded.\n\n"
                f"{error_text}"
            ),
        )

    def _voice_loading_finished(self) -> None:
        """Release the completed voice-loading worker."""

        worker = self.voice_loading_thread
        self.voice_loading_thread = None

        if worker is not None:
            worker.deleteLater()

        self.engineSelector.setEnabled(True)

        if self.all_voices:
            self.previewButton.setEnabled(True)

    def _set_voice_loading_state(self, loading: bool) -> None:
        """Show or clear the voice-loading state."""

        self.engineSelector.setEnabled(not loading)
        self.languageFilter.clear()
        self.languageFilter.addItem("Loading languages...")
        self.languageFilter.setEnabled(False)
        self.voiceCombo.clear()
        self.voiceCombo.addItem("Loading voices...")
        self.voiceCombo.setEnabled(False)
        self.favoriteButton.setEnabled(False)
        self.previewButton.setEnabled(False)

    def _populate_languages(self) -> None:
        """Populate the dropdown with friendly locale names."""

        locales = {
            str(voice.get("locale", "")).strip()
            for voice in self.all_voices
            if str(voice.get("locale", "")).strip()
        }

        entries = sorted(
            (
                self._language_sort_key(locale),
                self._friendly_locale_name(locale),
                locale,
            )
            for locale in locales
        )

        self.languageFilter.blockSignals(True)
        self.languageFilter.clear()
        self.languageFilter.addItem("All Languages", "")
        self.languageFilter.addItem(
            "★ Favorites",
            self.FAVORITES_FILTER_VALUE,
        )

        for _, name, locale in entries:
            self.languageFilter.addItem(name, locale)

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
            matching = [
                voice
                for voice in self.all_voices
                if voice["short_name"] in self.favorite_voices
            ]
        elif selected_locale:
            matching = [
                voice
                for voice in self.all_voices
                if voice.get("locale") == selected_locale
            ]
        else:
            matching = self.all_voices.copy()

        matching.sort(
            key=lambda voice: (
                self._voice_display_name(voice).lower(),
                voice["short_name"].lower(),
            )
        )

        self.voiceCombo.blockSignals(True)
        self.voiceCombo.clear()

        if not matching:
            self.voiceCombo.addItem("No voices found")
            self.voiceCombo.setEnabled(False)
            self.favoriteButton.setEnabled(False)
            self.voiceCombo.blockSignals(False)
            self._update_favorite_button()
            return

        for voice in matching:
            display_name = self._voice_display_name(voice)

            if voice["short_name"] in self.favorite_voices:
                display_name = f"★ {display_name}"

            self.voiceCombo.addItem(
                display_name,
                voice["short_name"],
            )

        self.voiceCombo.setEnabled(True)

        current_index = self.voiceCombo.findText(
            current_voice_id
        )

        if current_index >= 0:
            self.voiceCombo.setCurrentIndex(current_index)

        self.voiceCombo.blockSignals(False)
        self._update_favorite_button()

    def _toggle_current_favorite(self) -> None:
        """Add or remove the selected voice from Favorites."""

        voice_id = self.voiceCombo.currentText().strip()

        if not self._is_valid_voice(voice_id):
            return

        is_favorite = (
            self.settings_service.toggle_favorite_voice(voice_id)
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

    def _preview_voice(self) -> None:
        """Generate and play a preview using the active engine."""

        if (
            self.preview_thread is not None
            and self.preview_thread.isRunning()
        ):
            QMessageBox.information(
                self,
                "Preview In Progress",
                "Scriptolator is already generating a voice preview.",
            )
            return

        voice = self.voiceCombo.currentText().strip()

        if not self._is_valid_voice(voice):
            QMessageBox.warning(
                self,
                "Voice Not Available",
                "Select a valid narration voice first.",
            )
            return

        preview_path = (
            Path(gettempdir())
            / f"scriptolator-preview-{uuid4().hex}.mp3"
        )

        self.preview_thread = VoicePreviewThread(
            engine=self.engine_manager.current_engine,
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

        self._set_preview_controls_enabled(False)
        self.previewButton.setText("Generating...")
        self.preview_thread.start()

    def _preview_generated(self, preview_path: str) -> None:
        """Open the generated preview in the default player."""

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
                "Scriptolator could not generate the voice preview."
                "\n\n"
                f"{error_message}"
            ),
        )

    def _preview_finished(self) -> None:
        """Restore controls after preview generation."""

        worker = self.preview_thread
        self.preview_thread = None

        self._set_preview_controls_enabled(True)
        self.previewButton.setText("Preview")

        if worker is not None:
            worker.deleteLater()

    def _set_preview_controls_enabled(
        self,
        enabled: bool,
    ) -> None:
        """Enable or disable controls used by preview."""

        self.engineSelector.setEnabled(enabled)
        self.languageFilter.setEnabled(enabled)
        self.voiceCombo.setEnabled(enabled)
        self.favoriteButton.setEnabled(
            enabled
            and self._is_valid_voice(
                self.voiceCombo.currentText().strip()
            )
        )
        self.speedSlider.setEnabled(enabled)
        self.pitchSlider.setEnabled(enabled)
        self.volumeSlider.setEnabled(enabled)
        self.previewButton.setEnabled(enabled)

    def _get_preview_text(self) -> str:
        """Return script-based preview text or a fallback."""

        default_text = (
            "In the beginning, God created the heavens and the earth."
        )

        if self.preview_text_provider is None:
            return default_text

        provided_text = self.preview_text_provider().strip()

        if not provided_text:
            return default_text

        return " ".join(provided_text.split()[:25])

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

    @classmethod
    def _language_sort_key(
        cls,
        locale: str,
    ) -> tuple[int, int, str]:
        """Place English variants first."""

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
        """Convert a Microsoft locale code to a readable name."""

        if locale in cls.ENGLISH_LOCALE_NAMES:
            return cls.ENGLISH_LOCALE_NAMES[locale]

        if locale in cls.CHINESE_LOCALE_NAMES:
            return cls.CHINESE_LOCALE_NAMES[locale]

        language_code, separator, region_code = (
            locale.partition("-")
        )
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
        """Extract a speaker name from a Microsoft voice ID."""

        name = short_name.rsplit("-", 1)[-1]

        if name.lower().endswith("neural"):
            name = name[:-6]

        return name or short_name

    def _voice_display_name(
        self,
        voice: dict[str, str],
    ) -> str:
        """Return a concise friendly voice dropdown label."""

        friendly_name = str(
            voice.get("friendly_name", "")
        ).strip()

        if (
            self.current_engine_id
            == SpeechEngineManager.EDGE_ENGINE_ID
        ):
            speaker_name = self._clean_edge_voice_name(
                friendly_name
            )
        else:
            speaker_name = friendly_name

        if not speaker_name:
            speaker_name = self._simple_voice_name(
                voice["short_name"]
            )

        gender = str(
            voice.get("gender", "")
        ).strip() or "Unknown"

        return f"{speaker_name} — {gender}"

    @staticmethod
    def _clean_edge_voice_name(
        friendly_name: str,
    ) -> str:
        """Remove redundant Microsoft and locale text."""

        cleaned_name = friendly_name.strip()

        if cleaned_name.startswith("Microsoft "):
            cleaned_name = cleaned_name[len("Microsoft "):]

        for suffix in (
            " Online (Natural)",
            " Online",
        ):
            suffix_index = cleaned_name.find(suffix)

            if suffix_index >= 0:
                cleaned_name = cleaned_name[:suffix_index]
                break

        if " - " in cleaned_name:
            cleaned_name = cleaned_name.split(" - ", 1)[0]

        return cleaned_name.strip()

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
        """Return whether the selected value is usable."""

        return bool(voice) and voice not in cls.INVALID_VOICE_VALUES

    @staticmethod
    def _format_percentage(value: int) -> str:
        """Format an integer as a TTS percentage adjustment."""

        return f"{value:+d}%"

    @staticmethod
    def _format_pitch(value: int) -> str:
        """Format an integer as a TTS pitch adjustment."""

        return f"{value:+d}Hz"