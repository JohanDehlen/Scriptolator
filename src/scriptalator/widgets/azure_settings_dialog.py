from __future__ import annotations

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.azure_settings_service import AzureSettingsService
from services.azure_tts_service import AzureTTSService


class AzureConnectionTestThread(QThread):
    """Test Azure credentials without blocking the dialog."""

    connection_succeeded = Signal(int)
    connection_failed = Signal(str)

    def __init__(
        self,
        subscription_key: str,
        region: str,
    ) -> None:
        super().__init__()

        self.subscription_key = subscription_key
        self.region = region

    def run(self) -> None:
        """Retrieve the Azure voice catalogue as a connection test."""

        try:
            service = AzureTTSService(
                subscription_key=self.subscription_key,
                region=self.region,
            )
            voices = service.get_voice_details()
        except Exception as error:
            self.connection_failed.emit(str(error))
        else:
            self.connection_succeeded.emit(len(voices))


class AzureSettingsDialog(QDialog):
    """Configure Microsoft Azure AI Speech for Scriptolator."""

    def __init__(
        self,
        settings_service: AzureSettingsService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.settings_service = settings_service
        self.test_thread: AzureConnectionTestThread | None = None
        self.connection_verified = False

        self.setWindowTitle("Microsoft Azure AI Speech")
        self.setModal(True)
        self.setMinimumWidth(540)
        self.setWindowFlag(
            Qt.WindowType.WindowContextHelpButtonHint,
            False,
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        intro = QLabel(
            "Connect Scriptolator to Microsoft Azure AI Speech to use "
            "the same premium Microsoft speech platform used by Clipchamp."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        credentials_group = QGroupBox("Azure Speech credentials")
        credentials_layout = QFormLayout(credentials_group)
        credentials_layout.setSpacing(10)

        key_row = QHBoxLayout()

        self.subscriptionKeyEdit = QLineEdit()
        self.subscriptionKeyEdit.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.subscriptionKeyEdit.setPlaceholderText(
            "Enter Azure Speech Key 1 or Key 2"
        )
        self.subscriptionKeyEdit.setClearButtonEnabled(True)

        self.showKeyCheckBox = QCheckBox("Show")
        self.showKeyCheckBox.setToolTip(
            "Temporarily display the Azure subscription key."
        )

        key_row.addWidget(self.subscriptionKeyEdit, 1)
        key_row.addWidget(self.showKeyCheckBox)

        self.regionEdit = QLineEdit()
        self.regionEdit.setPlaceholderText(
            "For example: southafricanorth"
        )
        self.regionEdit.setClearButtonEnabled(True)

        credentials_layout.addRow(
            "Subscription key:",
            key_row,
        )
        credentials_layout.addRow(
            "Region:",
            self.regionEdit,
        )

        layout.addWidget(credentials_group)

        security_note = QLabel(
            "Your subscription key is stored securely in Windows "
            "Credential Manager. It is not written to projects, profiles, "
            "settings.ini, or GitHub."
        )
        security_note.setWordWrap(True)
        security_note.setStyleSheet("color: gray;")
        layout.addWidget(security_note)

        actions_layout = QHBoxLayout()

        self.testButton = QPushButton("Test Connection")
        self.testButton.setDefault(False)

        self.clearButton = QPushButton("Clear Azure Settings")
        self.clearButton.setToolTip(
            "Remove the saved Azure key and region from Scriptolator."
        )

        actions_layout.addWidget(self.testButton)
        actions_layout.addWidget(self.clearButton)
        actions_layout.addStretch()

        layout.addLayout(actions_layout)

        self.statusLabel = QLabel()
        self.statusLabel.setWordWrap(True)
        self.statusLabel.setMinimumHeight(24)
        layout.addWidget(self.statusLabel)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.saveButton = self.buttonBox.button(
            QDialogButtonBox.StandardButton.Save
        )
        self.saveButton.setEnabled(False)

        layout.addWidget(self.buttonBox)

        self.showKeyCheckBox.toggled.connect(
            self._toggle_key_visibility
        )
        self.subscriptionKeyEdit.textChanged.connect(
            self._credentials_changed
        )
        self.regionEdit.textChanged.connect(
            self._credentials_changed
        )
        self.testButton.clicked.connect(
            self._test_connection
        )
        self.clearButton.clicked.connect(
            self._clear_settings
        )
        self.buttonBox.accepted.connect(
            self._save_and_accept
        )
        self.buttonBox.rejected.connect(self.reject)

        self._load_saved_settings()

    def _load_saved_settings(self) -> None:
        """Load the current Azure settings into the dialog."""

        try:
            azure_settings = (
                self.settings_service.get_azure_settings()
            )
        except RuntimeError as error:
            self.statusLabel.setText(str(error))
            self.statusLabel.setStyleSheet("color: #b00020;")
            self.regionEdit.setText(
                self.settings_service.get_azure_region()
            )
            return

        self.subscriptionKeyEdit.setText(
            azure_settings.subscription_key
        )
        self.regionEdit.setText(
            azure_settings.region
        )

        if azure_settings.is_configured:
            self.statusLabel.setText(
                "Azure credentials are saved. Test the connection "
                "before saving any changes."
            )
            self.statusLabel.setStyleSheet("color: gray;")

    def _toggle_key_visibility(self, visible: bool) -> None:
        """Show or mask the Azure subscription key."""

        mode = (
            QLineEdit.EchoMode.Normal
            if visible
            else QLineEdit.EchoMode.Password
        )
        self.subscriptionKeyEdit.setEchoMode(mode)

    def _credentials_changed(self) -> None:
        """Invalidate a previous connection test after editing."""

        self.connection_verified = False
        self.saveButton.setEnabled(False)

        if self.test_thread is None:
            self.statusLabel.setText(
                "Test the connection before saving."
            )
            self.statusLabel.setStyleSheet("color: gray;")

    def _test_connection(self) -> None:
        """Validate the entered Azure credentials."""

        if (
            self.test_thread is not None
            and self.test_thread.isRunning()
        ):
            return

        subscription_key = (
            self.subscriptionKeyEdit.text().strip()
        )
        region = self.regionEdit.text().strip().lower()

        if not subscription_key:
            QMessageBox.warning(
                self,
                "Azure Key Required",
                "Enter an Azure Speech subscription key.",
            )
            self.subscriptionKeyEdit.setFocus()
            return

        if not region:
            QMessageBox.warning(
                self,
                "Azure Region Required",
                "Enter the region used by your Azure Speech resource.",
            )
            self.regionEdit.setFocus()
            return

        self.connection_verified = False
        self._set_controls_enabled(False)
        self.testButton.setText("Testing...")
        self.statusLabel.setText(
            "Connecting to Azure AI Speech and retrieving voices..."
        )
        self.statusLabel.setStyleSheet("color: gray;")

        self.test_thread = AzureConnectionTestThread(
            subscription_key=subscription_key,
            region=region,
        )
        self.test_thread.connection_succeeded.connect(
            self._connection_succeeded
        )
        self.test_thread.connection_failed.connect(
            self._connection_failed
        )
        self.test_thread.finished.connect(
            self._connection_test_finished
        )
        self.test_thread.start()

    def _connection_succeeded(self, voice_count: int) -> None:
        """Report a successful Azure connection test."""

        self.connection_verified = True
        self.saveButton.setEnabled(True)
        self.statusLabel.setText(
            "Connection successful. "
            f"Azure returned {voice_count} voices."
        )
        self.statusLabel.setStyleSheet("color: #167c2f;")

    def _connection_failed(self, error_text: str) -> None:
        """Report a failed Azure connection test."""

        self.connection_verified = False
        self.saveButton.setEnabled(False)
        self.statusLabel.setText(
            "Connection failed. Check the subscription key and region."
        )
        self.statusLabel.setStyleSheet("color: #b00020;")

        QMessageBox.critical(
            self,
            "Azure Connection Failed",
            (
                "Scriptolator could not connect to Azure AI Speech.\n\n"
                f"{error_text}"
            ),
        )

    def _connection_test_finished(self) -> None:
        """Restore the dialog after the connection test."""

        worker = self.test_thread
        self.test_thread = None

        self._set_controls_enabled(True)
        self.testButton.setText("Test Connection")
        self.saveButton.setEnabled(
            self.connection_verified
        )

        if worker is not None:
            worker.deleteLater()

    def _set_controls_enabled(self, enabled: bool) -> None:
        """Enable or disable controls during network work."""

        self.subscriptionKeyEdit.setEnabled(enabled)
        self.showKeyCheckBox.setEnabled(enabled)
        self.regionEdit.setEnabled(enabled)
        self.testButton.setEnabled(enabled)
        self.clearButton.setEnabled(enabled)
        self.buttonBox.button(
            QDialogButtonBox.StandardButton.Cancel
        ).setEnabled(enabled)

    def _save_and_accept(self) -> None:
        """Save verified Azure settings and close the dialog."""

        if not self.connection_verified:
            QMessageBox.warning(
                self,
                "Connection Test Required",
                "Test the Azure connection before saving.",
            )
            return

        try:
            self.settings_service.save_azure_settings(
                subscription_key=(
                    self.subscriptionKeyEdit.text()
                ),
                region=self.regionEdit.text(),
            )
        except (RuntimeError, ValueError) as error:
            QMessageBox.critical(
                self,
                "Unable to Save Azure Settings",
                str(error),
            )
            return

        self.accept()

    def _clear_settings(self) -> None:
        """Remove saved Azure settings after confirmation."""

        answer = QMessageBox.question(
            self,
            "Clear Azure Settings",
            (
                "Remove the saved Azure subscription key and region?\n\n"
                "Scriptolator will switch back to Microsoft Edge."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.settings_service.clear_azure_settings()
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "Unable to Clear Azure Settings",
                str(error),
            )
            return

        self.subscriptionKeyEdit.clear()
        self.regionEdit.setText(
            self.settings_service.DEFAULT_AZURE_REGION
        )
        self.connection_verified = False
        self.saveButton.setEnabled(False)
        self.statusLabel.setText(
            "Azure settings were removed. Microsoft Edge is now "
            "the saved speech engine."
        )
        self.statusLabel.setStyleSheet("color: #167c2f;")