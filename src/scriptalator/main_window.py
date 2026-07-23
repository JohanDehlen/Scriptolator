import sys
from pathlib import Path

from PySide6.QtCore import QThread, QTimer, QUrl, Signal
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QDesktopServices,
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from services.edge_tts_service import EdgeTTSService
from services.profile_service import ProfileService
from services.project_service import ProjectService
from services.logging_service import LoggingService
from services.recovery_service import RecoveryService
from services.settings_service import SettingsService
from version import APP_NAME, APP_VERSION
from widgets.about_dialog import AboutDialog
from widgets.button_bar import ButtonBar
from widgets.output_panel import OutputPanel
from widgets.preferences_dialog import (
    GeneralPreferences,
    PreferencesDialog,
)
from widgets.script_editor import ScriptEditor
from widgets.script_statistics import ScriptStatistics
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


def _application_root() -> Path:
    """Return the writable root used by source and executable builds."""

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


class MainWindow(QMainWindow):
    """Main application window for Scriptolator."""

    def __init__(self) -> None:
        super().__init__()

        self.project_root = _application_root()
        self.current_project_path: Path | None = None
        self.last_generated_path: Path | None = None
        self.generation_thread: NarrationGenerationThread | None = None

        self.settings_service = SettingsService(
            self.project_root
        )
        self.profile_service = ProfileService(
            self.project_root
        )
        self.recovery_service = RecoveryService(
            self.project_root
        )
        self.logging_service = LoggingService(
            self.project_root
        )
        self.logging_service.info(
            f"{APP_NAME} {APP_VERSION} started."
        )

        self._recovery_enabled = False
        self._recovery_timer = QTimer(self)
        self._recovery_timer.setSingleShot(True)
        self._recovery_timer.setInterval(2000)
        self._recovery_timer.timeout.connect(
            self._save_recovery_snapshot
        )

        self._applying_profile = False
        self._loaded_profile_data: dict[str, object] | None = None

        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
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
        self.scriptStatistics = ScriptStatistics()

        script_layout.addWidget(self.scriptEditor)
        script_layout.addWidget(self.scriptStatistics)
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

        self._create_menus()
        self._restore_application_settings()
        self._initialize_profiles()
        self.voicePanel.set_preview_text_provider(
            self._get_preview_text
        )
        self._connect_actions()
        self._create_shortcuts()
        self._update_script_statistics()
        self._update_window_title()
        self._restore_window_state()
        self._handle_startup_recovery()
        self._recovery_enabled = True
        self._schedule_recovery_save()

        self.scriptEditor.editor.setFocus()

    def _handle_startup_recovery(self) -> None:
        """Offer to restore work left by an unclean shutdown."""

        if not self.recovery_service.has_recovery():
            return

        message_box = QMessageBox(self)
        message_box.setIcon(
            QMessageBox.Icon.Warning
        )
        message_box.setWindowTitle(
            "Unsaved Recovery Found"
        )
        message_box.setText(
            "Scriptolator found work that was not closed normally."
        )
        message_box.setInformativeText(
            "Restore the recovered project or discard it?"
        )

        restore_button = message_box.addButton(
            "Restore",
            QMessageBox.ButtonRole.AcceptRole,
        )
        discard_button = message_box.addButton(
            "Discard",
            QMessageBox.ButtonRole.DestructiveRole,
        )
        message_box.setDefaultButton(restore_button)
        message_box.exec()

        if message_box.clickedButton() is discard_button:
            self.logging_service.info(
                "Recovery data discarded by the user."
            )

            try:
                self.recovery_service.discard_recovery()
            except RuntimeError as error:
                QMessageBox.warning(
                    self,
                    "Unable to Discard Recovery",
                    str(error),
                )
            return

        try:
            project_data, project_path = (
                self.recovery_service.load_recovery()
            )
        except (
            FileNotFoundError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            QMessageBox.critical(
                self,
                "Unable to Restore Recovery",
                str(error),
            )
            return

        self._apply_project_data(project_data)
        self.current_project_path = project_path
        self.last_generated_path = None
        self._update_window_title()
        self._update_script_statistics()

        self.statusBarWidget.setText(
            "Recovered unsaved work successfully."
        )
        self.logging_service.info(
            "Unsaved recovery data restored successfully."
        )

    def _schedule_recovery_save(self, *args: object) -> None:
        """Save recovery data after a short period of inactivity."""

        del args

        if not self._recovery_enabled:
            return

        self._recovery_timer.start()

    def _save_recovery_snapshot(self) -> None:
        """Write the current project state to the recovery file."""

        if not self._recovery_enabled:
            return

        project_data = self._collect_project_data()
        script_text = str(project_data["script"]).strip()

        if not script_text and self.current_project_path is None:
            try:
                self.recovery_service.discard_recovery()
            except RuntimeError:
                pass
            return

        try:
            self.recovery_service.save_recovery(
                project_data=project_data,
                current_project_path=self.current_project_path,
            )
        except (
            RuntimeError,
            TypeError,
            ValueError,
        ):
            return

    def _restore_window_state(self) -> None:
        """Restore the saved window size, position, and state."""

        if not self.settings_service.get_restore_window_state():
            return

        saved_geometry = (
            self.settings_service.get_window_geometry()
        )
        saved_state = self.settings_service.get_window_state()

        if not saved_geometry.isEmpty():
            self.restoreGeometry(saved_geometry)

        if not saved_state.isEmpty():
            self.restoreState(saved_state)

    def _save_window_state(self) -> None:
        """Save the current window size, position, and state."""

        self.settings_service.set_window_geometry(
            self.saveGeometry()
        )
        self.settings_service.set_window_state(
            self.saveState()
        )

    def _create_menus(self) -> None:
        """Create the application menu bar."""

        file_menu = self.menuBar().addMenu("&File")

        self.newProjectAction = QAction(
            "&New Project",
            self,
        )
        self.newProjectAction.setShortcut(
            QKeySequence.StandardKey.New
        )
        self.newProjectAction.triggered.connect(
            self._clear_project
        )

        self.openProjectAction = QAction(
            "&Open Project...",
            self,
        )
        self.openProjectAction.setShortcut(
            QKeySequence.StandardKey.Open
        )
        self.openProjectAction.triggered.connect(
            self._load_project
        )

        self.saveProjectAction = QAction(
            "&Save Project...",
            self,
        )
        self.saveProjectAction.setShortcut(
            QKeySequence.StandardKey.Save
        )
        self.saveProjectAction.triggered.connect(
            self._save_project
        )

        self.exitAction = QAction(
            "E&xit",
            self,
        )
        self.exitAction.setShortcut(
            QKeySequence.StandardKey.Quit
        )
        self.exitAction.triggered.connect(self.close)

        file_menu.addAction(self.newProjectAction)
        file_menu.addAction(self.openProjectAction)
        file_menu.addAction(self.saveProjectAction)
        file_menu.addSeparator()

        self.recentProjectsMenu = file_menu.addMenu(
            "Recent Projects"
        )
        self.recentProjectsMenu.aboutToShow.connect(
            self._refresh_recent_projects_menu
        )

        file_menu.addSeparator()
        file_menu.addAction(self.exitAction)

        self._refresh_recent_projects_menu()

        edit_menu = self.menuBar().addMenu("&Edit")

        self.undoAction = QAction("&Undo", self)
        self.undoAction.setShortcut(
            QKeySequence.StandardKey.Undo
        )
        self.undoAction.triggered.connect(
            self.scriptEditor.editor.undo
        )

        self.redoAction = QAction("&Redo", self)
        self.redoAction.setShortcut(
            QKeySequence.StandardKey.Redo
        )
        self.redoAction.triggered.connect(
            self.scriptEditor.editor.redo
        )

        self.cutAction = QAction("Cu&t", self)
        self.cutAction.setShortcut(
            QKeySequence.StandardKey.Cut
        )
        self.cutAction.triggered.connect(
            self.scriptEditor.editor.cut
        )

        self.copyAction = QAction("&Copy", self)
        self.copyAction.setShortcut(
            QKeySequence.StandardKey.Copy
        )
        self.copyAction.triggered.connect(
            self.scriptEditor.editor.copy
        )

        self.pasteAction = QAction("&Paste", self)
        self.pasteAction.setShortcut(
            QKeySequence.StandardKey.Paste
        )
        self.pasteAction.triggered.connect(
            self.scriptEditor.editor.paste
        )

        self.selectAllAction = QAction(
            "Select &All",
            self,
        )
        self.selectAllAction.setShortcut(
            QKeySequence.StandardKey.SelectAll
        )
        self.selectAllAction.triggered.connect(
            self.scriptEditor.editor.selectAll
        )

        edit_menu.addAction(self.undoAction)
        edit_menu.addAction(self.redoAction)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cutAction)
        edit_menu.addAction(self.copyAction)
        edit_menu.addAction(self.pasteAction)
        edit_menu.addSeparator()
        edit_menu.addAction(self.selectAllAction)

        tools_menu = self.menuBar().addMenu("&Tools")

        self.openOutputFolderAction = QAction(
            "Open &Output Folder",
            self,
        )
        self.openOutputFolderAction.triggered.connect(
            self._open_output_folder
        )

        self.openProfilesFolderAction = QAction(
            "Open &Profiles Folder",
            self,
        )
        self.openProfilesFolderAction.triggered.connect(
            self._open_profiles_folder
        )

        self.preferencesAction = QAction(
            "&Preferences...",
            self,
        )
        self.preferencesAction.triggered.connect(
            self._show_preferences_dialog
        )

        tools_menu.addAction(self.openOutputFolderAction)
        tools_menu.addAction(self.openProfilesFolderAction)
        tools_menu.addSeparator()
        tools_menu.addAction(self.preferencesAction)

        help_menu = self.menuBar().addMenu("&Help")

        self.aboutAction = QAction(
            f"About {APP_NAME}...",
            self,
        )
        self.aboutAction.triggered.connect(
            self._show_about_dialog
        )

        help_menu.addAction(self.aboutAction)

    def _refresh_recent_projects_menu(self) -> None:
        """Rebuild the Recent Projects submenu."""

        self.recentProjectsMenu.clear()

        recent_projects = (
            self.settings_service.get_recent_projects()
        )

        if not recent_projects:
            empty_action = self.recentProjectsMenu.addAction(
                "No Recent Projects"
            )
            empty_action.setEnabled(False)
            return

        stem_counts: dict[str, int] = {}

        for project_path in recent_projects:
            stem_key = project_path.stem.casefold()
            stem_counts[stem_key] = (
                stem_counts.get(stem_key, 0) + 1
            )

        for project_path in recent_projects:
            display_name = project_path.stem

            if stem_counts[project_path.stem.casefold()] > 1:
                display_name = (
                    f"{display_name} — {project_path.parent}"
                )

            project_action = self.recentProjectsMenu.addAction(
                display_name
            )
            project_action.setToolTip(str(project_path))
            project_action.triggered.connect(
                lambda checked=False, path=project_path: (
                    self._load_project_path(path)
                )
            )

        self.recentProjectsMenu.addSeparator()

        clear_action = self.recentProjectsMenu.addAction(
            "Clear Recent Projects"
        )
        clear_action.triggered.connect(
            self._clear_recent_projects
        )

    def _clear_recent_projects(self) -> None:
        """Clear the Recent Projects list."""

        self.settings_service.clear_recent_projects()
        self._refresh_recent_projects_menu()
        self.statusBarWidget.setText(
            "Recent projects cleared."
        )

    def _show_preferences_dialog(self) -> None:
        """Show and save general application preferences."""

        current_preferences = GeneralPreferences(
            restore_window_state=(
                self.settings_service.get_restore_window_state()
            ),
            confirm_before_clearing=(
                self.settings_service.get_confirm_before_clearing()
            ),
        )

        dialog = PreferencesDialog(
            preferences=current_preferences,
            parent=self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        preferences = dialog.preferences()

        self.settings_service.set_restore_window_state(
            preferences.restore_window_state
        )
        self.settings_service.set_confirm_before_clearing(
            preferences.confirm_before_clearing
        )

        self.statusBarWidget.setText(
            "Preferences saved successfully."
        )

    def _show_about_dialog(self) -> None:
        """Show current application and system information."""

        profile_name = (
            self.voicePanel.profileControls.current_profile_name()
        )

        project_name = ""

        if self.current_project_path is not None:
            project_name = self.current_project_path.stem

        dialog = AboutDialog(
            parent=self,
            current_profile=profile_name,
            current_project=project_name,
            voice_count=len(self.voicePanel.all_voices),
        )
        dialog.exec()

    def _restore_application_settings(self) -> None:
        """Restore saved narration and output preferences."""

        language = self.settings_service.get_language()
        voice = self.settings_service.get_voice()

        language_index = self.voicePanel.languageFilter.findData(
            language
        )

        if language_index < 0:
            language_index = 0

        self.voicePanel.languageFilter.setCurrentIndex(
            language_index
        )

        voice_index = self.voicePanel.voiceCombo.findText(voice)

        if voice_index >= 0:
            self.voicePanel.voiceCombo.setCurrentIndex(
                voice_index
            )

        self.voicePanel.speedSlider.setValue(
            self.settings_service.get_speed()
        )
        self.voicePanel.pitchSlider.setValue(
            self.settings_service.get_pitch()
        )
        self.voicePanel.volumeSlider.setValue(
            self.settings_service.get_volume()
        )

        output_folder = self.settings_service.get_output_folder()

        self.outputPanel.folder.setText(str(output_folder))
        self.outputPanel.clear_filename()
        self.outputPanel.suggest_filename("Untitled.mp3")

    def _save_voice_preferences(self) -> None:
        """Store the current narration preferences."""

        voice = self.voicePanel.voiceCombo.currentText().strip()

        if not self._is_valid_voice(voice):
            return

        language = (
            self.voicePanel.languageFilter.currentData() or ""
        )

        self.settings_service.save_voice_settings(
            language=str(language),
            voice=voice,
            speed=self.voicePanel.speedSlider.value(),
            pitch=self.voicePanel.pitchSlider.value(),
            volume=self.voicePanel.volumeSlider.value(),
        )

        if not self._applying_profile:
            self._update_profile_modified_state()

    def _save_output_folder(self) -> None:
        """Store the current output folder."""

        output_folder = self.outputPanel.folder.text().strip()

        if not output_folder:
            return

        self.settings_service.set_output_folder(
            output_folder
        )

    def _connect_actions(self) -> None:
        """Connect application controls."""

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
        self.buttonBar.save.clicked.connect(
            self._save_project
        )
        self.buttonBar.load.clicked.connect(
            self._load_project
        )
        self.buttonBar.clear.clicked.connect(
            self._clear_project
        )

        self.scriptEditor.openButton.clicked.connect(
            self._open_script
        )
        self.scriptEditor.saveButton.clicked.connect(
            self._save_script
        )
        self.scriptEditor.clearButton.clicked.connect(
            self._clear_script
        )

        self.voicePanel.languageFilter.currentIndexChanged.connect(
            self._save_voice_preferences
        )
        self.voicePanel.voiceCombo.currentTextChanged.connect(
            self._save_voice_preferences
        )
        self.voicePanel.speedSlider.valueChanged.connect(
            self._save_voice_preferences
        )
        self.voicePanel.speedSlider.valueChanged.connect(
            self._update_script_statistics
        )
        self.voicePanel.pitchSlider.valueChanged.connect(
            self._save_voice_preferences
        )
        self.voicePanel.volumeSlider.valueChanged.connect(
            self._save_voice_preferences
        )
        self.scriptEditor.editor.textChanged.connect(
            self._update_script_statistics
        )
        self.scriptEditor.editor.textChanged.connect(
            self._schedule_recovery_save
        )

        self.outputPanel.folder.textChanged.connect(
            self._schedule_recovery_save
        )
        self.outputPanel.filename.textChanged.connect(
            self._schedule_recovery_save
        )

        self.voicePanel.languageFilter.currentIndexChanged.connect(
            self._schedule_recovery_save
        )
        self.voicePanel.voiceCombo.currentIndexChanged.connect(
            self._schedule_recovery_save
        )
        self.voicePanel.speedSlider.valueChanged.connect(
            self._schedule_recovery_save
        )
        self.voicePanel.pitchSlider.valueChanged.connect(
            self._schedule_recovery_save
        )
        self.voicePanel.volumeSlider.valueChanged.connect(
            self._schedule_recovery_save
        )
        self.scriptEditor.script_file_dropped.connect(
            self._load_dropped_script_file
        )

        profile_controls = self.voicePanel.profileControls
        profile_controls.profile_selected.connect(
            self._profile_selected
        )
        profile_controls.new_requested.connect(
            self._new_profile
        )
        profile_controls.save_requested.connect(
            self._save_profile
        )
        profile_controls.rename_requested.connect(
            self._rename_profile
        )
        profile_controls.delete_requested.connect(
            self._delete_profile
        )
        profile_controls.open_folder_requested.connect(
            self._open_profiles_folder
        )

    def _initialize_profiles(self) -> None:
        """Load available profiles and restore the last selection."""

        controls = self.voicePanel.profileControls

        try:
            profile_names = self.profile_service.list_profiles()
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Load Profiles",
                str(error),
            )
            controls.set_profiles([])
            return

        last_profile = self.settings_service.get_last_profile()

        if last_profile not in profile_names:
            last_profile = ""
            self.settings_service.clear_last_profile()

        controls.set_profiles(
            profile_names=profile_names,
            selected_profile=last_profile,
        )

        if last_profile:
            self._load_profile_by_name(
                last_profile,
                show_error=True,
            )

    def _collect_profile_data(self) -> dict[str, object]:
        """Collect the current reusable narration settings."""

        return {
            "language": str(
                self.voicePanel.languageFilter.currentData() or ""
            ),
            "voice": self.voicePanel.voiceCombo.currentText().strip(),
            "speed": self.voicePanel.speedSlider.value(),
            "pitch": self.voicePanel.pitchSlider.value(),
            "volume": self.voicePanel.volumeSlider.value(),
        }

    def _apply_profile_data(
        self,
        profile_data: dict[str, object],
    ) -> None:
        """Apply narration settings from a saved profile."""

        self._applying_profile = True

        try:
            language = str(profile_data["language"])
            voice = str(profile_data["voice"])

            language_index = (
                self.voicePanel.languageFilter.findData(language)
            )

            if language_index < 0:
                language_index = 0

            self.voicePanel.languageFilter.setCurrentIndex(
                language_index
            )

            voice_index = self.voicePanel.voiceCombo.findText(voice)

            if voice_index < 0:
                raise ValueError(
                    "The profile voice is not currently available."
                )

            self.voicePanel.voiceCombo.setCurrentIndex(voice_index)
            self.voicePanel.speedSlider.setValue(
                int(profile_data["speed"])
            )
            self.voicePanel.pitchSlider.setValue(
                int(profile_data["pitch"])
            )
            self.voicePanel.volumeSlider.setValue(
                int(profile_data["volume"])
            )
        finally:
            self._applying_profile = False

        self._save_voice_preferences()

    def _profile_selected(self, profile_name: str) -> None:
        """Load the narration profile selected by the user."""

        if not profile_name:
            self._loaded_profile_data = None
            self.settings_service.clear_last_profile()
            self.voicePanel.profileControls.set_modified(False)
            self.statusBarWidget.setText("No narration profile selected.")
            return

        self._load_profile_by_name(
            profile_name,
            show_error=True,
        )

    def _load_profile_by_name(
        self,
        profile_name: str,
        show_error: bool,
    ) -> bool:
        """Load and apply a profile by name."""

        try:
            loaded_data = self.profile_service.load_profile(
                profile_name
            )
            self._apply_profile_data(loaded_data)
        except (
            FileNotFoundError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            self._loaded_profile_data = None
            self.settings_service.clear_last_profile()
            self.voicePanel.profileControls.select_no_profile()

            if show_error:
                QMessageBox.critical(
                    self,
                    "Unable to Load Profile",
                    str(error),
                )

            return False

        self._loaded_profile_data = {
            key: loaded_data[key]
            for key in (
                "language",
                "voice",
                "speed",
                "pitch",
                "volume",
            )
        }
        self.settings_service.set_last_profile(profile_name)
        self.voicePanel.profileControls.set_modified(False)
        self.statusBarWidget.setText(
            f"Narration profile loaded: {profile_name}"
        )

        return True

    def _new_profile(self) -> None:
        """Create a user-named profile from current settings."""

        profile_name, accepted = QInputDialog.getText(
            self,
            "Create Narration Profile",
            "Profile name:",
        )

        if not accepted:
            return

        try:
            self.profile_service.create_profile(
                profile_name,
                self._collect_profile_data(),
            )
        except (
            FileExistsError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            QMessageBox.warning(
                self,
                "Unable to Create Profile",
                str(error),
            )
            return

        normalized_name = profile_name.strip()
        self.voicePanel.profileControls.add_profile(
            normalized_name
        )
        self._loaded_profile_data = self._collect_profile_data()
        self.settings_service.set_last_profile(normalized_name)
        self.voicePanel.profileControls.set_modified(False)
        self.statusBarWidget.setText(
            f"Narration profile created: {normalized_name}"
        )

    def _save_profile(self) -> None:
        """Save current settings into the selected profile."""

        profile_name = (
            self.voicePanel.profileControls.current_profile_name()
        )

        if not profile_name:
            return

        profile_data = self._collect_profile_data()

        try:
            self.profile_service.save_profile(
                profile_name,
                profile_data,
            )
        except (
            FileNotFoundError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            QMessageBox.critical(
                self,
                "Unable to Save Profile",
                str(error),
            )
            return

        self._loaded_profile_data = profile_data
        self.settings_service.set_last_profile(profile_name)
        self.voicePanel.profileControls.set_modified(False)
        self.statusBarWidget.setText(
            f"Narration profile saved: {profile_name}"
        )

    def _rename_profile(self) -> None:
        """Rename the selected narration profile."""

        controls = self.voicePanel.profileControls
        current_name = controls.current_profile_name()

        if not current_name:
            return

        new_name, accepted = QInputDialog.getText(
            self,
            "Rename Narration Profile",
            "New profile name:",
            text=current_name,
        )

        if not accepted:
            return

        try:
            self.profile_service.rename_profile(
                current_name,
                new_name,
            )
        except (
            FileExistsError,
            FileNotFoundError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            QMessageBox.warning(
                self,
                "Unable to Rename Profile",
                str(error),
            )
            return

        normalized_name = new_name.strip()
        controls.rename_profile(
            current_name,
            normalized_name,
        )
        self.settings_service.set_last_profile(normalized_name)
        self.statusBarWidget.setText(
            f"Narration profile renamed: {normalized_name}"
        )

    def _delete_profile(self) -> None:
        """Delete the selected narration profile after confirmation."""

        controls = self.voicePanel.profileControls
        profile_name = controls.current_profile_name()

        if not profile_name:
            return

        response = QMessageBox.question(
            self,
            "Delete Narration Profile?",
            (
                f'Delete profile "{profile_name}"?\n\n'
                "This cannot be undone."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if response != QMessageBox.StandardButton.Yes:
            return

        try:
            self.profile_service.delete_profile(profile_name)
        except (FileNotFoundError, RuntimeError, ValueError) as error:
            QMessageBox.critical(
                self,
                "Unable to Delete Profile",
                str(error),
            )
            return

        controls.remove_profile(profile_name)
        self._loaded_profile_data = None
        self.settings_service.clear_last_profile()
        self.statusBarWidget.setText(
            f"Narration profile deleted: {profile_name}"
        )

    def _open_profiles_folder(self) -> None:
        """Open the narration profiles folder in the file manager."""

        try:
            profiles_folder = (
                self.profile_service.ensure_profiles_folder()
            )
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Open Profiles Folder",
                str(error),
            )
            return

        opened = QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(profiles_folder.resolve()))
        )

        if not opened:
            QMessageBox.critical(
                self,
                "Unable to Open Profiles Folder",
                "Windows could not open the profiles folder.",
            )
            return

        self.statusBarWidget.setText(
            f"Opened profiles folder: {profiles_folder}"
        )

    def _update_profile_modified_state(self) -> None:
        """Mark the selected profile when settings differ from disk."""

        controls = self.voicePanel.profileControls

        if (
            not controls.current_profile_name()
            or self._loaded_profile_data is None
        ):
            controls.set_modified(False)
            return

        controls.set_modified(
            self._collect_profile_data()
            != self._loaded_profile_data
        )

    def _create_shortcuts(self) -> None:
        """Create keyboard shortcuts for common actions."""

        self.generateReturnShortcut = QShortcut(
            QKeySequence("Ctrl+Return"),
            self,
        )
        self.generateReturnShortcut.activated.connect(
            self._generate_narration
        )

        self.generateEnterShortcut = QShortcut(
            QKeySequence("Ctrl+Enter"),
            self,
        )
        self.generateEnterShortcut.activated.connect(
            self._generate_narration
        )

    def _get_preview_text(self) -> str:
        """Return selected script text or a short script preview."""

        text_cursor = self.scriptEditor.editor.textCursor()
        selected_text = text_cursor.selectedText().strip()

        if selected_text:
            return selected_text.replace("\u2029", "\n")

        text = self.scriptEditor.editor.toPlainText().strip()

        if not text:
            return ""

        sentence_endings = (".", "!", "?")
        sentence = text

        for index, character in enumerate(text):
            if character in sentence_endings:
                sentence = text[: index + 1]
                break

        words = sentence.split()

        if len(words) <= 30:
            return sentence.strip()

        return " ".join(words[:30])

    def _update_script_statistics(self) -> None:
        """Refresh live script statistics and duration estimate."""

        self.scriptStatistics.update_statistics(
            text=self.scriptEditor.editor.toPlainText(),
            speed_adjustment=self.voicePanel.speedSlider.value(),
        )

    def _open_script(self) -> None:
        """Choose and load a plain-text or Markdown script."""

        open_folder = (
            self.settings_service.get_last_script_open_folder()
        )

        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Narration Script",
            str(open_folder),
            (
                "Narration Scripts (*.txt *.md);;"
                "Text Files (*.txt);;"
                "Markdown Files (*.md)"
            ),
        )

        if not selected_path:
            return

        script_path = Path(selected_path).expanduser()

        self.settings_service.set_last_script_open_folder(
            script_path.parent
        )
        self._load_script_path(script_path)

    def _save_script(self) -> None:
        """Save only the current narration script text."""

        script_text = self.scriptEditor.editor.toPlainText()

        if not script_text.strip():
            QMessageBox.warning(
                self,
                "No Script to Save",
                "Enter or open a narration script before saving it.",
            )
            return

        suggested_name = "narration-script.txt"

        if self.current_project_path is not None:
            suggested_name = (
                f"{self.current_project_path.stem}.txt"
            )

        save_folder = (
            self.settings_service.get_last_script_save_folder()
        )

        selected_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Narration Script",
            str(save_folder / suggested_name),
            (
                "Text Files (*.txt);;"
                "Markdown Files (*.md)"
            ),
        )

        if not selected_path:
            return

        script_path = Path(selected_path).expanduser()

        if script_path.suffix.lower() not in {".txt", ".md"}:
            script_path = script_path.with_suffix(".txt")

        try:
            script_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            script_path.write_text(
                script_text,
                encoding="utf-8",
            )
        except OSError as error:
            QMessageBox.critical(
                self,
                "Unable to Save Script",
                (
                    "Scriptolator could not save the narration "
                    "script.\n\n"
                    f"{error}"
                ),
            )
            return

        self.settings_service.set_last_script_save_folder(
            script_path.parent
        )

        self.statusBarWidget.setText(
            f"Script saved: {script_path.name}"
        )
        self.logging_service.info(
            f"Script saved: {script_path}"
        )

        QMessageBox.information(
            self,
            "Script Saved",
            (
                "The narration script was saved successfully.\n\n"
                f"{script_path}"
            ),
        )

    def _clear_script(self) -> None:
        """Clear only the narration script editor."""

        script_text = self.scriptEditor.editor.toPlainText()

        if not script_text:
            self.scriptEditor.editor.setFocus()
            return

        if self.settings_service.get_confirm_before_clearing():
            response = QMessageBox.question(
                self,
                "Clear Narration Script?",
                (
                    "This will remove all text from the narration "
                    "script editor.\n\n"
                    "The project voice and output settings will remain."
                ),
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if response != QMessageBox.StandardButton.Yes:
                return

        self.scriptEditor.editor.clear()
        self.last_generated_path = None
        self._update_script_statistics()
        self.statusBarWidget.setText(
            "Narration script cleared."
        )
        self.scriptEditor.editor.setFocus()

    def _load_script_path(self, script_path: Path) -> None:
        """Load one supported script file into the editor."""

        normalized_path = Path(script_path).expanduser()

        if not normalized_path.is_file():
            QMessageBox.warning(
                self,
                "Script File Not Found",
                (
                    "The narration script could not be found.\n\n"
                    f"{normalized_path}"
                ),
            )
            return

        if normalized_path.suffix.lower() not in {".txt", ".md"}:
            QMessageBox.warning(
                self,
                "Unsupported Script File",
                (
                    "Scriptolator can currently load only .txt "
                    "and .md files."
                ),
            )
            return

        current_script = (
            self.scriptEditor.editor.toPlainText().strip()
        )

        if current_script:
            response = QMessageBox.question(
                self,
                "Replace Current Script?",
                (
                    "The current narration script contains text.\n\n"
                    "Replace it with:\n"
                    f"{normalized_path.name}?"
                ),
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if response != QMessageBox.StandardButton.Yes:
                self.statusBarWidget.setText(
                    "Narration script was not loaded."
                )
                return

        try:
            script_text = normalized_path.read_text(
                encoding="utf-8-sig"
            )
        except UnicodeDecodeError:
            try:
                script_text = normalized_path.read_text(
                    encoding="cp1252"
                )
            except (OSError, UnicodeDecodeError) as error:
                QMessageBox.critical(
                    self,
                    "Unable to Load Script",
                    (
                        "Scriptolator could not read the narration "
                        "script.\n\n"
                        f"{error}"
                    ),
                )
                return
        except OSError as error:
            QMessageBox.critical(
                self,
                "Unable to Load Script",
                (
                    "Scriptolator could not read the narration "
                    "script.\n\n"
                    f"{error}"
                ),
            )
            return

        self.scriptEditor.editor.setPlainText(script_text)
        self.current_project_path = None
        self.last_generated_path = None
        self._update_window_title()
        self._update_script_statistics()

        self.statusBarWidget.setText(
            f"Loaded script: {normalized_path.name}"
        )
        self.logging_service.info(
            f"Script loaded: {normalized_path}"
        )
        self.scriptEditor.editor.setFocus()

    def _load_dropped_script_file(
        self,
        file_path: str,
    ) -> None:
        """Load a dropped .txt or .md file into the script editor."""

        self._load_script_path(Path(file_path))

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

    def _get_projects_folder(self) -> Path | None:
        """Create and return Scriptolator's project folder."""

        projects_folder = self.project_root / "projects"

        try:
            projects_folder.mkdir(
                parents=True,
                exist_ok=True,
            )
        except OSError as error:
            QMessageBox.critical(
                self,
                "Unable to Access Projects Folder",
                (
                    "Scriptolator could not create or access the "
                    "projects folder.\n\n"
                    f"{error}"
                ),
            )
            return None

        return projects_folder

    def _save_project(self) -> None:
        """Save the current narration workspace as a project."""

        projects_folder = self._get_projects_folder()

        if projects_folder is None:
            return

        suggested_name = (
            self.current_project_path.name
            if self.current_project_path is not None
            else "untitled.scriptolator"
        )

        initial_path = projects_folder / suggested_name

        selected_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Scriptolator Project",
            str(initial_path),
            (
                "Scriptolator Projects "
                f"(*{ProjectService.FILE_EXTENSION})"
            ),
        )

        if not selected_path:
            return

        normalized_selected_path = (
            ProjectService.normalize_project_path(
                Path(selected_path)
            )
        )

        self.outputPanel.suggest_filename(
            f"{normalized_selected_path.stem}.mp3"
        )

        project_data = self._collect_project_data()

        try:
            saved_path = ProjectService.save_project(
                normalized_selected_path,
                project_data,
            )
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            QMessageBox.critical(
                self,
                "Unable to Save Project",
                str(error),
            )
            return

        self.current_project_path = saved_path
        self.settings_service.add_recent_project(saved_path)
        self._refresh_recent_projects_menu()
        self._update_window_title()

        self.statusBarWidget.setText(
            f"Project saved: {saved_path}"
        )
        self.logging_service.info(
            f"Project saved: {saved_path}"
        )

        QMessageBox.information(
            self,
            "Project Saved",
            (
                "Scriptolator project saved successfully:\n\n"
                f"{saved_path}"
            ),
        )

    def _load_project(self) -> None:
        """Choose and load a Scriptolator project."""

        projects_folder = self._get_projects_folder()

        if projects_folder is None:
            return

        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Scriptolator Project",
            str(projects_folder),
            (
                "Scriptolator Projects "
                f"(*{ProjectService.FILE_EXTENSION} "
                f"*{ProjectService.LEGACY_FILE_EXTENSION})"
            ),
        )

        if not selected_path:
            return

        self._load_project_path(Path(selected_path))

    def _load_project_path(
        self,
        project_path: Path,
    ) -> None:
        """Load a project from a known file path."""

        normalized_path = Path(project_path).expanduser()

        if not normalized_path.is_file():
            self.settings_service.remove_recent_project(
                normalized_path
            )
            self._refresh_recent_projects_menu()

            QMessageBox.warning(
                self,
                "Project Not Found",
                (
                    "The project file could not be found and was "
                    "removed from Recent Projects.\n\n"
                    f"{normalized_path}"
                ),
            )
            return

        try:
            project_data = ProjectService.load_project(
                normalized_path
            )
        except (
            FileNotFoundError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            QMessageBox.critical(
                self,
                "Unable to Load Project",
                str(error),
            )
            return

        self._apply_project_data(project_data)

        self.current_project_path = normalized_path.resolve()
        self.last_generated_path = None

        self.settings_service.add_recent_project(
            self.current_project_path
        )
        self._refresh_recent_projects_menu()
        self._update_window_title()

        self._save_voice_preferences()
        self._save_output_folder()

        self.statusBarWidget.setText(
            f"Project loaded: {self.current_project_path}"
        )
        self.logging_service.info(
            f"Project loaded: {self.current_project_path}"
        )

        QMessageBox.information(
            self,
            "Project Loaded",
            (
                "Scriptolator project loaded successfully:\n\n"
                f"{self.current_project_path}"
            ),
        )

    def _collect_project_data(self) -> dict[str, object]:
        """Collect the current interface values for project saving."""

        return {
            "script": self.scriptEditor.editor.toPlainText(),
            "language": (
                self.voicePanel.languageFilter.currentData() or ""
            ),
            "voice": self.voicePanel.voiceCombo.currentText().strip(),
            "speed": self.voicePanel.speedSlider.value(),
            "pitch": self.voicePanel.pitchSlider.value(),
            "volume": self.voicePanel.volumeSlider.value(),
            "output_folder": (
                self.outputPanel.folder.text().strip()
            ),
            "output_filename": (
                self.outputPanel.filename.text().strip()
            ),
        }

    def _apply_project_data(
        self,
        project_data: dict[str, object],
    ) -> None:
        """Restore project values into the interface."""

        script = str(project_data["script"])
        language = str(project_data["language"])
        voice = str(project_data["voice"])
        output_folder = str(project_data["output_folder"])
        output_filename = str(project_data["output_filename"])

        speed = int(project_data["speed"])
        pitch = int(project_data["pitch"])
        volume = int(project_data["volume"])

        language_index = (
            self.voicePanel.languageFilter.findData(language)
        )

        if language_index < 0:
            language_index = 0

        self.voicePanel.languageFilter.setCurrentIndex(
            language_index
        )

        voice_index = self.voicePanel.voiceCombo.findText(voice)

        if voice_index >= 0:
            self.voicePanel.voiceCombo.setCurrentIndex(
                voice_index
            )

        self.scriptEditor.editor.setPlainText(script)
        self.voicePanel.speedSlider.setValue(speed)
        self.voicePanel.pitchSlider.setValue(pitch)
        self.voicePanel.volumeSlider.setValue(volume)
        self.outputPanel.folder.setText(output_folder)
        self.outputPanel.set_filename(
            output_filename,
            user_defined=bool(output_filename.strip()),
        )

        self.scriptEditor.editor.setFocus()

    def _clear_project(self) -> None:
        """Clear the current script and project-specific values."""

        has_content = bool(
            self.scriptEditor.editor.toPlainText().strip()
            or self.outputPanel.filename.text().strip()
        )

        if (
            has_content
            and self.settings_service.get_confirm_before_clearing()
        ):
            response = QMessageBox.question(
                self,
                "Clear Current Project?",
                (
                    "This will clear the current script and output "
                    "filename.\n\n"
                    "Unsaved project changes will be lost."
                ),
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if response != QMessageBox.StandardButton.Yes:
                return

        self.scriptEditor.editor.clear()
        self.outputPanel.clear_filename()
        self.outputPanel.suggest_filename("Untitled.mp3")

        self.current_project_path = None
        self.last_generated_path = None

        self._update_window_title()
        self.statusBarWidget.setText("Current project cleared.")
        self.scriptEditor.editor.setFocus()

    def _update_window_title(self) -> None:
        """Display the active project and application version."""

        application_title = f"{APP_NAME} {APP_VERSION}"

        if self.current_project_path is None:
            self.setWindowTitle(application_title)
            return

        project_name = self.current_project_path.stem

        self.setWindowTitle(
            f"{project_name} — {application_title}"
        )

    def _generate_narration(self) -> None:
        """Start MP3 generation in a background thread."""

        if (
            self.generation_thread is not None
            and self.generation_thread.isRunning()
        ):
            QMessageBox.information(
                self,
                "Narration In Progress",
                "Scriptolator is already generating narration.",
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

        self._save_voice_preferences()
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

        self.buttonBar.generate.show_generating_state()
        self._set_generation_controls_enabled(False)
        self.statusBarWidget.setText("Generating narration...")
        self.logging_service.info(
            (
                "Narration generation started: "
                f"voice={voice}, output={output_path}"
            )
        )

        self.generation_thread.start()

    def _narration_generated(self, generated_path: str) -> None:
        """Handle successful narration generation."""

        self.last_generated_path = Path(generated_path)
        self.buttonBar.generate.show_complete_state()

        self.statusBarWidget.setText(
            f"Narration saved: {generated_path}"
        )
        self.logging_service.info(
            f"Narration generated successfully: {generated_path}"
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

        self.buttonBar.generate.show_error_state()

        self.statusBarWidget.setText(
            "Narration generation failed."
        )
        self.logging_service.error(
            f"Narration generation failed: {error_message}"
        )

        if "Permission denied" in error_message:
            user_message = (
                "Scriptolator could not replace the output file.\n\n"
                "The MP3 may currently be open in another application. "
                "Close the audio player or choose a different filename.\n\n"
                f"Technical details:\n{error_message}"
            )
        else:
            user_message = (
                "Scriptolator could not generate the narration.\n\n"
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

        self.buttonBar.save.setEnabled(enabled)
        self.buttonBar.load.setEnabled(enabled)
        self.buttonBar.clear.setEnabled(enabled)

        self.newProjectAction.setEnabled(enabled)
        self.openProjectAction.setEnabled(enabled)
        self.saveProjectAction.setEnabled(enabled)

        self.outputPanel.folder.setEnabled(enabled)
        self.outputPanel.filename.setEnabled(enabled)
        self.outputPanel.browse.setEnabled(enabled)

        self.voicePanel.profileControls.setEnabled(enabled)
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
                    "Scriptolator is still generating narration.\n\n"
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
                    "Scriptolator is still generating a voice preview.\n\n"
                    "Wait for the preview to finish before closing."
                ),
            )
            event.ignore()
            return

        self._recovery_timer.stop()
        self._recovery_enabled = False
        self._save_window_state()

        try:
            self.recovery_service.discard_recovery()
        except RuntimeError as error:
            QMessageBox.warning(
                self,
                "Unable to Clear Recovery",
                str(error),
            )

        self.logging_service.info(
            f"{APP_NAME} closed normally."
        )
        event.accept()

    @staticmethod
    def _normalize_mp3_filename(filename: str) -> str:
        """Return a Windows-safe MP3 filename."""

        entered_name = filename.strip()

        if entered_name.casefold().endswith(".mp3"):
            entered_name = entered_name[:-4]

        sanitized_characters: list[str] = []

        for character in entered_name:
            if ord(character) < 32:
                sanitized_characters.append(" ")
                continue

            if character in '<>:"/\\|?*':
                sanitized_characters.append("-")
                continue

            sanitized_characters.append(character)

        sanitized_stem = "".join(sanitized_characters)

        while "  " in sanitized_stem:
            sanitized_stem = sanitized_stem.replace("  ", " ")

        sanitized_stem = sanitized_stem.strip(" .")

        reserved_names = {
            "con",
            "prn",
            "aux",
            "nul",
            *(f"com{number}" for number in range(1, 10)),
            *(f"lpt{number}" for number in range(1, 10)),
        }

        if sanitized_stem.casefold() in reserved_names:
            sanitized_stem = f"{sanitized_stem}-narration"

        if not sanitized_stem:
            sanitized_stem = "Untitled"

        return f"{sanitized_stem}.mp3"

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