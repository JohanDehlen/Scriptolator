import platform
import sys

from PySide6 import __version__ as PYSIDE_VERSION
from PySide6.QtCore import Qt, qVersion
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from version import APP_NAME, APP_VERSION


class AboutDialog(QDialog):
    """Display Scriptalator version and diagnostic information."""

    COPYRIGHT_TEXT = "© 2026 Johan Dehlen"

    def __init__(
        self,
        parent: QWidget | None = None,
        current_profile: str = "",
        current_project: str = "",
        voice_count: int | None = None,
    ) -> None:
        super().__init__(parent)

        self.current_profile = current_profile.strip()
        self.current_project = current_project.strip()
        self.voice_count = voice_count

        self.setWindowTitle(f"About {APP_NAME}")
        self.setModal(True)
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            """
        )

        subtitle = QLabel(
            "Transform scripts into professional AI narration."
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(version_label)

        details = QGridLayout()
        details.setHorizontalSpacing(18)
        details.setVerticalSpacing(6)

        detail_rows = [
            ("Created by", "Johan Dehlen"),
            ("Powered by", "Microsoft Edge Neural Voices and edge-tts"),
            ("Copyright", self.COPYRIGHT_TEXT),
        ]

        if self.current_profile:
            detail_rows.append(
                ("Current profile", self.current_profile)
            )

        if self.current_project:
            detail_rows.append(
                ("Current project", self.current_project)
            )

        for row, (label_text, value_text) in enumerate(detail_rows):
            label = QLabel(f"{label_text}:")
            label.setStyleSheet("font-weight: bold;")

            value = QLabel(value_text)
            value.setWordWrap(True)

            details.addWidget(label, row, 0)
            details.addWidget(value, row, 1)

        layout.addLayout(details)

        self.copyButton = QPushButton("Copy System Information")
        self.copyButton.clicked.connect(
            self._copy_system_information
        )

        layout.addWidget(self.copyButton)

        self.systemInfo = QTextEdit()
        self.systemInfo.setReadOnly(True)
        self.systemInfo.setPlainText(
            self.build_system_information()
        )
        self.systemInfo.setMinimumHeight(170)

        layout.addWidget(self.systemInfo)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
        )
        button_box.accepted.connect(self.accept)

        layout.addWidget(button_box)

    def build_system_information(self) -> str:
        """Return diagnostic information suitable for issue reports."""

        lines = [
            f"{APP_NAME}: {APP_VERSION}",
            f"Python: {platform.python_version()}",
            f"PySide6: {PYSIDE_VERSION}",
            f"Qt: {qVersion()}",
            f"Operating system: {platform.platform()}",
        ]

        if self.voice_count is not None:
            lines.append(
                f"Available Microsoft voices: {self.voice_count}"
            )

        lines.append(
            f"Current profile: {self.current_profile or 'No Profile'}"
        )
        lines.append(
            f"Current project: {self.current_project or 'No Project'}"
        )
        lines.append(f"Executable: {sys.executable}")

        return "\n".join(lines)

    def _copy_system_information(self) -> None:
        """Copy diagnostic information to the system clipboard."""

        application = QApplication.instance()

        if application is None:
            QMessageBox.warning(
                self,
                "Clipboard Unavailable",
                "The system clipboard is not available.",
            )
            return

        application.clipboard().setText(
            self.build_system_information()
        )

        self.copyButton.setText("Copied")

        QMessageBox.information(
            self,
            "System Information Copied",
            (
                "Scriptalator system information was copied "
                "to the clipboard."
            ),
        )

        self.copyButton.setText("Copy System Information")