from pathlib import Path

from PySide6.QtCore import QSettings


class SettingsService:
    """Store and retrieve Scriptalator application preferences."""

    ORGANIZATION_NAME = "JohanDehlen"
    APPLICATION_NAME = "Scriptalator"
    PREVIOUS_APPLICATION_NAME = "Voiceanator"

    VOICE_KEY = "narration/last_voice"
    LANGUAGE_KEY = "narration/last_language"
    SPEED_KEY = "narration/speed"
    PITCH_KEY = "narration/pitch"
    VOLUME_KEY = "narration/volume"
    FAVORITE_VOICES_KEY = "narration/favorite_voices"
    LAST_PROFILE_KEY = "narration/last_profile"
    RECENT_PROJECTS_KEY = "projects/recent"
    OUTPUT_FOLDER_KEY = "output/last_folder"

    LEGACY_OUTPUT_FILENAME_KEY = "output/last_filename"
    MIGRATION_COMPLETE_KEY = (
        "application/voiceanator_settings_migrated"
    )

    DEFAULT_LANGUAGE = ""
    DEFAULT_VOICE = ""
    DEFAULT_SPEED = 0
    DEFAULT_PITCH = 0
    DEFAULT_VOLUME = 100
    DEFAULT_PROFILE = ""
    MAX_RECENT_PROJECTS = 10

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root)

        self.settings = QSettings(
            self.ORGANIZATION_NAME,
            self.APPLICATION_NAME,
        )

        self._migrate_previous_settings()
        self._remove_legacy_filename_setting()

    def get_language(self) -> str:
        """Return the last selected language code."""

        return self.settings.value(
            self.LANGUAGE_KEY,
            self.DEFAULT_LANGUAGE,
            type=str,
        ).strip()

    def set_language(self, language: str) -> None:
        """Store the selected language code."""

        self.settings.setValue(
            self.LANGUAGE_KEY,
            language.strip(),
        )
        self.settings.sync()

    def get_voice(self) -> str:
        """Return the last selected Microsoft voice ID."""

        return self.settings.value(
            self.VOICE_KEY,
            self.DEFAULT_VOICE,
            type=str,
        ).strip()

    def set_voice(self, voice: str) -> None:
        """Store the selected Microsoft voice ID."""

        normalized_voice = voice.strip()

        if not normalized_voice:
            return

        self.settings.setValue(
            self.VOICE_KEY,
            normalized_voice,
        )
        self.settings.sync()

    def get_last_profile(self) -> str:
        """Return the last selected narration profile name."""

        return self.settings.value(
            self.LAST_PROFILE_KEY,
            self.DEFAULT_PROFILE,
            type=str,
        ).strip()

    def set_last_profile(self, profile_name: str) -> None:
        """Store the last selected narration profile name."""

        self.settings.setValue(
            self.LAST_PROFILE_KEY,
            profile_name.strip(),
        )
        self.settings.sync()

    def clear_last_profile(self) -> None:
        """Clear the saved last-profile selection."""

        self.settings.remove(self.LAST_PROFILE_KEY)
        self.settings.sync()

    def get_recent_projects(self) -> list[Path]:
        """Return existing recent project files, newest first."""

        saved_value = self.settings.value(
            self.RECENT_PROJECTS_KEY,
            [],
        )

        if isinstance(saved_value, str):
            saved_paths = [saved_value]
        elif isinstance(saved_value, (list, tuple)):
            saved_paths = list(saved_value)
        else:
            saved_paths = []

        recent_projects: list[Path] = []
        seen_paths: set[str] = set()

        for saved_path in saved_paths:
            path_text = str(saved_path).strip()

            if not path_text:
                continue

            project_path = Path(path_text).expanduser()
            normalized_key = str(project_path).casefold()

            if normalized_key in seen_paths:
                continue

            if not project_path.is_file():
                continue

            seen_paths.add(normalized_key)
            recent_projects.append(project_path)

            if len(recent_projects) >= self.MAX_RECENT_PROJECTS:
                break

        self.set_recent_projects(recent_projects)

        return recent_projects

    def set_recent_projects(
        self,
        project_paths: list[Path | str],
    ) -> None:
        """Store the complete recent-project list."""

        normalized_paths: list[str] = []
        seen_paths: set[str] = set()

        for project_path in project_paths:
            path_text = str(
                Path(project_path).expanduser()
            ).strip()

            if not path_text:
                continue

            normalized_key = path_text.casefold()

            if normalized_key in seen_paths:
                continue

            seen_paths.add(normalized_key)
            normalized_paths.append(path_text)

            if len(normalized_paths) >= self.MAX_RECENT_PROJECTS:
                break

        self.settings.setValue(
            self.RECENT_PROJECTS_KEY,
            normalized_paths,
        )
        self.settings.sync()

    def add_recent_project(
        self,
        project_path: Path | str,
    ) -> None:
        """Move a project to the top of the recent-project list."""

        normalized_path = Path(project_path).expanduser()

        if not normalized_path.is_file():
            return

        recent_projects = [
            path
            for path in self.get_recent_projects()
            if str(path).casefold()
            != str(normalized_path).casefold()
        ]

        recent_projects.insert(0, normalized_path)

        self.set_recent_projects(recent_projects)

    def remove_recent_project(
        self,
        project_path: Path | str,
    ) -> None:
        """Remove one project from the recent-project list."""

        normalized_key = str(
            Path(project_path).expanduser()
        ).casefold()

        recent_projects = [
            path
            for path in self.get_recent_projects()
            if str(path).casefold() != normalized_key
        ]

        self.set_recent_projects(recent_projects)

    def clear_recent_projects(self) -> None:
        """Clear all recent-project entries."""

        self.settings.remove(self.RECENT_PROJECTS_KEY)
        self.settings.sync()

    def get_favorite_voices(self) -> list[str]:
        """Return the saved favorite Microsoft voice IDs."""

        saved_value = self.settings.value(
            self.FAVORITE_VOICES_KEY,
            [],
        )

        if isinstance(saved_value, str):
            saved_voices = [saved_value]
        elif isinstance(saved_value, (list, tuple)):
            saved_voices = list(saved_value)
        else:
            saved_voices = []

        normalized_voices = {
            str(voice).strip()
            for voice in saved_voices
            if str(voice).strip()
        }

        return sorted(
            normalized_voices,
            key=str.lower,
        )

    def set_favorite_voices(
        self,
        favorite_voices: list[str],
    ) -> None:
        """Store the complete list of favorite voice IDs."""

        normalized_voices = sorted(
            {
                voice.strip()
                for voice in favorite_voices
                if isinstance(voice, str) and voice.strip()
            },
            key=str.lower,
        )

        self.settings.setValue(
            self.FAVORITE_VOICES_KEY,
            normalized_voices,
        )
        self.settings.sync()

    def is_favorite_voice(self, voice: str) -> bool:
        """Return whether a voice ID is currently a favorite."""

        normalized_voice = voice.strip()

        if not normalized_voice:
            return False

        return normalized_voice in self.get_favorite_voices()

    def add_favorite_voice(self, voice: str) -> None:
        """Add a Microsoft voice ID to favorites."""

        normalized_voice = voice.strip()

        if not normalized_voice:
            return

        favorites = set(self.get_favorite_voices())
        favorites.add(normalized_voice)

        self.set_favorite_voices(list(favorites))

    def remove_favorite_voice(self, voice: str) -> None:
        """Remove a Microsoft voice ID from favorites."""

        normalized_voice = voice.strip()

        if not normalized_voice:
            return

        favorites = set(self.get_favorite_voices())
        favorites.discard(normalized_voice)

        self.set_favorite_voices(list(favorites))

    def toggle_favorite_voice(self, voice: str) -> bool:
        """
        Toggle a voice favorite.

        Returns:
            True when the voice is a favorite after toggling.
        """

        normalized_voice = voice.strip()

        if not normalized_voice:
            return False

        if self.is_favorite_voice(normalized_voice):
            self.remove_favorite_voice(normalized_voice)
            return False

        self.add_favorite_voice(normalized_voice)
        return True

    def get_speed(self) -> int:
        """Return the saved speaking-speed adjustment."""

        return self._get_bounded_integer(
            key=self.SPEED_KEY,
            default=self.DEFAULT_SPEED,
            minimum=-100,
            maximum=100,
        )

    def set_speed(self, speed: int) -> None:
        """Store the speaking-speed adjustment."""

        self._set_bounded_integer(
            key=self.SPEED_KEY,
            value=speed,
            minimum=-100,
            maximum=100,
        )

    def get_pitch(self) -> int:
        """Return the saved pitch adjustment."""

        return self._get_bounded_integer(
            key=self.PITCH_KEY,
            default=self.DEFAULT_PITCH,
            minimum=-100,
            maximum=100,
        )

    def set_pitch(self, pitch: int) -> None:
        """Store the pitch adjustment."""

        self._set_bounded_integer(
            key=self.PITCH_KEY,
            value=pitch,
            minimum=-100,
            maximum=100,
        )

    def get_volume(self) -> int:
        """Return the saved volume level."""

        return self._get_bounded_integer(
            key=self.VOLUME_KEY,
            default=self.DEFAULT_VOLUME,
            minimum=0,
            maximum=100,
        )

    def set_volume(self, volume: int) -> None:
        """Store the volume level."""

        self._set_bounded_integer(
            key=self.VOLUME_KEY,
            value=volume,
            minimum=0,
            maximum=100,
        )

    def get_output_folder(self) -> Path:
        """Return the saved output folder."""

        default_output_folder = self.project_root / "output"

        saved_folder = self.settings.value(
            self.OUTPUT_FOLDER_KEY,
            str(default_output_folder),
            type=str,
        ).strip()

        output_folder = self._resolve_output_folder(
            saved_folder=saved_folder,
            default_output_folder=default_output_folder,
        )

        self.set_output_folder(output_folder)

        return output_folder

    def set_output_folder(
        self,
        output_folder: Path | str,
    ) -> None:
        """Store the selected output folder."""

        normalized_folder = str(
            Path(output_folder).expanduser()
        ).strip()

        if not normalized_folder:
            return

        self.settings.setValue(
            self.OUTPUT_FOLDER_KEY,
            normalized_folder,
        )
        self.settings.sync()

    def save_voice_settings(
        self,
        language: str,
        voice: str,
        speed: int,
        pitch: int,
        volume: int,
    ) -> None:
        """Store all narration preferences together."""

        self.set_language(language)
        self.set_voice(voice)
        self.set_speed(speed)
        self.set_pitch(pitch)
        self.set_volume(volume)

    def _migrate_previous_settings(self) -> None:
        """Copy relevant Voiceanator settings into Scriptalator once."""

        migration_complete = self.settings.value(
            self.MIGRATION_COMPLETE_KEY,
            False,
            type=bool,
        )

        if migration_complete:
            return

        previous_settings = QSettings(
            self.ORGANIZATION_NAME,
            self.PREVIOUS_APPLICATION_NAME,
        )

        migration_keys = (
            self.VOICE_KEY,
            self.OUTPUT_FOLDER_KEY,
        )

        for key in migration_keys:
            if self.settings.contains(key):
                continue

            if not previous_settings.contains(key):
                continue

            self.settings.setValue(
                key,
                previous_settings.value(key),
            )

        self.settings.setValue(
            self.MIGRATION_COMPLETE_KEY,
            True,
        )
        self.settings.sync()

    def _remove_legacy_filename_setting(self) -> None:
        """Remove the old saved output filename."""

        if not self.settings.contains(
            self.LEGACY_OUTPUT_FILENAME_KEY
        ):
            return

        self.settings.remove(
            self.LEGACY_OUTPUT_FILENAME_KEY
        )
        self.settings.sync()

    @staticmethod
    def _resolve_output_folder(
        saved_folder: str,
        default_output_folder: Path,
    ) -> Path:
        """Resolve the output folder after the application rename."""

        if not saved_folder:
            return default_output_folder

        saved_path = Path(saved_folder).expanduser()

        is_voiceanator_output = (
            saved_path.name.lower() == "output"
            and saved_path.parent.name.lower() == "voiceanator"
        )

        if is_voiceanator_output:
            return default_output_folder

        return saved_path

    def _get_bounded_integer(
        self,
        key: str,
        default: int,
        minimum: int,
        maximum: int,
    ) -> int:
        """Return a saved integer restricted to an accepted range."""

        value = self.settings.value(
            key,
            default,
            type=int,
        )

        if value < minimum or value > maximum:
            return default

        return value

    def _set_bounded_integer(
        self,
        key: str,
        value: int,
        minimum: int,
        maximum: int,
    ) -> None:
        """Store an integer after validating its range."""

        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                f"Setting '{key}' must be an integer."
            )

        if value < minimum or value > maximum:
            raise ValueError(
                (
                    f"Setting '{key}' must be between "
                    f"{minimum} and {maximum}."
                )
            )

        self.settings.setValue(key, value)
        self.settings.sync()