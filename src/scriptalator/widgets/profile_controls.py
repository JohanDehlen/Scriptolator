from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ProfileControls(QWidget):
    """Display controls for user-defined narration profiles."""

    profile_selected = Signal(str)
    new_requested = Signal()
    save_requested = Signal()
    rename_requested = Signal()
    delete_requested = Signal()

    NO_PROFILE_TEXT = "No Profile"
    NO_PROFILE_VALUE = ""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(6)

        heading = QLabel("Narration Profile")
        heading.setStyleSheet("font-weight: bold;")

        layout.addWidget(heading)

        self.profileCombo = QComboBox()
        self.profileCombo.addItem(
            self.NO_PROFILE_TEXT,
            self.NO_PROFILE_VALUE,
        )

        layout.addWidget(self.profileCombo)

        button_layout = QHBoxLayout()

        self.newButton = QPushButton("New")
        self.saveButton = QPushButton("Save")
        self.renameButton = QPushButton("Rename")
        self.deleteButton = QPushButton("Delete")

        button_layout.addWidget(self.newButton)
        button_layout.addWidget(self.saveButton)
        button_layout.addWidget(self.renameButton)
        button_layout.addWidget(self.deleteButton)

        layout.addLayout(button_layout)

        self.profileCombo.currentIndexChanged.connect(
            self._profile_changed
        )
        self.newButton.clicked.connect(
            self.new_requested.emit
        )
        self.saveButton.clicked.connect(
            self.save_requested.emit
        )
        self.renameButton.clicked.connect(
            self.rename_requested.emit
        )
        self.deleteButton.clicked.connect(
            self.delete_requested.emit
        )

        self._update_action_buttons()

    def set_profiles(
        self,
        profile_names: list[str],
        selected_profile: str = "",
    ) -> None:
        """Populate the profile selector and restore a selection."""

        normalized_profiles = sorted(
            {
                profile_name.strip()
                for profile_name in profile_names
                if isinstance(profile_name, str)
                and profile_name.strip()
            },
            key=str.casefold,
        )

        self.profileCombo.blockSignals(True)
        self.profileCombo.clear()
        self.profileCombo.addItem(
            self.NO_PROFILE_TEXT,
            self.NO_PROFILE_VALUE,
        )

        for profile_name in normalized_profiles:
            self.profileCombo.addItem(
                profile_name,
                profile_name,
            )

        selected_index = self.profileCombo.findData(
            selected_profile.strip()
        )

        if selected_index < 0:
            selected_index = 0

        self.profileCombo.setCurrentIndex(selected_index)
        self.profileCombo.blockSignals(False)

        self._update_action_buttons()

    def current_profile_name(self) -> str:
        """Return the selected user-defined profile name."""

        profile_name = self.profileCombo.currentData()

        if not isinstance(profile_name, str):
            return ""

        return profile_name.strip()

    def select_profile(
        self,
        profile_name: str,
    ) -> bool:
        """Select a profile by name."""

        profile_index = self.profileCombo.findData(
            profile_name.strip()
        )

        if profile_index < 0:
            return False

        self.profileCombo.setCurrentIndex(profile_index)

        return True

    def select_no_profile(self) -> None:
        """Select the unsaved No Profile state."""

        self.profileCombo.setCurrentIndex(0)

    def add_profile(
        self,
        profile_name: str,
    ) -> None:
        """Add and select a newly created profile."""

        normalized_name = profile_name.strip()

        if not normalized_name:
            return

        existing_index = self.profileCombo.findData(
            normalized_name
        )

        if existing_index >= 0:
            self.profileCombo.setCurrentIndex(existing_index)
            return

        self.profileCombo.addItem(
            normalized_name,
            normalized_name,
        )

        self._sort_profiles()
        self.select_profile(normalized_name)

    def remove_profile(
        self,
        profile_name: str,
    ) -> None:
        """Remove a profile and return to No Profile."""

        profile_index = self.profileCombo.findData(
            profile_name.strip()
        )

        if profile_index >= 0:
            self.profileCombo.removeItem(profile_index)

        self.select_no_profile()

    def rename_profile(
        self,
        current_name: str,
        new_name: str,
    ) -> None:
        """Rename a profile in the selector."""

        current_index = self.profileCombo.findData(
            current_name.strip()
        )

        if current_index < 0:
            return

        normalized_new_name = new_name.strip()

        self.profileCombo.setItemText(
            current_index,
            normalized_new_name,
        )
        self.profileCombo.setItemData(
            current_index,
            normalized_new_name,
        )

        self._sort_profiles()
        self.select_profile(normalized_new_name)

    def _profile_changed(self) -> None:
        """Report the selected profile and update button state."""

        self._update_action_buttons()
        self.profile_selected.emit(
            self.current_profile_name()
        )

    def _update_action_buttons(self) -> None:
        """Enable actions that require a selected profile."""

        has_profile = bool(
            self.current_profile_name()
        )

        self.saveButton.setEnabled(has_profile)
        self.renameButton.setEnabled(has_profile)
        self.deleteButton.setEnabled(has_profile)

    def _sort_profiles(self) -> None:
        """Sort profiles while keeping No Profile first."""

        selected_profile = self.current_profile_name()

        profile_names = [
            str(self.profileCombo.itemData(index)).strip()
            for index in range(1, self.profileCombo.count())
        ]

        self.set_profiles(
            profile_names=profile_names,
            selected_profile=selected_profile,
        )