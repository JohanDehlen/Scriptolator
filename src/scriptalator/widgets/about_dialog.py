import platform
import sys
from pathlib import Path

from PySide6 import __version__ as PYSIDE_VERSION
from PySide6.QtCore import Qt, qVersion
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from version import APP_NAME, APP_VERSION
from widgets.help_viewer import HelpViewerDialog


def _resource_path(filename: str) -> Path:
    """Return a resource path for source and packaged builds."""

    if getattr(sys, "frozen", False):
        bundle_root = Path(
            getattr(sys, "_MEIPASS", Path(sys.executable).parent)
        )
        return bundle_root / "resources" / filename

    return Path(__file__).resolve().parents[1] / "resources" / filename


class AboutDialog(QDialog):
    """Display Scriptolator branding, help links, and diagnostics."""

    COPYRIGHT_TEXT = "© 2026 Johan Dehlen"
    TAGLINE = "Professional AI Narration"

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
        self.setMinimumWidth(620)
        self.resize(620, 700)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_path = _resource_path("scriptolator.png")
        logo_pixmap = QPixmap(str(logo_path))

        if not logo_pixmap.isNull():
            logo.setPixmap(
                logo_pixmap.scaled(
                    128,
                    128,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 30px; font-weight: 700;"
        )

        tagline = QLabel(self.TAGLINE)
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet(
            "font-size: 16px; font-weight: 600;"
        )

        description = QLabel(
            "Transform scripts into professional AI narration "
            "using Microsoft Edge Neural voices."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)

        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("font-weight: 600;")

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(tagline)
        layout.addWidget(description)
        layout.addWidget(version_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        product_details = QGridLayout()
        product_details.setHorizontalSpacing(18)
        product_details.setVerticalSpacing(7)

        detail_rows = [
            ("Created by", "Johan Dehlen"),
            (
                "Narration engine",
                "Microsoft Edge Neural Voices via edge-tts",
            ),
            ("Website", "Scriptolator.com"),
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

        for row, (label_text, value_text) in enumerate(
            detail_rows
        ):
            label = QLabel(f"{label_text}:")
            label.setStyleSheet("font-weight: 600;")

            value = QLabel(value_text)
            value.setWordWrap(True)
            value.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )

            product_details.addWidget(label, row, 0)
            product_details.addWidget(value, row, 1)

        layout.addLayout(product_details)

        help_buttons = QHBoxLayout()

        quick_start_button = QPushButton("Quick Start")
        quick_start_button.clicked.connect(
            lambda: self._open_help(
                "Quick Start Guide",
                "QuickStart.md",
            )
        )

        user_guide_button = QPushButton("User Guide")
        user_guide_button.clicked.connect(
            lambda: self._open_help(
                "User Guide",
                "UserGuide.md",
            )
        )

        release_notes_button = QPushButton("Release Notes")
        release_notes_button.clicked.connect(
            lambda: self._open_help(
                "Release Notes",
                "ReleaseNotes.md",
            )
        )

        help_buttons.addWidget(quick_start_button)
        help_buttons.addWidget(user_guide_button)
        help_buttons.addWidget(release_notes_button)

        layout.addLayout(help_buttons)

        diagnostics_label = QLabel("System information")
        diagnostics_label.setStyleSheet(
            "font-size: 14px; font-weight: 600;"
        )
        layout.addWidget(diagnostics_label)

        self.systemInfo = QTextEdit()
        self.systemInfo.setReadOnly(True)
        self.systemInfo.setPlainText(
            self.build_system_information()
        )
        self.systemInfo.setMinimumHeight(170)
        layout.addWidget(self.systemInfo)

        self.copyButton = QPushButton(
            "Copy System Information"
        )
        self.copyButton.clicked.connect(
            self._copy_system_information
        )
        layout.addWidget(self.copyButton)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
        )
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setWindowFlag(
            Qt.WindowType.WindowContextHelpButtonHint,
            False,
        )

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
            (
                "Current profile: "
                f"{self.current_profile or 'No Profile'}"
            )
        )
        lines.append(
            (
                "Current project: "
                f"{self.current_project or 'No Project'}"
            )
        )
        lines.append(f"Executable: {sys.executable}")

        return "\n".join(lines)

    def _open_help(
        self,
        title: str,
        document_name: str,
    ) -> None:
        """Open one bundled help document."""

        dialog = HelpViewerDialog(
            title=title,
            document_name=document_name,
            parent=self,
        )
        dialog.exec()

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

        QMessageBox.information(
            self,
            "System Information Copied",
            (
                "Scriptolator system information was copied "
                "to the clipboard."
            ),
        )