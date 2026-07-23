import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


def documentation_root() -> Path:
    """Return the folder containing bundled documentation."""

    if getattr(sys, "frozen", False):
        bundle_root = Path(
            getattr(sys, "_MEIPASS", Path(sys.executable).parent)
        )
        return bundle_root / "docs"

    return Path(__file__).resolve().parents[3] / "docs"


class HelpViewerDialog(QDialog):
    """Display one Scriptolator Markdown document."""

    def __init__(
        self,
        title: str,
        document_name: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.document_path = (
            documentation_root() / document_name
        )

        self.setWindowTitle(title)
        self.setModal(False)
        self.resize(900, 700)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        heading = QLabel(title)
        heading.setStyleSheet(
            "font-size: 20px; font-weight: 600;"
        )
        layout.addWidget(heading)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.anchorClicked.connect(
            QDesktopServices.openUrl
        )
        layout.addWidget(self.browser, 1)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        button_box.rejected.connect(self.reject)
        button_box.clicked.connect(self.close)
        layout.addWidget(button_box)

        self.setWindowFlag(
            Qt.WindowType.WindowContextHelpButtonHint,
            False,
        )

        self._load_document()

    def _load_document(self) -> None:
        """Read and render the selected Markdown document."""

        if not self.document_path.is_file():
            self.browser.setPlainText(
                (
                    "The requested help document could not be found.\n\n"
                    f"{self.document_path}"
                )
            )

            QMessageBox.warning(
                self,
                "Help Document Not Found",
                (
                    "Scriptolator could not locate the requested "
                    "help document.\n\n"
                    f"{self.document_path}"
                ),
            )
            return

        try:
            markdown_text = self.document_path.read_text(
                encoding="utf-8"
            )
        except OSError as error:
            self.browser.setPlainText(str(error))

            QMessageBox.critical(
                self,
                "Unable to Open Help",
                (
                    "Scriptolator could not read the requested "
                    "help document.\n\n"
                    f"{error}"
                ),
            )
            return

        self.browser.setMarkdown(markdown_text)
        self.browser.moveCursor(
            self.browser.textCursor().MoveOperation.Start
        )