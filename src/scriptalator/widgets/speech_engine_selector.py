from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QWidget,
)

from services.azure_settings_service import AzureSettingsService
from services.speech_engine_manager import SpeechEngineManager


class SpeechEngineSelector(QWidget):
    """Select and configure Scriptolator's narration engine."""

    engine_changed = Signal(str)
    azure_settings_requested = Signal()

    def __init__(
        self,
        engine_manager: SpeechEngineManager,
        settings_service: AzureSettingsService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.engine_manager = engine_manager
        self.settings_service = settings_service
        self._restoring_selection = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.engineCombo = QComboBox()
        self.engineCombo.setToolTip(
            "Choose the Microsoft speech platform used for previews "
            "and narration generation."
        )

        for (
            engine_id,
            display_name,
        ) in self.engine_manager.available_engines().items():
            self.engineCombo.addItem(
                display_name,
                engine_id,
            )

        self.configureButton = QPushButton("Configure Azure...")
        self.configureButton.setToolTip(
            "Enter, test, or clear Microsoft Azure AI Speech settings."
        )

        layout.addWidget(QLabel("Speech Engine"))
        layout.addWidget(self.engineCombo, 1)
        layout.addWidget(self.configureButton)

        self.engineCombo.currentIndexChanged.connect(
            self._selection_changed
        )
        self.configureButton.clicked.connect(
            self.azure_settings_requested
        )

        self.restore_saved_engine()

    @property
    def current_engine_id(self) -> str:
        """Return the selected stable engine identifier."""

        engine_id = self.engineCombo.currentData()

        if isinstance(engine_id, str):
            return engine_id

        return SpeechEngineManager.EDGE_ENGINE_ID

    def restore_saved_engine(self) -> None:
        """Restore and activate the saved engine selection."""

        saved_engine = self.settings_service.get_selected_engine()

        if (
            saved_engine == SpeechEngineManager.AZURE_ENGINE_ID
            and not self.settings_service.is_azure_configured()
        ):
            saved_engine = SpeechEngineManager.EDGE_ENGINE_ID
            self.settings_service.set_selected_engine(saved_engine)

        self._restoring_selection = True

        try:
            index = self.engineCombo.findData(saved_engine)

            if index < 0:
                index = self.engineCombo.findData(
                    SpeechEngineManager.EDGE_ENGINE_ID
                )

            self.engineCombo.setCurrentIndex(max(index, 0))
            self._activate_engine(
                self.current_engine_id,
                show_errors=False,
            )
        finally:
            self._restoring_selection = False

        self._update_configure_button()

    def refresh_after_azure_settings(self) -> None:
        """Refresh selection after Azure settings are changed."""

        selected_engine = self.current_engine_id

        if (
            selected_engine
            == SpeechEngineManager.AZURE_ENGINE_ID
            and not self.settings_service.is_azure_configured()
        ):
            self.set_engine(
                SpeechEngineManager.EDGE_ENGINE_ID
            )
            return

        if (
            selected_engine
            == SpeechEngineManager.AZURE_ENGINE_ID
        ):
            if self._activate_engine(
                selected_engine,
                show_errors=True,
            ):
                self.engine_changed.emit(selected_engine)

        self._update_configure_button()

    def set_engine(
        self,
        engine_id: str,
    ) -> bool:
        """Select and activate an engine programmatically."""

        index = self.engineCombo.findData(engine_id)

        if index < 0:
            raise ValueError(
                f"Unsupported speech engine: {engine_id!r}"
            )

        if index == self.engineCombo.currentIndex():
            activated = self._activate_engine(
                engine_id,
                show_errors=True,
            )

            if activated:
                self.engine_changed.emit(engine_id)

            return activated

        self.engineCombo.setCurrentIndex(index)

        return self.current_engine_id == engine_id

    def _selection_changed(self) -> None:
        """Activate and persist the user-selected engine."""

        if self._restoring_selection:
            return

        engine_id = self.current_engine_id

        if self._activate_engine(
            engine_id,
            show_errors=True,
        ):
            self.settings_service.set_selected_engine(
                engine_id
            )
            self._update_configure_button()
            self.engine_changed.emit(engine_id)
            return

        self._restore_previous_valid_selection()

    def _activate_engine(
        self,
        engine_id: str,
        *,
        show_errors: bool,
    ) -> bool:
        """Configure the manager for the requested engine."""

        try:
            if engine_id == SpeechEngineManager.EDGE_ENGINE_ID:
                self.engine_manager.use_edge()
                return True

            if engine_id == SpeechEngineManager.AZURE_ENGINE_ID:
                azure_settings = (
                    self.settings_service.get_azure_settings()
                )

                if not azure_settings.is_configured:
                    if show_errors:
                        QMessageBox.information(
                            self,
                            "Azure Configuration Required",
                            (
                                "Configure Microsoft Azure AI Speech "
                                "before selecting it as the narration "
                                "engine."
                            ),
                        )
                        self.azure_settings_requested.emit()

                    return False

                self.engine_manager.use_azure(
                    subscription_key=(
                        azure_settings.subscription_key
                    ),
                    region=azure_settings.region,
                )
                return True

            raise ValueError(
                f"Unsupported speech engine: {engine_id!r}"
            )
        except (RuntimeError, ValueError) as error:
            if show_errors:
                QMessageBox.critical(
                    self,
                    "Unable to Select Speech Engine",
                    str(error),
                )

            return False

    def _restore_previous_valid_selection(self) -> None:
        """Return the combo box to the active engine."""

        active_engine = self.engine_manager.current_engine_id
        index = self.engineCombo.findData(active_engine)

        self._restoring_selection = True

        try:
            self.engineCombo.setCurrentIndex(
                max(index, 0)
            )
        finally:
            self._restoring_selection = False

        self._update_configure_button()

    def _update_configure_button(self) -> None:
        """Clarify whether Azure is configured."""

        if self.settings_service.is_azure_configured():
            self.configureButton.setText("Azure Settings...")
            self.configureButton.setToolTip(
                "Review, test, or clear Microsoft Azure AI Speech "
                "settings."
            )
            return

        self.configureButton.setText("Configure Azure...")
        self.configureButton.setToolTip(
            "Configure Microsoft Azure AI Speech before selecting it."
        )