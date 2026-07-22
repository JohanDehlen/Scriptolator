from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ProfileControls(QWidget):
    """Display compact controls for user-defined narration profiles."""

    profile_selected = Signal(str)
    new_requested = Signal()
    save_requested = Signal()
    rename_requested = Signal()
    delete_requested = Signal()
    open_folder_requested = Signal()

    NO_PROFILE_TEXT = "No Profile"
    NO_PROFILE_VALUE = ""

    def __init__(self) -> None:
        super().__init__()

        self._profile_modified = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(6)

        heading = QLabel("Narration Profile")
        heading.setStyleSheet("font-weight: bold;")

        layout.addWidget(heading)

        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(6)

        self.profileCombo = QComboBox()
        self.profileCombo.addItem(
            self.NO_PROFILE_TEXT,
            self.NO_PROFILE_VALUE,
        )

        self.menuButton = QPushButton("⚙")
        self.menuButton.setFixedWidth(38)
        self.menuButton.setToolTip("Manage narration profiles")

        selection_layout.addWidget(self.profileCombo, 1)
        selection_layout.addWidget(self.menuButton)

        layout.addLayout(selection_layout)

        self.profileMenu = QMenu(self)

        self.newAction = QAction(
            "New Profile...",
            self,
        )
        self.saveAction = QAction(
            "Save Profile",
            self,
        )
        self.renameAction = QAction(
            "Rename Profile...",
            self,
        )
        self.deleteAction = QAction(
            "Delete Profile...",
            self,
        )
        self.openFolderAction = QAction(
            "Open Profiles Folder",
            self,
        )

        self.profileMenu.addAction(self.newAction)
        self.profileMenu.addAction(self.saveAction)
        self.profileMenu.addAction(self.renameAction)
        self.profileMenu.addAction(self.deleteAction)
        self.profileMenu.addSeparator()
        self.profileMenu.addAction(self.openFolderAction)

        self.menuButton.setMenu(self.profileMenu)

        self.profileCombo.currentIndexChanged.connect(
            self._profile_changed
        )
        self.newAction.triggered.connect(
            self.new_requested.emit
        )
        self.saveAction.triggered.connect(
            self.save_requested.emit
        )
        self.renameAction.triggered.connect(
            self.rename_requested.emit
        )
        self.deleteAction.triggered.connect(
            self.delete_requested.emit
        )
        self.openFolderAction.triggered.connect(
            self.open_folder_requested.emit
        )

        self._update_action_states()

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

        self._profile_modified = False
        self._refresh_current_profile_label()
        self._update_action_states()

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
            self.set_modified(False)
            return

        self.profileCombo.addItem(
            normalized_name,
            normalized_name,
        )

        self._sort_profiles()
        self.select_profile(normalized_name)
        self.set_modified(False)

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
        self.set_modified(False)

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

        self.profileCombo.setItemData(
            current_index,
            normalized_new_name,
        )

        self._sort_profiles()
        self.select_profile(normalized_new_name)
        self.set_modified(False)

    def set_modified(
        self,
        modified: bool,
    ) -> None:
        """Show whether the selected profile has unsaved changes."""

        self._profile_modified = (
            bool(modified)
            and bool(self.current_profile_name())
        )

        self._refresh_current_profile_label()
        self._update_action_states()

    def is_modified(self) -> bool:
        """Return whether the selected profile has unsaved changes."""

        return self._profile_modified

    def _profile_changed(self) -> None:
        """Report the selected profile and reset modified state."""

        self._profile_modified = False
        self._refresh_current_profile_label()
        self._update_action_states()

        self.profile_selected.emit(
            self.current_profile_name()
        )

    def _refresh_current_profile_label(self) -> None:
        """Update the selected profile label and modified marker."""

        current_index = self.profileCombo.currentIndex()

        if current_index < 0:
            return

        profile_name = self.current_profile_name()

        if not profile_name:
            self.profileCombo.setItemText(
                current_index,
                self.NO_PROFILE_TEXT,
            )
            return

        display_text = profile_name

        if self._profile_modified:
            display_text = f"{profile_name} *"

        self.profileCombo.setItemText(
            current_index,
            display_text,
        )

    def _update_action_states(self) -> None:
        """Enable actions that require a selected profile."""

        has_profile = bool(
            self.current_profile_name()
        )

        self.saveAction.setEnabled(
            has_profile and self._profile_modified
        )
        self.renameAction.setEnabled(has_profile)
        self.deleteAction.setEnabled(has_profile)

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