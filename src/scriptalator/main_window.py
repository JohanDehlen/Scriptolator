from pathlib import Path

from PySide6.QtCore import QSettings, QThread, QUrl, Signal
from PySide6.QtGui import QCloseEvent, QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from services.edge_tts_service import EdgeTTSService
from version import APP_NAME, APP_VERSION
from widgets.button_bar import ButtonBar
from widgets.output_panel import OutputPanel
from widgets.script_editor import ScriptEditor
from widgets.status_bar import StatusBar
from widgets.voice_panel import VoicePanel


class NarrationGenerationThread(QThread):
    """Generate narration without blocking the application interface."""

    narration_generated = Signal(str)
    generation_failed = Signal(str)

    def __init__(
        self,
        text: str,
        voice: str,
        output_path: Path,
        rate: str,
        pitch: str,
        volume: str,
    ) -> None:
        super().__init__()

        self.text = text
        self.voice = voice
        self.output_path = output_path
        self.rate = rate
        self.pitch = pitch
        self.volume = volume

    def run(self) -> None:
        """Generate the narration and report the result."""

        try:
            generated_path = EdgeTTSService.generate_mp3(
                text=self.text,
                voice=self.voice,
                output_path=self.output_path,
                rate=self.rate,
                pitch=self.pitch,
                volume=self.volume,
            )
        except Exception as error:
            self.generation_failed.emit(str(error))
        else:
            self.narration_generated.emit(str(generated_path))


class MainWindow(QMainWindow):
    """Main application window for Scriptalator."""

    ORGANIZATION_NAME = "JohanDehlen"
    PREVIOUS_APPLICATION_NAME = "Voiceanator"

    VOICE_SETTING_KEY = "narration/last_voice"
    OUTPUT_FOLDER_SETTING_KEY = "output/last_folder"
    LEGACY_OUTPUT_FILENAME_SETTING_KEY = "output/last_filename"
    SETTINGS_MIGRATED_KEY = "application/voiceanator_settings_migrated"

    def __init__(self) -> None:
        super().__init__()

        self.project_root = Path(__file__).resolve().parents[2]
        self.last_generated_path: Path | None = None
        self.generation_thread: NarrationGenerationThread | None = None

        self.settings = QSettings(
            self.ORGANIZATION_NAME,
            APP_NAME,
        )

        self._migrate_previous_settings()
        self._remove_legacy_filename_setting()

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1280, 850)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        title = QLabel(APP_NAME)
        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        subtitle = QLabel(
            "Transform scripts into professional AI narration"
        )

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        content_layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        script_group = QGroupBox("Script")
        script_layout = QVBoxLayout()

        self.scriptEditor = ScriptEditor()

        script_layout.addWidget(self.scriptEditor)
        script_group.setLayout(script_layout)

        left_layout.addWidget(script_group)

        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()

        self.outputPanel = OutputPanel()

        output_layout.addWidget(self.outputPanel)
        output_group.setLayout(output_layout)

        left_layout.addWidget(output_group)

        right_layout = QVBoxLayout()

        voice_group = QGroupBox("Voice Settings")
        voice_layout = QVBoxLayout()

        self.voicePanel = VoicePanel()

        voice_layout.addWidget(self.voicePanel)
        voice_group.setLayout(voice_layout)

        right_layout.addWidget(voice_group)
        right_layout.addStretch()

        content_layout.addLayout(left_layout, 3)
        content_layout.addLayout(right_layout, 1)

        main_layout.addLayout(content_layout)

        self.buttonBar = ButtonBar()
        main_layout.addWidget(self.buttonBar)

        self.statusBarWidget = StatusBar()
        self.statusBarWidget.setStyleSheet(
            """
            padding: 8px;
            border-top: 1px solid gray;
            """
        )

        main_layout.addWidget(self.statusBarWidget)

        self._restore_output_settings()
        self._restore_last_voice()
        self._connect_actions()

    def _migrate_previous_settings(self) -> None:
        """Copy relevant Voiceanator settings into Scriptalator once."""

        migration_complete = self.settings.value(
            self.SETTINGS_MIGRATED_KEY,
            False,
            type=bool,
        )

        if migration_complete:
            return

        previous_settings = QSettings(
            self.ORGANIZATION_NAME,
            self.PREVIOUS_APPLICATION_NAME,
        )

        setting_keys = (
            self.VOICE_SETTING_KEY,
            self.OUTPUT_FOLDER_SETTING_KEY,
        )

        for setting_key in setting_keys:
            if self.settings.contains(setting_key):
                continue

            if not previous_settings.contains(setting_key):
                continue

            self.settings.setValue(
                setting_key,
                previous_settings.value(setting_key),
            )

        self.settings.setValue(
            self.SETTINGS_MIGRATED_KEY,
            True,
        )
        self.settings.sync()

    def _remove_legacy_filename_setting(self) -> None:
        """Remove the old saved filename so each session starts blank."""

        if self.settings.contains(
            self.LEGACY_OUTPUT_FILENAME_SETTING_KEY
        ):
            self.settings.remove(
                self.LEGACY_OUTPUT_FILENAME_SETTING_KEY
            )
            self.settings.sync()

    def _restore_output_settings(self) -> None:
        """Restore the output folder and begin with a blank filename."""

        default_output_folder = self.project_root / "output"

        saved_folder = self.settings.value(
            self.OUTPUT_FOLDER_SETTING_KEY,
            str(default_output_folder),
            type=str,
        ).strip()

        output_folder = self._resolve_output_folder(
            saved_folder=saved_folder,
            default_output_folder=default_output_folder,
        )

        self.outputPanel.folder.setText(str(output_folder))
        self.outputPanel.filename.clear()

        self.settings.setValue(
            self.OUTPUT_FOLDER_SETTING_KEY,
            str(output_folder),
        )
        self.settings.sync()

    @staticmethod
    def _resolve_output_folder(
        saved_folder: str,
        default_output_folder: Path,
    ) -> Path:
        """Return the appropriate output folder after the project rename."""

        if not saved_folder:
            return default_output_folder

        saved_path = Path(saved_folder).expanduser()

        is_voiceanator_output = (
            saved_path.name.lower() == "output"
            and saved_path.parent.name.lower() == "voiceanator"
        )

        if is_voiceanator_output:
            return default_output_folder

        return saved_path

    def _restore_last_voice(self) -> None:
        """Restore the voice selected during the previous session."""

        saved_voice = self.settings.value(
            self.VOICE_SETTING_KEY,
            "",
            type=str,
        ).strip()

        if not saved_voice:
            return

        voice_index = self.voicePanel.voiceCombo.findText(
            saved_voice
        )

        if voice_index >= 0:
            self.voicePanel.voiceCombo.setCurrentIndex(
                voice_index
            )

    def _save_selected_voice(self) -> None:
        """Store the current valid voice selection."""

        voice = self.voicePanel.voiceCombo.currentText().strip()

        if not self._is_valid_voice(voice):
            return

        self.settings.setValue(
            self.VOICE_SETTING_KEY,
            voice,
        )
        self.settings.sync()

    def _save_output_folder(self) -> None:
        """Store the current output folder."""

        output_folder = self.outputPanel.folder.text().strip()

        if not output_folder:
            return

        self.settings.setValue(
            self.OUTPUT_FOLDER_SETTING_KEY,
            output_folder,
        )
        self.settings.sync()

    def _connect_actions(self) -> None:
        """Connect the essential narration controls."""

        self.outputPanel.browse.clicked.connect(
            self._select_output_folder
        )
        self.outputPanel.folder.editingFinished.connect(
            self._save_output_folder
        )

        self.buttonBar.generate.clicked.connect(
            self._generate_narration
        )
        self.buttonBar.play.clicked.connect(
            self._play_narration
        )
        self.buttonBar.open.clicked.connect(
            self._open_output_folder
        )

        self.voicePanel.voiceCombo.currentTextChanged.connect(
            self._save_selected_voice
        )

    def _select_output_folder(self) -> None:
        """Allow the user to select the narration output folder."""

        current_folder = self.outputPanel.folder.text().strip()

        selected_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            current_folder or str(self.project_root),
        )

        if selected_folder:
            self.outputPanel.folder.setText(selected_folder)
            self._save_output_folder()

    def _generate_narration(self) -> None:
        """Start MP3 generation in a background thread."""

        if (
            self.generation_thread is not None
            and self.generation_thread.isRunning()
        ):
            QMessageBox.information(
                self,
                "Narration In Progress",
                "Scriptalator is already generating narration.",
            )
            return

        script = self.scriptEditor.editor.toPlainText().strip()
        voice = self.voicePanel.voiceCombo.currentText().strip()
        output_folder = self.outputPanel.folder.text().strip()
        entered_filename = self.outputPanel.filename.text().strip()

        validation_error = self._validate_generation_inputs(
            script=script,
            voice=voice,
            output_folder=output_folder,
            filename=entered_filename,
        )

        if validation_error:
            QMessageBox.warning(
                self,
                "Cannot Generate Narration",
                validation_error,
            )
            return

        filename = self._normalize_mp3_filename(entered_filename)
        self.outputPanel.filename.setText(filename)

        output_path = Path(output_folder).expanduser() / filename

        if output_path.exists() and not self._confirm_overwrite(
            output_path
        ):
            self.statusBarWidget.setText(
                "Narration generation cancelled."
            )
            return

        rate = self._format_percentage(
            self.voicePanel.speedSlider.value()
        )
        pitch = self._format_pitch(
            self.voicePanel.pitchSlider.value()
        )
        volume = self._format_percentage(
            self.voicePanel.volumeSlider.value() - 100
        )

        self._save_selected_voice()
        self._save_output_folder()

        self.generation_thread = NarrationGenerationThread(
            text=script,
            voice=voice,
            output_path=output_path,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )

        self.generation_thread.narration_generated.connect(
            self._narration_generated
        )
        self.generation_thread.generation_failed.connect(
            self._narration_generation_failed
        )
        self.generation_thread.finished.connect(
            self._generation_finished
        )
        self.generation_thread.finished.connect(
            self.generation_thread.deleteLater
        )

        self._set_generation_controls_enabled(False)
        self.statusBarWidget.setText("Generating narration...")

        self.generation_thread.start()

    def _narration_generated(self, generated_path: str) -> None:
        """Handle successful narration generation."""

        self.last_generated_path = Path(generated_path)

        self.statusBarWidget.setText(
            f"Narration saved: {generated_path}"
        )

        QMessageBox.information(
            self,
            "Narration Complete",
            (
                "MP3 narration saved successfully:\n\n"
                f"{generated_path}"
            ),
        )

    def _narration_generation_failed(
        self,
        error_message: str,
    ) -> None:
        """Handle narration generation failure."""

        self.statusBarWidget.setText(
            "Narration generation failed."
        )

        if "Permission denied" in error_message:
            user_message = (
                "Scriptalator could not replace the output file.\n\n"
                "The MP3 may currently be open in another application. "
                "Close the audio player or choose a different filename.\n\n"
                f"Technical details:\n{error_message}"
            )
        else:
            user_message = (
                "Scriptalator could not generate the narration.\n\n"
                f"{error_message}"
            )

        QMessageBox.critical(
            self,
            "Narration Generation Failed",
            user_message,
        )

    def _generation_finished(self) -> None:
        """Restore controls after background generation finishes."""

        self._set_generation_controls_enabled(True)
        self.generation_thread = None

    def _set_generation_controls_enabled(
        self,
        enabled: bool,
    ) -> None:
        """Enable or disable controls that affect generation."""

        self.buttonBar.generate.setEnabled(enabled)
        self.outputPanel.folder.setEnabled(enabled)
        self.outputPanel.filename.setEnabled(enabled)
        self.outputPanel.browse.setEnabled(enabled)
        self.voicePanel.languageFilter.setEnabled(enabled)
        self.voicePanel.voiceCombo.setEnabled(enabled)
        self.voicePanel.speedSlider.setEnabled(enabled)
        self.voicePanel.pitchSlider.setEnabled(enabled)
        self.voicePanel.volumeSlider.setEnabled(enabled)
        self.voicePanel.previewButton.setEnabled(enabled)

    def _confirm_overwrite(self, output_path: Path) -> bool:
        """Ask the user before replacing an existing narration file."""

        response = QMessageBox.question(
            self,
            "Replace Existing File?",
            (
                "The output file already exists:\n\n"
                f"{output_path}\n\n"
                "Do you want to replace it?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        return response == QMessageBox.StandardButton.Yes

    def _play_narration(self) -> None:
        """Open the current narration MP3 in the default audio player."""

        narration_path = self._get_current_output_path()

        if not narration_path.is_file():
            QMessageBox.warning(
                self,
                "Narration Not Found",
                (
                    "Generate the narration before trying to play it.\n\n"
                    f"Expected file:\n{narration_path}"
                ),
            )
            return

        opened = QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(narration_path.resolve()))
        )

        if not opened:
            QMessageBox.critical(
                self,
                "Unable to Play Narration",
                (
                    "Windows could not open the MP3 file in the "
                    "default audio player."
                ),
            )
            return

        self.statusBarWidget.setText(
            f"Playing narration: {narration_path}"
        )

    def _open_output_folder(self) -> None:
        """Open the selected narration output folder."""

        folder_text = self.outputPanel.folder.text().strip()

        if not folder_text:
            QMessageBox.warning(
                self,
                "Output Folder Missing",
                "Select an output folder first.",
            )
            return

        output_folder = Path(folder_text).expanduser()

        try:
            output_folder.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            QMessageBox.critical(
                self,
                "Unable to Open Folder",
                str(error),
            )
            return

        self._save_output_folder()

        opened = QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(output_folder.resolve()))
        )

        if not opened:
            QMessageBox.critical(
                self,
                "Unable to Open Folder",
                "Windows could not open the output folder.",
            )
            return

        self.statusBarWidget.setText(
            f"Opened output folder: {output_folder}"
        )

    def _get_current_output_path(self) -> Path:
        """Return the output path currently shown in the interface."""

        if self.last_generated_path is not None:
            return self.last_generated_path

        output_folder = self.outputPanel.folder.text().strip()
        entered_filename = self.outputPanel.filename.text().strip()

        if not entered_filename:
            return Path(output_folder).expanduser()

        filename = self._normalize_mp3_filename(entered_filename)

        return Path(output_folder).expanduser() / filename

    def closeEvent(self, event: QCloseEvent) -> None:
        """Prevent closing while narration or preview generation runs."""

        if (
            self.generation_thread is not None
            and self.generation_thread.isRunning()
        ):
            QMessageBox.warning(
                self,
                "Narration In Progress",
                (
                    "Scriptalator is still generating narration.\n\n"
                    "Wait for generation to finish before closing."
                ),
            )
            event.ignore()
            return

        preview_thread = self.voicePanel.preview_thread

        if (
            preview_thread is not None
            and preview_thread.isRunning()
        ):
            QMessageBox.warning(
                self,
                "Preview In Progress",
                (
                    "Scriptalator is still generating a voice preview.\n\n"
                    "Wait for the preview to finish before closing."
                ),
            )
            event.ignore()
            return

        event.accept()

    @staticmethod
    def _normalize_mp3_filename(filename: str) -> str:
        """Add the MP3 extension when the entered filename lacks it."""

        normalized_filename = filename.strip()

        if normalized_filename.lower().endswith(".mp3"):
            return normalized_filename

        return f"{normalized_filename}.mp3"

    @staticmethod
    def _is_valid_voice(voice: str) -> bool:
        """Return whether a voice value represents a usable voice."""

        return bool(voice) and voice not in {
            "Loading voices...",
            "No voices found",
            "Unable to load voices",
        }

    @classmethod
    def _validate_generation_inputs(
        cls,
        script: str,
        voice: str,
        output_folder: str,
        filename: str,
    ) -> str | None:
        """Return a user-facing validation message when input is invalid."""

        if not script:
            return (
                "Enter or paste narration text before generating audio."
            )

        if not cls._is_valid_voice(voice):
            return "Select a valid Microsoft Edge voice."

        if not output_folder:
            return "Select an output folder."

        if not filename:
            return "Enter an output filename."

        return None

    @staticmethod
    def _format_percentage(value: int) -> str:
        """Format an integer as an Edge TTS percentage adjustment."""

        return f"{value:+d}%"

    @staticmethod
    def _format_pitch(value: int) -> str:
        """Format an integer as an Edge TTS pitch adjustment."""

        return f"{value:+d}Hz"