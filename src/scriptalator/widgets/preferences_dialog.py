from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class GeneralPreferences:
    """User-configurable general application preferences."""

    restore_window_state: bool = True
    confirm_before_clearing: bool = True


class PreferencesDialog(QDialog):
    """Edit Scriptolator application preferences."""

    def __init__(
        self,
        preferences: GeneralPreferences,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        intro = QLabel(
            "Choose how Scriptolator restores and clears your workspace."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        general_group = QGroupBox("General")
        general_layout = QVBoxLayout(general_group)
        general_layout.setSpacing(10)

        self.restoreWindowStateCheckBox = QCheckBox(
            "Restore previous window size and position"
        )
        self.restoreWindowStateCheckBox.setChecked(
            preferences.restore_window_state
        )
        self.restoreWindowStateCheckBox.setToolTip(
            "Reopen Scriptolator using the previous window size, "
            "position, and maximized state."
        )

        self.confirmBeforeClearingCheckBox = QCheckBox(
            "Confirm before clearing a project or script"
        )
        self.confirmBeforeClearingCheckBox.setChecked(
            preferences.confirm_before_clearing
        )
        self.confirmBeforeClearingCheckBox.setToolTip(
            "Ask for confirmation before clearing the current "
            "project or narration script."
        )

        general_layout.addWidget(
            self.restoreWindowStateCheckBox
        )
        general_layout.addWidget(
            self.confirmBeforeClearingCheckBox
        )

        layout.addWidget(general_group)

        remembered_note = QLabel(
            "Scriptolator always remembers your last narration profile "
            "and output folder until you change them."
        )
        remembered_note.setWordWrap(True)
        remembered_note.setStyleSheet("color: gray;")
        layout.addWidget(remembered_note)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        self.setWindowFlag(
            Qt.WindowType.WindowContextHelpButtonHint,
            False,
        )

    def preferences(self) -> GeneralPreferences:
        """Return the preferences currently selected in the dialog."""

        return GeneralPreferences(
            restore_window_state=(
                self.restoreWindowStateCheckBox.isChecked()
            ),
            confirm_before_clearing=(
                self.confirmBeforeClearingCheckBox.isChecked()
            ),
        )