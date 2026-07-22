from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ScriptTextEdit(QTextEdit):
    """Text editor that accepts supported narration files."""

    script_file_dropped = Signal(str)

    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".md",
    }

    def __init__(self) -> None:
        super().__init__()

        self.setAcceptDrops(True)
        self.setPlaceholderText(
            "Paste, type, or drop a .txt or .md narration file here..."
        )

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Accept a drag containing one supported local file."""

        file_path = self._supported_file_from_event(event)

        if file_path is None:
            event.ignore()
            return

        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Report a supported dropped file to the parent widget."""

        file_path = self._supported_file_from_event(event)

        if file_path is None:
            event.ignore()
            return

        self.script_file_dropped.emit(str(file_path))
        event.acceptProposedAction()

    @classmethod
    def is_supported_script_file(cls, file_path: Path) -> bool:
        """Return whether a path is a supported narration text file."""

        return (
            file_path.is_file()
            and file_path.suffix.lower() in cls.SUPPORTED_EXTENSIONS
        )

    @classmethod
    def _supported_file_from_event(
        cls,
        event: QDragEnterEvent | QDropEvent,
    ) -> Path | None:
        """Return the supported local file carried by a drag event."""

        mime_data = event.mimeData()

        if not mime_data.hasUrls():
            return None

        local_files = [
            Path(url.toLocalFile())
            for url in mime_data.urls()
            if url.isLocalFile()
        ]

        if len(local_files) != 1:
            return None

        file_path = local_files[0]

        if not cls.is_supported_script_file(file_path):
            return None

        return file_path


class ScriptEditor(QWidget):
    """Provide the narration text editor and its existing toolbar."""

    script_file_dropped = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()

        self.openButton = QPushButton("Open")
        self.saveButton = QPushButton("Save")
        self.clearButton = QPushButton("Clear")

        self.wordLabel = QLabel("Words: 0")
        self.timeLabel = QLabel("Time: 0 sec")

        toolbar.addWidget(self.openButton)
        toolbar.addWidget(self.saveButton)
        toolbar.addWidget(self.clearButton)

        toolbar.addStretch()

        toolbar.addWidget(self.wordLabel)
        toolbar.addWidget(self.timeLabel)

        layout.addLayout(toolbar)

        self.editor = ScriptTextEdit()
        layout.addWidget(self.editor)

        self.editor.textChanged.connect(self.update_stats)
        self.editor.script_file_dropped.connect(
            self.script_file_dropped.emit
        )

    def update_stats(self) -> None:
        """Update the existing compact word and time indicators."""

        text = self.editor.toPlainText()
        words = len(text.split())

        self.wordLabel.setText(f"Words: {words}")

        seconds = round(words / 2.5)

        self.timeLabel.setText(
            f"Time: {seconds} sec"
        )