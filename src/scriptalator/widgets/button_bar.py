from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QWidget,
)


class GenerateButton(QPushButton):
    """Primary action button with an animated generation state."""

    IDLE_TEXT = "Generate MP3"
    COMPLETE_TEXT = "✓ Complete"

    SPINNER_FRAMES = (
        "◐",
        "◓",
        "◑",
        "◒",
    )

    def __init__(self) -> None:
        super().__init__(self.IDLE_TEXT)

        self._spinner_index = 0
        self._generating = False

        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(120)
        self._spinner_timer.timeout.connect(
            self._advance_spinner
        )

        self._complete_timer = QTimer(self)
        self._complete_timer.setSingleShot(True)
        self._complete_timer.setInterval(2000)
        self._complete_timer.timeout.connect(
            self.show_idle_state
        )

        self.setMinimumHeight(42)
        self.setDefault(True)
        self.setToolTip(
            "Generate an MP3 narration from the current script."
        )

    def is_generating(self) -> bool:
        """Return whether the animated generation state is active."""

        return self._generating

    def show_generating_state(self) -> None:
        """Disable the button and start the rotating indicator."""

        self._complete_timer.stop()
        self._generating = True
        self._spinner_index = 0
        self.setEnabled(False)
        self._update_spinner_text()
        self._spinner_timer.start()

    def show_complete_state(self) -> None:
        """Show a short success state before returning to idle."""

        self._spinner_timer.stop()
        self._generating = False
        self.setText(self.COMPLETE_TEXT)
        self.setEnabled(False)
        self._complete_timer.start()

    def show_idle_state(self) -> None:
        """Restore the normal ready-to-generate state."""

        self._spinner_timer.stop()
        self._complete_timer.stop()
        self._generating = False
        self.setText(self.IDLE_TEXT)
        self.setEnabled(True)

    def show_error_state(self) -> None:
        """Return immediately to the normal state after an error."""

        self.show_idle_state()

    def _advance_spinner(self) -> None:
        """Advance the animated spinner by one frame."""

        self._spinner_index = (
            self._spinner_index + 1
        ) % len(self.SPINNER_FRAMES)

        self._update_spinner_text()

    def _update_spinner_text(self) -> None:
        """Display the current spinner frame."""

        frame = self.SPINNER_FRAMES[self._spinner_index]
        self.setText(f"{frame} Generating Narration...")


class ButtonBar(QWidget):
    """Provide the main narration and project action buttons."""

    def __init__(self) -> None:
        super().__init__()

        layout = QHBoxLayout(self)

        self.generate = GenerateButton()

        self.play = QPushButton("Play MP3")
        self.play.setToolTip(
            "Open the most recently generated MP3."
        )

        self.open = QPushButton("Open Output Folder")
        self.open.setToolTip(
            "Open the current narration output folder."
        )

        self.save = QPushButton("Save Project")
        self.save.setToolTip(
            "Save the complete Scriptolator project."
        )

        self.load = QPushButton("Open Project")
        self.load.setToolTip(
            "Open a saved Scriptolator project."
        )

        self.clear = QPushButton("New Project")
        self.clear.setToolTip(
            "Clear the current project and start a new one."
        )

        layout.addWidget(self.generate, 2)
        layout.addWidget(self.play)
        layout.addWidget(self.open)

        layout.addStretch()

        layout.addWidget(self.save)
        layout.addWidget(self.load)
        layout.addWidget(self.clear)