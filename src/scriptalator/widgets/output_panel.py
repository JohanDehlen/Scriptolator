from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class OutputPanel(QWidget):
    """Provide narration output folder and filename controls."""

    filename_user_edited = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self._filename_was_edited = False

        layout = QFormLayout(self)

        folder_layout = QHBoxLayout()

        self.folder = QLineEdit()
        self.folder.setPlaceholderText(
            "Choose where generated narration files are saved"
        )
        self.folder.setToolTip(
            (
                "Scriptolator remembers this folder and restores it "
                "the next time the application starts."
            )
        )

        self.browse = QPushButton("Browse...")
        self.browse.setToolTip(
            "Choose the folder for generated MP3 narration files."
        )

        folder_layout.addWidget(self.folder)
        folder_layout.addWidget(self.browse)

        self.filename = QLineEdit()
        self.filename.setPlaceholderText("Narration filename")
        self.filename.setToolTip(
            (
                "Enter the MP3 filename. Scriptolator adds the .mp3 "
                "extension automatically when needed."
            )
        )
        self.filename.textEdited.connect(
            self._handle_filename_edited
        )

        layout.addRow("Output Folder", folder_layout)
        layout.addRow("Output File", self.filename)

    def filename_was_edited(self) -> bool:
        """Return whether the user manually changed the filename."""

        return self._filename_was_edited

    def set_filename(
        self,
        filename: str,
        *,
        user_defined: bool,
    ) -> None:
        """Set the filename and record whether it is user-defined."""

        self.filename.setText(filename.strip())
        self._filename_was_edited = user_defined

    def suggest_filename(self, filename: str) -> bool:
        """Set a suggested filename unless the user already edited it."""

        if self._filename_was_edited:
            return False

        self.filename.setText(filename.strip())
        return True

    def clear_filename(self) -> None:
        """Clear the filename and reset its user-edited state."""

        self.filename.clear()
        self._filename_was_edited = False

    def _handle_filename_edited(self, filename: str) -> None:
        """Record a manual filename edit."""

        self._filename_was_edited = True
        self.filename_user_edited.emit(filename)